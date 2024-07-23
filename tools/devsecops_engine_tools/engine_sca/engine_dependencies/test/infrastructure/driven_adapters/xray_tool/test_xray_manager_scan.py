from devsecops_engine_tools.engine_sca.engine_dependencies.src.infrastructure.driven_adapters.xray_tool.xray_manager_scan import (
    XrayScan,
)

import pytest
from unittest.mock import patch, Mock

import subprocess


@pytest.fixture
def xray_scan_instance():
    return XrayScan()

def test_install_tool_linux_success(xray_scan_instance):
    version = "2.52.8"
    with patch("subprocess.run") as mock_subprocess, patch(
        "requests.get"
    ) as mock_requests:
        mock_subprocess.return_value.returncode = 1
        mock_requests.return_value.content = b"fake_binary_data"
        xray_scan_instance.install_tool_linux(version)

        mock_subprocess.assert_called_with(
            ["chmod", "+x", "./jf"], check=True, stdout=-1, stderr=-1
        )
        mock_requests.assert_called_with(
            f"https://releases.jfrog.io/artifactory/jfrog-cli/v2-jf/{version}/jfrog-cli-linux-amd64/jf",
            allow_redirects=True,
        )


def test_install_tool_linux_failure(xray_scan_instance):
    version = "2.52.8"
    with patch("subprocess.run") as mock_subprocess, patch(
        "requests.get"
    ) as mock_requests, patch(
        "devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.driven_adapters.prisma_cloud.prisma_cloud_manager_scan.logger.error"
    ) as mock_logger_error:
        mock_subprocess.side_effect = [
            Mock(returncode=1),
            subprocess.CalledProcessError(returncode=1, cmd="chmod"),
        ]
        mock_requests.return_value.content = b"fake_binary_data"
        xray_scan_instance.install_tool_linux(version)
        mock_logger_error.assert_called_with(
            "Error during Jfrog Cli installation on Linux: Command 'chmod' returned non-zero exit status 1."
        )


def test_install_tool_windows_success(xray_scan_instance):
    version = "2.52.8"

    with patch("subprocess.run") as mock_subprocess, patch(
        "requests.get"
    ) as mock_requests:
        mock_subprocess.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="chmod"
        )
        mock_requests.return_value.content = b"fake_binary_data"
        xray_scan_instance.install_tool_windows(version)

        mock_requests.assert_called_with(
            f"https://releases.jfrog.io/artifactory/jfrog-cli/v2-jf/{version}/jfrog-cli-windows-amd64/jf.exe",
            allow_redirects=True,
        )


def test_install_tool_windows_failure(xray_scan_instance):
    version = "2.52.8"
    with patch("subprocess.run") as mock_subprocess, patch(
        "requests.get"
    ) as mock_requests, patch(
        "devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.driven_adapters.prisma_cloud.prisma_cloud_manager_scan.logger.error"
    ) as mock_logger_error:
        mock_subprocess.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="chmod"
        )
        mock_requests.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="chmod"
        )
        xray_scan_instance.install_tool_windows(version)

        mock_logger_error.assert_called_with(
            "Error while Jfrog Cli installation on Windows: Command 'chmod' returned non-zero exit status 1."
        )


def test_install_tool_darwin_success(xray_scan_instance):
    version = "2.52.8"
    with patch("subprocess.run") as mock_subprocess, patch(
        "requests.get"
    ) as mock_requests:
        mock_subprocess.return_value.returncode = 1
        mock_requests.return_value.content = b"fake_binary_data"
        xray_scan_instance.install_tool_darwin(version)

        mock_subprocess.assert_called_with(
            ["chmod", "+x", "./jf"], check=True, stdout=-1, stderr=-1
        )
        mock_requests.assert_called_with(
            f"https://releases.jfrog.io/artifactory/jfrog-cli/v2-jf/{version}/jfrog-cli-mac-386/jf",
            allow_redirects=True,
        )


def test_install_tool_darwin_failure(xray_scan_instance):
    version = "2.52.8"
    with patch("subprocess.run") as mock_subprocess, patch(
        "requests.get"
    ) as mock_requests, patch(
        "devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.driven_adapters.prisma_cloud.prisma_cloud_manager_scan.logger.error"
    ) as mock_logger_error:
        mock_subprocess.side_effect = [
            Mock(returncode=1),
            subprocess.CalledProcessError(returncode=1, cmd="chmod"),
        ]
        mock_requests.return_value.content = b"fake_binary_data"
        xray_scan_instance.install_tool_darwin(version)
        mock_logger_error.assert_called_with(
            "Error during Jfrog Cli installation on Darwin: Command 'chmod' returned non-zero exit status 1."
        )


def test_config_server_success(xray_scan_instance):
    prefix = "prefix_test"
    token = "toke_test"
    with patch("subprocess.run") as mock_subprocess:
        mock_subprocess.side_effect = [
            Mock(
                returncode=0,
                stderr="15:43:29 [🔵Info] Importing server ID 'Artifactory'",
            ),
            Mock(returncode=0),
        ]
        xray_scan_instance.config_server(prefix, token)

        mock_subprocess.assert_called_with(
            [prefix, "c", "use", "Artifactory"],
            check=True,
            stdout=-1,
            stderr=-1,
            text=True,
        )


def test_config_server_failure(xray_scan_instance):
    prefix = "prefix_test"
    token = "toke_test"
    with patch("subprocess.run") as mock_subprocess, patch(
        "devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.driven_adapters.prisma_cloud.prisma_cloud_manager_scan.logger.error"
    ) as mock_logger_error:
        mock_subprocess.side_effect = [
            Mock(
                returncode=0,
                stderr="15:43:29 [🔵Info] Importing server ID 'Artifactory'",
            ),
            subprocess.CalledProcessError(returncode=1, cmd="chmod"),
        ]
        xray_scan_instance.config_server(prefix, token)

        mock_logger_error.assert_called_with(
            "Error during Xray Server configuration: Command 'chmod' returned non-zero exit status 1."
        )

def test_scan_dependencies_success(xray_scan_instance):
    with patch("subprocess.run") as mock_subprocess_run, patch(
        "json.dump"
    ) as mock_json_dump, patch("json.loads") as mock_json_loads, patch(
        "builtins.open"
    ) as mock_open, patch(
        "os.path.join"
    ) as mock_path_join, patch(
        "os.getcwd"
    ) as mock_os_getcwd:
        prefix = "jf"
        cwd = "working_dir"
        mode = "scan"
        to_scan = "target_file.tar"
        mock_subprocess_run.return_value = Mock(returncode=0)
        mock_os_getcwd.return_value = "working_dir"

        xray_scan_instance.scan_dependencies(
            prefix, cwd, mode, to_scan
        )

        mock_subprocess_run.assert_called_with(
            [
                prefix,
                "scan",
                "--format=json",
                f"{to_scan}",
            ],
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )


def test_scan_dependencies_failure(xray_scan_instance):
    with patch("subprocess.run") as mock_subprocess_run, patch(
        "devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.driven_adapters.prisma_cloud.prisma_cloud_manager_scan.logger.error"
    ) as mock_logger_error:
        prefix = "jf"
        cwd = "working_dir"
        mode = "scan"
        to_scan = "target_file.tar"
        mock_subprocess_run.return_value = Mock(returncode=1, stderr="Command 'xray scan' returned non-zero exit status 1.")

        xray_scan_instance.scan_dependencies(
            prefix, cwd, mode, to_scan
        )

        mock_logger_error.assert_called_with(
            "Error executing jf scan: Command 'xray scan' returned non-zero exit status 1."
        )


def test_run_tool_dependencies_sca_linux(xray_scan_instance):
    with patch("platform.system") as mock_system, patch(
        "os.getcwd"
    ) as mock_getcwd, patch(
        "devsecops_engine_tools.engine_sca.engine_dependencies.src.infrastructure.driven_adapters.xray_tool.xray_manager_scan.XrayScan.install_tool_linux"
    ) as mock_install_tool, patch(
        "devsecops_engine_tools.engine_sca.engine_dependencies.src.infrastructure.driven_adapters.xray_tool.xray_manager_scan.XrayScan.config_server"
    ) as mock_config_server, patch(
        "devsecops_engine_tools.engine_sca.engine_dependencies.src.infrastructure.driven_adapters.xray_tool.xray_manager_scan.XrayScan.scan_dependencies"
    ) as mock_scan_dependencies, patch(
        "devsecops_engine_tools.engine_sca.engine_dependencies.src.infrastructure.driven_adapters.xray_tool.xray_manager_scan.XrayScan.config_audit_scan"
    ) as mock_config_audit_scan:
        remote_config = {
            "XRAY": {"CLI_VERSION": "1.0"},
        }
        dict_args = {
            "xray_mode": "audit"
        }
        to_scan = "working_dir"
        token = "token123"
        mock_system.return_value = "Linux"
        mock_getcwd.return_value = "working_dir"

        xray_scan_instance.run_tool_dependencies_sca(
            remote_config,
            dict_args,
            to_scan,
            token,
        )

        mock_install_tool.assert_called_with("1.0")
        mock_config_server.assert_called_with("./jf", token)
        mock_getcwd.assert_any_call()

        mock_scan_dependencies.assert_called_with(
            "./jf",
            "working_dir",
            dict_args["xray_mode"],
            ''
        )


def test_run_tool_dependencies_sca_windows(xray_scan_instance):
    with patch("platform.system") as mock_system, patch(
        "os.getcwd"
    ) as mock_getcwd, patch(
        "devsecops_engine_tools.engine_sca.engine_dependencies.src.infrastructure.driven_adapters.xray_tool.xray_manager_scan.XrayScan.install_tool_windows"
    ) as mock_install_tool, patch(
        "devsecops_engine_tools.engine_sca.engine_dependencies.src.infrastructure.driven_adapters.xray_tool.xray_manager_scan.XrayScan.config_server"
    ) as mock_config_server, patch(
        "devsecops_engine_tools.engine_sca.engine_dependencies.src.infrastructure.driven_adapters.xray_tool.xray_manager_scan.XrayScan.scan_dependencies"
    ) as mock_scan_dependencies, patch(
        "devsecops_engine_tools.engine_sca.engine_dependencies.src.infrastructure.driven_adapters.xray_tool.xray_manager_scan.XrayScan.config_audit_scan"
    ) as mock_config_audit_scan:
        remote_config = {
            "XRAY": {"CLI_VERSION": "1.0"},
        }
        dict_args = {
            "xray_mode": "audit"
        }
        to_scan = "working_dir"
        token = "token123"
        mock_system.return_value = "Windows"
        mock_getcwd.return_value = "working_dir"

        xray_scan_instance.run_tool_dependencies_sca(
            remote_config,
            dict_args,
            to_scan,
            token,
        )

        mock_install_tool.assert_called_with("1.0")
        mock_config_server.assert_called_with("./jf.exe", token)
        mock_getcwd.assert_any_call()

        mock_scan_dependencies.assert_called_with(
            "./jf.exe",
            "working_dir",
            dict_args["xray_mode"],
            ''
        )


def test_run_tool_dependencies_sca_darwin(xray_scan_instance):
    with patch("platform.system") as mock_system, patch(
        "os.getcwd"
    ) as mock_getcwd, patch(
        "devsecops_engine_tools.engine_sca.engine_dependencies.src.infrastructure.driven_adapters.xray_tool.xray_manager_scan.XrayScan.install_tool_darwin"
    ) as mock_install_tool, patch(
        "devsecops_engine_tools.engine_sca.engine_dependencies.src.infrastructure.driven_adapters.xray_tool.xray_manager_scan.XrayScan.config_server"
    ) as mock_config_server, patch(
        "devsecops_engine_tools.engine_sca.engine_dependencies.src.infrastructure.driven_adapters.xray_tool.xray_manager_scan.XrayScan.scan_dependencies"
    ) as mock_scan_dependencies, patch(
        "devsecops_engine_tools.engine_sca.engine_dependencies.src.infrastructure.driven_adapters.xray_tool.xray_manager_scan.XrayScan.config_audit_scan"
    ) as mock_config_audit_scan:
        remote_config = {
            "XRAY": {"CLI_VERSION": "1.0"},
        }
        dict_args = {
            "xray_mode": "audit"
        }
        to_scan = "working_dir"
        token = "token123"
        mock_system.return_value = "Darwin"
        mock_getcwd.return_value = "working_dir"

        xray_scan_instance.run_tool_dependencies_sca(
            remote_config,
            dict_args,
            to_scan,
            token,
        )

        mock_install_tool.assert_called_with("1.0")
        mock_config_server.assert_called_with("./jf", token)
        mock_getcwd.assert_any_call()

        mock_scan_dependencies.assert_called_with(
            "./jf",
            "working_dir",
            dict_args["xray_mode"],
            ''
        )
