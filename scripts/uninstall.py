#!/usr/bin/env python3

from pathlib import Path

CLI_NAME = "wipman"
LOCAL_BIN_PATH = Path("~/.local/bin").expanduser()
BIN_PATH = LOCAL_BIN_PATH / CLI_NAME


def uninstall():
    if not BIN_PATH.exists():
        print(f"{CLI_NAME} is not installed at {BIN_PATH}")
        exit()  # all good

    print(f"Deleting {BIN_PATH} ...")
    BIN_PATH.unlink()

    print("Uninstallation finished")


if __name__ == "__main__":
    uninstall()
