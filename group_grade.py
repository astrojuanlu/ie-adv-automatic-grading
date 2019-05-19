import logging
import os
import subprocess
import sys
import zipfile
from glob import glob
from pathlib import Path

import colorlog

logger = logging.getLogger(__name__)


def grade_team(zip_path):
    contents_dir = extract_zip(zip_path)
    library_name = install_lib(contents_dir)
    for check_func, check_name in [(check_import, "check_import")]:
        try:
            check_func()
        except Exception as e:
            logger.warning(f"'{check_name}' failed")
        else:
            logger.info(f"'{check_name}' successful")

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


def check_import():
    _run_command([sys.executable, "-c", "from ie_pandas import DataFrame"])


def _run_command(command, *args, **kwargs):
    res = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, *args, **kwargs
    )
    logger.debug(res.stdout.decode())
    if res.returncode != 0:
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

    logger.setLevel(logging.DEBUG)

    main()
