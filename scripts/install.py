#!/usr/bin/env python3

import stat
from pathlib import Path
from string import Template
from textwrap import dedent

CLI_NAME = "wipman"
LOCAL_BIN_PATH = Path("~/.local/bin").expanduser()
REPO_PATH = Path(__file__).parent.parent
BIN_PATH = LOCAL_BIN_PATH / CLI_NAME


class InstallationError(Exception):
    ...


def install():
    # Create ~/.local/bin directory if required
    LOCAL_BIN_PATH.mkdir(parents=True, exist_ok=True)

    venv_path = REPO_PATH / ".venv"
    if not venv_path.exists():
        raise InstallationError(f"No virtual environment found in {REPO_PATH}")

    python_bin_path = venv_path / "bin/python"
    if not python_bin_path.exists():
        raise InstallationError(
            f"Python binary not found in the venv: {python_bin_path}"
        )

    # Create executable
    executable_template = Template(
        dedent(
            """
            #!/usr/bin/env python3

            import os
            import subprocess
            import sys

            arguments = sys.argv[1:]
            repo_path = "/home/dtg/projects/wip-manager/"
            os.chdir(repo_path)

            python_bin_path = ".venv/bin/python"
            cli_module = "src.cli.cli"
            cmd = [python_bin_path, "-m", cli_module, *arguments]
            subprocess.run(cmd)
            """
        ).lstrip()
    )
    executable_content = executable_template.substitute(
        python_bin_path="/home/dtg/projects/wip-manager/.venv/bin/python",
    )
    print(f"Creating binary under {python_bin_path}")
    BIN_PATH.write_text(executable_content)

    # Assign executable permissions: https://stackoverflow.com/a/12792002
    current_permissions = BIN_PATH.stat().st_mode
    executable_permission = current_permissions | stat.S_IEXEC
    print("Assigning permissions...")
    BIN_PATH.chmod(executable_permission)

    print("Installation finished")


def main():
    should_install = True
    if BIN_PATH.exists():
        answer = input('Already installed, type "yes" to reinstall: ')
        should_install = answer == "yes"
        print("Overwriting current installation...")

    if not should_install:
        print("Installation aborted")
        exit(1)

    install()


if __name__ == "__main__":
    try:
        main()
    except InstallationError as e:
        error_message = e.args[0]
        print(error_message)
        exit(1)
