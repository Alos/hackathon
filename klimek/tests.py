
import unittest
import os
from unittest.mock import patch
from utils import apply_changes
from github import search_github, create_pr

class TestApplyChanges(unittest.TestCase):

    def test_apply_changes(self):
        # Create a temporary file with some content
        with open("test.txt", "w") as f:
            f.write("This is a test file.")

        # Apply the changes to the file
        apply_changes("test.txt", "test", "hello")

        # Check that the changes were applied correctly
        with open("test.txt", "r") as f:
            content = f.read()
            self.assertEqual(content, "This is a hello file.")

        # Clean up the temporary file
        os.remove("test.txt")

class TestSearchGithub(unittest.TestCase):

    @patch("github.requests.get")
    def test_search_github(self, mock_get):
        # Create a mock response object
        mock_response = unittest.mock.Mock()
        mock_response.json.return_value = {
            "items": [
                {
                    "repository": {
                        "html_url": "https://github.com/test/test"
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        # Search for a known API call
        results = search_github("requests.get", "test")

        # Check that the results are not empty
        self.assertNotEqual(len(results), 0)

class TestCreatePr(unittest.TestCase):

    @patch("github.subprocess.run")
    @patch("github.requests.post")
    def test_create_pr(self, mock_post, mock_run):
        # Create a mock response object
        mock_response = unittest.mock.Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Create a mock subprocess object
        mock_run.return_value = None

        # Create a pull request
        create_pr("https://github.com/test/test", "old", "new", "main", "test", "test")

        # Check that the subprocess was called correctly
        self.assertEqual(mock_run.call_count, 5)

        # Check that the post request was called correctly
        self.assertEqual(mock_post.call_count, 1)

if __name__ == "__main__":
    unittest.main()
