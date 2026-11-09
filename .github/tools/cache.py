"""Remove private workspace output before measuring and saving a public cache."""
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib


def remove_workspace_output(root):
    workspace = tomllib.loads((root / 'Cargo.toml').read_text())
    names = set()

    for member in workspace['workspace']['members']:
        manifest = tomllib.loads((root / member / 'Cargo.toml').read_text())
        name = manifest['package']['name']
        names.update((name, name.replace('-', '_')))

    names.update(('temporal-rs', 'temporal_rs'))
    prefixes = tuple(prefix + name + '-' for name in names for prefix in ('', 'lib'))

    # ASVS 13.3.2: public caches must not expose private code or embedded media.
    for path in sorted((root / 'target').rglob('*'), key=lambda path: len(path.parts)):
        if not path.exists():
            continue

        if path.name.startswith(prefixes) or path.name == 'incremental':
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)
            else:
                path.unlink()


if __name__ == '__main__':
    root = Path.cwd()
    remove_workspace_output(root)
    helper = root / '.github/tools/ci.py'
    subprocess.run([sys.executable, str(helper), 'prune-cache', *sys.argv[1:]], check=True)
