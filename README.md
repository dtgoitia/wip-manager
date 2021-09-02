Developed with Python 3.9.6

## Configuration

At `~/.config/wip-manager/config.json`:

```json
{
  "wip_path": "~/path/to/my/wip/file.md",
  "archive_path": "~/path/to/my/archive/file.md"
}
```

## Usage:

* Validate WIP file:

  ```bash
  python -m src.cli.cli validate
  ```

  It fails if the parsed WIP file cannot be restored as it was after being parsed.
  If it fails, you can use the `--debug` option to get a dump to compare against the original file.

* Clean-up completed tasks:

  ```bash
  python -m src.cli.cli clean
  ```

  Move completed tasks from the WIP file (at `wip_path`) into the archive file (`archive_path`).
