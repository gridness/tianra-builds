import base64
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import admin


class AdminSource(unittest.TestCase):

    def test_untrusted_source_is_rejected(self):
        for source in ('main', None, 'x\ninjected=true', 'a' * 41):
            with self.subTest(source=source), self.assertRaises(ValueError):
                admin.source_commit(source)

    def test_first_admin_release_has_no_baseline(self):
        with patch.object(admin, 'api', return_value=dict(workflow_runs=[])):
            self.assertEqual(admin.successful_source(), '')

    def test_manual_success_retains_selected_private_source(self):
        run = dict(event='workflow_dispatch', display_title='Admin ' + 'a' * 40)

        with patch.object(admin, 'api', return_value=dict(workflow_runs=[run])):
            self.assertEqual(admin.successful_source(), 'a' * 40)

    def test_push_success_resolves_request_at_its_historical_public_commit(self):
        run = dict(event='push', head_sha='b' * 40)
        request = dict(repository='gridness/tianra', source='a' * 40)
        content = base64.b64encode(json.dumps(request).encode()).decode()

        with patch.object(admin, 'api', side_effect=[dict(workflow_runs=[run]), dict(content=content)]) as api:
            self.assertEqual(admin.successful_source(), 'a' * 40)

        self.assertTrue(api.call_args.args[0].endswith('ref=' + 'b' * 40))

    def test_invalid_success_identity_stops_planning(self):
        for run in (
            dict(event='workflow_dispatch', display_title='Admin main'),
            dict(event='pull_request'),
        ):
            with self.subTest(run=run), patch.object(admin, 'api', return_value=dict(workflow_runs=[run])):
                with self.assertRaises(ValueError):
                    admin.successful_source()


if __name__ == '__main__':
    unittest.main()
