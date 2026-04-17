from pathlib import Path
import sys
import unittest
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import karma_tracker


class KarmaTrackerTests(unittest.TestCase):
    def test_get_karma_uses_api_when_available(self):
        session = Mock()
        api_response = Mock()
        api_response.json.return_value = {"id": "nkko", "karma": 878}
        api_response.raise_for_status.return_value = None
        session.get.return_value = api_response

        karma = karma_tracker.get_karma("nkko", session=session)

        self.assertEqual(karma, 878)
        self.assertEqual(session.get.call_count, 1)
        requested_url = session.get.call_args[0][0]
        self.assertIn("hacker-news.firebaseio.com", requested_url)

    def test_get_karma_falls_back_to_html_when_api_payload_is_invalid(self):
        session = Mock()

        api_response = Mock()
        api_response.json.return_value = {"id": "nkko"}
        api_response.raise_for_status.return_value = None

        html_response = Mock()
        html_response.text = """
        <html><body><table>
        <tr><td valign="top">karma:</td><td>878</td></tr>
        </table></body></html>
        """
        html_response.raise_for_status.return_value = None

        session.get.side_effect = [api_response, html_response]

        karma = karma_tracker.get_karma("nkko", session=session)

        self.assertEqual(karma, 878)
        self.assertEqual(session.get.call_count, 2)
        self.assertIn("news.ycombinator.com/user", session.get.call_args_list[1][0][0])


if __name__ == "__main__":
    unittest.main()
