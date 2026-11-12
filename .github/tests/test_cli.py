import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import cli
import tap


class CliDelivery(unittest.TestCase):
    def test_cli_baseline_is_independent_of_admin_and_players(self):
        with patch.object(cli, 'api', return_value={'workflow_runs': []}) as api:
            self.assertEqual(cli.successful_source(), '')
            self.assertIn('cli-release.yml', str(api.call_args))

        run = dict(event='workflow_dispatch', display_title='CLI ' + 'a' * 40)
        with patch.object(cli, 'api', return_value={'workflow_runs': [run]}):
            self.assertEqual(cli.successful_source(), 'a' * 40)

    def test_formula_uses_exact_verified_archive_and_monotonic_build_version(self):
        value = tap.formula('0.1.0', '12', 'a' * 64)
        self.assertIn('version "0.1.0.12"', value)
        self.assertIn('tianra-gm-v0.1.0-build.12/tianra-gm-0.1.0-build-12-macos-aarch64.tar.gz', value)
        self.assertIn('sha256 "' + 'a' * 64 + '"', value)
        self.assertNotIn('itch.io', value)
        self.assertIn('generate_completions_from_executable(bin/"tianra-gm", "completions", shells: [:bash, :zsh, :fish])', value)

    def test_formula_inputs_cannot_inject_ruby_or_another_origin(self):
        for version, build, checksum in [('1.0.0";system("x")', '1', 'a' * 64), ('1.0.0', '1\ninjected', 'a' * 64), ('1.0.0', '1', 'main')]:
            with self.assertRaises(ValueError):
                tap.formula(version, build, checksum)


if __name__ == '__main__':
    unittest.main()
