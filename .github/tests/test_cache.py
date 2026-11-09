from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from cache import remove_workspace_output


class PublicCache(unittest.TestCase):

    def test_workspace_build_output_is_removed_while_dependencies_survive(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'app').mkdir()
            (root / 'Cargo.toml').write_text('[workspace]\nmembers = ["app"]\n')
            (root / 'app/Cargo.toml').write_text('[package]\nname = "private-app"\n')
            outputs = (
                'release/deps/libprivate_app-123.rlib',
                'release/.fingerprint/private-app-123/output',
                'release/build/private-app-123/out/private-media.png',
                'release/incremental/compiler/private-source.o',
                'debug/deps/libtemporal_rs-123.rlib',
            )

            for name in (*outputs, 'release/deps/libpublic_dependency-123.rlib'):
                path = root / 'target' / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'compiled data')

            remove_workspace_output(root)

            for name in outputs:
                self.assertFalse((root / 'target' / name).exists(), name)

            self.assertTrue((root / 'target/release/deps/libpublic_dependency-123.rlib').is_file())


if __name__ == '__main__':
    unittest.main()
