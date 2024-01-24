from abc import ABCMeta, abstractmethod


class ToolGateway(metaclass=ABCMeta):
    @abstractmethod
    def run_tool_dependencies_sca(self, remote_config, get_variable, token) -> str:
        "run tool dependencies sca"
