import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from request import read_request, verify_source


class RequestValidation(unittest.TestCase):

    def request(self):
        return dict(repository='gridness/tianra', source='a' * 40, base='b' * 40,
                    run_number=20, run_id=42, run_attempt=1)

    def test_valid_request_preserves_private_counter(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'request.json'
            path.write_text(json.dumps(self.request()))

            self.assertEqual(read_request(path)['run_number'], 20)

    def test_untrusted_request_fields_are_rejected(self):
        for name, value in (
            ('repository', 'attacker/fork'), ('source', 'main'),
            ('base', 'x\ninjected=true'), ('run_number', True),
            ('run_number', 0), ('run_id', '42'),
        ):
            request = self.request()
            request[name] = value

            with tempfile.TemporaryDirectory() as temporary:
                path = Path(temporary) / 'request.json'
                path.write_text(json.dumps(request))

                with self.assertRaises(ValueError):
                    read_request(path)

    def test_wrong_checkout_is_rejected_before_running_source(self):
        with patch('request.subprocess.check_output', return_value='b' * 40):
            with self.assertRaisesRegex(ValueError, 'checkout differs'):
                verify_source('a' * 40)


if __name__ == '__main__':
    unittest.main()
