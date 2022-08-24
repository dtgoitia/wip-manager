## Set up

Developed and tested with Python 3.10.6.

* Install:

  ```shell
  git clone git@github.com:dtgoitia/wip-manager.git
  cd wip-manager

  # Create and activate Python virtual environment
  python3 -m venv .venv
  . .venv/bin/activate

  make install_development_dependencies

  # (optional) install repo under ~/.local/bin
  scripts/install.sh
  # NOTE: ensure ~/.local/bin is in your PATH
  ```

* Configuration (mandatory):

  At `~/.config/wip-manager/config.json`:

  ```json
  {
    "wip_path": "~/path/to/my/wip/file.md",
    "archive_path": "~/path/to/my/archive/file.md"
  }
  ```

* Uninstall:

  ```shell
  scripts/uninstall.sh
  ```

## Usage:

* Validate WIP file:

  ```shell
  python -m src.cli.cli validate
  ```

  It fails if the parsed WIP file cannot be restored as it was after being parsed.
  If it fails, you can use the `--debug` option to get a dump to compare against the original file.

* Clean-up completed tasks:

  ```shell
  python -m src.cli.cli clean
  ```

  Move completed tasks from the WIP file (at `wip_path`) into the archive file (`archive_path`).
