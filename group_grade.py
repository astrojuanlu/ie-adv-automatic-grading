import logging
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from glob import glob
from pathlib import Path

import colorlog

logger = logging.getLogger(__name__)

MINIMUM_COVERAGE = 0.9


class FailedCheckError(Exception):
    pass


def grade_team(zip_path):
    contents_dir = extract_zip(zip_path)
    library_name = install_lib(contents_dir)
    for check_func, check_name in [
        (check_import, "import"),
        (check_syntax, "syntax"),
        (check_pep8, "pep8"),
        (check_tests, "tests"),
        (check_coverage, "coverage"),
        (check_custom_tests, "custom tests"),
    ]:
        try:
            check_func(contents_dir)
        except Exception as e:
            logger.warning(f"Check '{check_name}' failed: {e}")
        else:
            logger.info(f"Check '{check_name}' succeeded")

    uninstall_lib(library_name)


def extract_zip(zip_path):
    target_dir = Path(Path(zip_path).stem)
    logger.debug(f"Extracting {zip_path} to {target_dir}")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(target_dir)

    return target_dir


def install_lib(contents_dir):
    library_name = _run_command(
        [sys.executable, "setup.py", "--name"], cwd=str(contents_dir)
    )
    _run_command(["pip", "install", "."], cwd=str(contents_dir))
    return library_name


def uninstall_lib(library_name):
    _run_command(["pip", "uninstall", library_name, "--yes"])


def check_import(_):
    _run_command([sys.executable, "-c", "from ie_pandas import DataFrame"])


def check_syntax(contents_dir):
    _run_command([sys.executable, "-m", "compileall", str(contents_dir)])


def check_pep8(contents_dir):
    _run_command(
        ["pycodestyle", "--max-line-length", "90", "src", "tests", "setup.py"],
        cwd=str(contents_dir),
    )


def check_tests(contents_dir):
    _run_command(["pytest"], cwd=str(contents_dir))


def check_coverage(contents_dir):
    # Instead of just doing
    # package_name = "ie_pandas"
    # let's try to find the package name
    # assuming there is only one directory in `src`
    package_name = list((contents_dir / "src").iterdir())[0].name

    _run_command(
        ["pytest", "--cov-report", "xml", "--cov", package_name], cwd=str(contents_dir)
    )
    tree = ET.parse(contents_dir / "coverage.xml")
    cov = float(tree.getroot().attrib["line-rate"])
    if cov < MINIMUM_COVERAGE:
        raise FailedCheckError(f"Test coverage is {cov}, less than {MINIMUM_COVERAGE}")


def check_custom_tests(_):
    _run_command(["pytest", "test_custom.py"])


def _run_command(command, *args, **kwargs):
    res = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, *args, **kwargs
    )
    logger.debug(res.stdout.decode())
    if res.returncode != 0:
        logger.error(res.stderr.decode())
        raise subprocess.CalledProcessError(res.returncode, command)

    return res.stdout.decode()


def main():
    for team_zip in glob("*.zip"):
        logger.info(f"Grading file {team_zip}")
        try:
            grade_team(team_zip)
        except Exception as e:
            logger.exception(e)


if __name__ == "__main__":
    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter("%(log_color)s%(levelname)s: %(message)s")
    )
    logger.addHandler(handler)

    if len(sys.argv) == 1:
        logger.setLevel(logging.INFO)
    elif sys.argv[1] in ("-v", "--verbose"):
        logger.setLevel(logging.DEBUG)
    else:
        print(f"Invalid arguments {sys.argv[1:]}")
        sys.exit(1)

    main()
