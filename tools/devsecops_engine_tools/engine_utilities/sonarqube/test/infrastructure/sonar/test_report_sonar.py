import unittest
from unittest.mock import patch, mock_open, MagicMock
from devsecops_engine_tools.engine_utilities.sonarqube.src.infrastructure.driven_adapters.sonarqube.sonarqube_report import SonarAdapter

class TestSonarAdapter(unittest.TestCase):

    @patch(
        "os.getenv"
    )
    def test_get_project_keys_from_env(self, mock_getenv):
        # Arrange
        adapter = SonarAdapter()
        mock_getenv.return_value = '{"sonar.scanner.metadataFilePath":"path/to/metadata.json"}'
        
        with patch.object(adapter, 'parse_project_key', return_value="project_key_123") as mock_parse:
            # Act
            project_keys = adapter.get_project_keys("pipeline_name")

            # Assert
            mock_parse.assert_called_once_with("path/to/metadata.json")
            self.assertEqual(project_keys, ["project_key_123"])

    @patch(
        "os.getenv"
    )
    def test_get_project_keys_no_match_in_env(self, mock_getenv):
        # Arrange
        adapter = SonarAdapter()
        mock_getenv.return_value = ""
        
        # Act
        project_keys = adapter.get_project_keys("pipeline_name")

        # Assert
        self.assertEqual(project_keys, ["pipeline_name"])

    @patch(
        "os.getenv"
    )
    def test_get_project_keys_no_project_key_found(self, mock_getenv):
        # Arrange
        adapter = SonarAdapter()
        mock_getenv.return_value = '{"sonar.scanner.metadataFilePath":"path/to/metadata.json"}'
        
        with patch.object(adapter, "parse_project_key", return_value=None) as mock_parse:
            # Act
            project_keys = adapter.get_project_keys("pipeline_name")

            # Assert
            mock_parse.assert_called_once_with("path/to/metadata.json")
            self.assertEqual(project_keys, ["pipeline_name"])

    @patch(
        "builtins.open", 
        new_callable=mock_open,
        read_data="projectKey=my_project_key"
    )
    def test_parse_project_key_success(self, mock_file):
        # Arrange
        adapter = SonarAdapter()
        
        # Act
        result = adapter.parse_project_key("path/to/metadata.json")

        # Assert
        mock_file.assert_called_once_with("path/to/metadata.json", "r", encoding="utf-8")
        self.assertEqual(result, "my_project_key")

    def test_parse_project_key_invalid_content(self):
        # Arrange
        adapter = SonarAdapter()

        # Act
        result = adapter.parse_project_key("path/to/metadata.json")

        # Assert
        self.assertIsNone(result)

    @patch(
        "builtins.open", 
        side_effect=Exception("File not found")
    )
    def test_parse_project_key_file_not_found(self, mock_file):
        # Arrange
        adapter = SonarAdapter()

        # Act
        result = adapter.parse_project_key("path/to/nonexistent_file.json")

        # Assert
        mock_file.assert_called_once_with("path/to/nonexistent_file.json", "r", encoding="utf-8")
        self.assertIsNone(result)

    def test_create_task_report_from_string(self):
        # Arrange
        adapter = SonarAdapter()
        file_content = "projectKey=my_project_key\nanotherSetting=some_value"
        
        # Act
        result = adapter.create_task_report_from_string(file_content)

        # Assert
        self.assertEqual(result["projectKey"], "my_project_key")
        self.assertEqual(result["anotherSetting"], "some_value")

    @patch(
        "requests.post"
    )
    @patch(
        "devsecops_engine_tools.engine_utilities.sonarqube.src.infrastructure.driven_adapters.sonarqube.sonarqube_report.Utils.encode_token_to_base64"
    ) 
    def test_change_finding_status(self, mock_encode, mock_post):
        # Arrange
        mock_encode.return_value = "encoded_token"
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        sonar_adapter = SonarAdapter()
        sonar_url = "https://sonar.example.com"
        sonar_token = "my_token"
        endpoint = "/api/issues/do_transition"
        data = {
            "issue": "123",
            "transition": "reopen"
        }

        # Act
        sonar_adapter.change_finding_status(
            sonar_url, 
            sonar_token, 
            endpoint,
            data,
            "issue"
        )

        # Assert
        mock_post.assert_called_once_with(
            f"{sonar_url}{endpoint}",
            headers={"Authorization": "Basic encoded_token"},
            data={"issue": "123", "transition": "reopen"}
        )
        mock_response.raise_for_status.assert_called_once()

    @patch(
        "requests.get"
    )
    @patch(
        "devsecops_engine_tools.engine_utilities.sonarqube.src.infrastructure.driven_adapters.sonarqube.sonarqube_report.Utils.encode_token_to_base64"
    )
    def test_get_findings(self, mock_encode, mock_get):
        # Arrange
        mock_encode.return_value = "encoded_token"
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "issues": [{"key": "123", "type": "VULNERABILITY"}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        report_sonar = SonarAdapter()
        sonar_url = "https://sonar.example.com"
        sonar_token = "my_token"
        endpoint = "/api/issues/search"
        params = {
            "componentKeys": "my_project",
            "types": "VULNERABILITY",
            "ps": 500,
            "p": 1,
            "s": "CREATION_DATE",
            "asc": "false"
        }

        # Act
        findings = report_sonar.get_findings(
            sonar_url, 
            sonar_token, 
            endpoint,
            params,
            "issues"
        )

        # Assert
        mock_get.assert_called_once_with(
            f"{sonar_url}{endpoint}",
            headers={"Authorization": "Basic encoded_token"},
            params=params
        )
        mock_response.raise_for_status.assert_called_once()
        self.assertEqual(findings, [{"key": "123", "type": "VULNERABILITY"}])

    def test_search_finding_by_id(self):
        # Arrange
        report_sonar = SonarAdapter()
        issues = [
            {"key": "123", "type": "VULNERABILITY"},
            {"key": "456", "type": "BUG"}
        ]
        issue_id = "123"

        # Act
        result = report_sonar.search_finding_by_id(issues, issue_id)

        # Assert
        self.assertEqual(result, {"key": "123", "type": "VULNERABILITY"})

    def test_search_finding_by_id_not_found(self):
        # Arrange
        report_sonar = SonarAdapter()
        issues = [
            {"key": "456", "type": "BUG"}
        ]
        issue_id = "999"

        # Act
        result = report_sonar.search_finding_by_id(issues, issue_id)

        # Assert
        self.assertIsNone(result)