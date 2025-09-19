
import unittest
import os
from unittest.mock import patch, MagicMock
from utils import apply_changes
from github_utils import search_github, create_pr

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

    @patch("github_utils.Github")
    def test_search_github(self, mock_github):
        # Create a mock Github object
        mock_g = MagicMock()
        mock_github.return_value = mock_g

        # Create a mock search result
        mock_result = MagicMock()
        mock_result.repository.html_url = "https://github.com/test/test"
        mock_g.search_code.return_value = [mock_result]

        # Search for a known API call
        results = search_github("requests.get", "test")

        # Check that the results are not empty
        self.assertNotEqual(len(results), 0)

class TestCreatePr(unittest.TestCase):

    @patch("github_utils.Github")
    def test_create_pr(self, mock_github):
        # Create a mock Github object
        mock_g = MagicMock()
        mock_github.return_value = mock_g

        # Create a mock user
        mock_user = MagicMock()
        mock_user.login = "testuser"
        mock_g.get_user.return_value = mock_user
        
        # Create a mock repo
        mock_repo = MagicMock()
        mock_g.get_repo.return_value = mock_repo

        # Create a mock fork
        mock_fork = MagicMock()
        mock_user.create_fork.return_value = mock_fork

        # Create a mock branch
        mock_branch = MagicMock()
        mock_branch.commit.sha = "testsha"
        mock_fork.get_branch.return_value = mock_branch

        # Create a mock file
        mock_file = MagicMock()
        mock_file.type = "file"
        mock_file.decoded_content = b"old"
        mock_file.path = "test.py"
        mock_file.sha = "testsha"
        mock_fork.get_contents.return_value = [mock_file]


        # Create a pull request
        create_pr("https://github.com/test/test", "old", "new", "main", "test", "test")

        # Check that the fork was created
        mock_user.create_fork.assert_called_once_with(mock_repo)
        
        # Check that the branch was created
        mock_fork.create_git_ref.assert_called_once()

        # Check that the file was updated
        mock_fork.update_file.assert_called_once()

        # Check that the PR was created
        mock_repo.create_pull.assert_called_once()


if __name__ == "__main__":
    unittest.main()
