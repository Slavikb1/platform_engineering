import unittest
import requests


class TestWebsiteReachability(unittest.TestCase):
    def test_website_reachable(self):
        url = 'http://127.0.0.1:5000/'

        try:
            response = requests.get(url)
            # Checks if the status code is within the range of successful responses
            self.assertTrue(response.status_code >= 200 and response.status_code < 300)
        except requests.exceptions.RequestException as e:
            self.fail(f"Failed to reach website: {e}")


if __name__ == '__main__':
    unittest.main()
