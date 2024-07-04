import unittest
import subprocess
import logging
from unittest.mock import MagicMock, patch, mock_open, call
from unittest import mock
from devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.kubescape.kubescape_tool import (
    KubescapeTool
)

logger = logging.getLogger()
logger.setLevel(logging.ERROR)
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)


class TestKubescapeTool(unittest.TestCase):

    def setUp(self):
        self.kubescape_tool = KubescapeTool()

    @patch("builtins.open", new_callable=mock_open)
    @patch('devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.kubescape.kubescape_tool.requests.get')
    def test_download_tool_success(self, mock_get, mock_file):

        mock_response = MagicMock()
        mock_response.content = b'Test content'
        mock_get.return_value = mock_response

        url = "http://example.com/test"
        file = "testfile.bin"

        self.kubescape_tool.download_tool(file, url)
        
        mock_get.assert_called_once_with(url, allow_redirects=True)

        mock_file().write.assert_called_once_with(b'Test content')

    @patch("devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.kubescape.kubescape_tool.subprocess.run")
    @patch("devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.kubescape.kubescape_tool.logger")
    @patch.object(KubescapeTool, "download_tool")
    def test_install_tool_aleady_installed(self, mock_download_tool, mock_logger, mock_subprocess_run):
        mock_installed = MagicMock()
        mock_installed.returncode = 0
        mock_subprocess_run.return_value = mock_installed

        file = "testfile"
        url = "http://example.com/test"
        tool = self.kubescape_tool
        tool.install_tool(file, url)

        mock_subprocess_run.assert_called_once_with(
            ["which", f"./{file}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        mock_download_tool.assert_not_called()

        mock_logger.error.assert_not_called()

    @patch("devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.kubescape.kubescape_tool.subprocess.run")
    @patch("devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.kubescape.kubescape_tool.logger")
    @patch.object(KubescapeTool, "download_tool")
    def test_install_tool_not_installed(self, mock_download_tool, mock_logger, mock_subprocess_run):
        mock_installed = MagicMock()
        mock_installed.returncode = 1
        mock_subprocess_run.side_effect = [mock_installed, MagicMock()]

        file = "testfile"
        url = "http://example.com/test"
        tool = self.kubescape_tool
        tool.install_tool(file, url)

        self.assertEqual(mock_subprocess_run.call_count, 2)
        mock_subprocess_run.assert_any_call(
            ["which", f"./{file}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        mock_subprocess_run.assert_any_call(["chmod", "+x", f"./{file}"])

        mock_download_tool.assert_called_once_with(file, url)

        mock_logger.error.assert_not_called()

    @patch("devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.kubescape.kubescape_tool.subprocess.run")
    @patch("devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.kubescape.kubescape_tool.logger")
    @patch.object(KubescapeTool, "download_tool")
    def test_install_tool_exception(self, mock_download_tool, mock_logger, mock_subprocess_run):
        mock_installed = MagicMock()
        mock_installed.returncode = 1
        mock_subprocess_run.side_effect = [mock_installed, MagicMock()]

        mock_download_tool.side_effect = Exception("Test exception")

        file = "testfile"
        url = "http://example.com/test"
        tool = self.kubescape_tool
        tool.install_tool(file, url)

        mock_subprocess_run.assert_called_once_with(
            ["which", f"./{file}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        mock_download_tool.assert_called_once_with(file, url)

        mock_logger.error.assert_called_once_with("Error installing Kubescape: Test exception")

    @patch("devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.kubescape.kubescape_tool.subprocess.run")
    @patch("devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.kubescape.kubescape_tool.logger")
    @patch.object(KubescapeTool, "download_tool")
    def test_install_tool_windows_already_installed(self, mock_download_tool, mock_logger, mock_subprocess_run):
        mock_installed = MagicMock()
        mock_subprocess_run.return_value = mock_installed

        file = "testfile"
        url = "http://example.com/test"
        tool = self.kubescape_tool
        tool.install_tool_windows(file, url)

        mock_subprocess_run.assert_called_once_with(
            [f"./{file}", "version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        mock_download_tool.assert_not_called()

        mock_logger.error.assert_not_called()

    @patch("devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.kubescape.kubescape_tool.subprocess.run", side_effect=Exception("Test exception"))
    @patch("devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.kubescape.kubescape_tool.logger")
    @patch.object(KubescapeTool, "download_tool")
    def test_install_tool_windows_not_installed(self, mock_download_tool, mock_logger, mock_subprocess_run):
        mock_download_tool.return_value = None

        file = "testfile"
        url = "http://example.com/test"
        tool = self.kubescape_tool
        tool.install_tool_windows(file, url)

        mock_subprocess_run.assert_called_once_with(
            [f"./{file}", "version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        mock_download_tool.assert_called_once_with(file, url)

        mock_logger.error.assert_not_called()

    @patch("devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.kubescape.kubescape_tool.subprocess.run", side_effect=Exception("Test exception"))
    @patch("devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.kubescape.kubescape_tool.logger")
    @patch.object(KubescapeTool, "download_tool", side_effect=Exception("Download exception"))
    def test_install_tool_windows_download_exception(self, mock_download_tool, mock_logger, mock_subprocess_run):

        file = "testfile"
        url = "http://example.com/test"
        tool = self.kubescape_tool
        tool.install_tool_windows(file, url)

        mock_subprocess_run.assert_called_once_with(
            [f"./{file}", "version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        mock_download_tool.assert_called_once_with(file, url)

        mock_logger.error.assert_called_once_with("Error installing Kubescape: Download exception")

    @patch('devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.kubescape.kubescape_tool.time.strftime', return_value='20220101-120000')
    @patch("devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.kubescape.kubescape_tool.subprocess.run")
    @patch("devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.kubescape.kubescape_tool.logger")
    def test_execute_kubescape_success(self, mock_logger, mock_subprocess_run, mock_time_strftime):
        mock_subprocess_run.return_value = MagicMock()

        folders_to_scan = ["folder1", "folder2"]
        prefix = "kubescape"
        platform_to_scan = "k8s"
        self.kubescape_tool.execute_kubescape(folders_to_scan, prefix, platform_to_scan)

        expected_calls = [
            call(
                ["kubescape", "scan", "framework", "nsa", "folder1", "--format", "json", "--format-version", "v2", "--output", "results_kubescape_20220101-120000.json", "-v"],
                capture_output=True
            ),
            call(
                ["kubescape", "scan", "framework", "nsa", "folder2", "--format", "json", "--format-version", "v2", "--output", "results_kubescape_20220101-120000.json", "-v"],
                capture_output=True
            )
        ]
        mock_subprocess_run.assert_has_calls(expected_calls, any_order=False)

        mock_logger.error.assert_not_called()

    @patch('devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.kubescape.kubescape_tool.time.strftime', return_value='20220101-120000')
    @patch("devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.kubescape.kubescape_tool.subprocess.run", side_effect=subprocess.CalledProcessError(returncode=1, cmd="kubescape"))
    @patch("devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.kubescape.kubescape_tool.logger")
    def test_execute_kubescape_failure(self, mock_logger, mock_subprocess_run, mock_time_strftime):

        folders_to_scan = ["folder1"]
        prefix = "kubescape"
        platform_to_scan = "k8s"
        self.kubescape_tool.execute_kubescape(folders_to_scan, prefix,platform_to_scan)

        mock_subprocess_run.assert_called_once_with(
            ["kubescape", "scan", "framework", "nsa", "folder1", "--format", "json", "--format-version", "v2", "--output", "results_kubescape_20220101-120000.json", "-v"],
            capture_output=True
        )

        mock_logger.error.assert_called_once_with("Error during Kubescape execution: Command 'kubescape' returned non-zero exit status 1.")

    @patch("builtins.open", new_callable=mock.mock_open, read_data='{"key": "value"}')
    def test_load_json_success(self, mock_file):
        result = self.kubescape_tool.load_json("json_name.json")
        self.assertEqual(result, {"key": "value"})
        mock_file.assert_called_once_with("json_name.json")

    def test_run_tool_empty_folders(self):
        config_tool = MagicMock()
        folders_to_scan = []
        environment = "dev"
        platform = "eks"
        secret_tool = MagicMock()

        findings_list, file_from_tool = self.kubescape_tool.run_tool(
            config_tool, folders_to_scan, environment, platform, secret_tool
        )
        
        self.assertEqual(findings_list, [])
        self.assertEqual(file_from_tool, None)

    