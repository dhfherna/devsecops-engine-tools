from devsecops_engine_tools.engine_core.src.domain.model.gateway.devops_platform_gateway import (
    DevopsPlatformGateway,
)


class HandleRemoteConfigPatterns:
    def __init__(
        self,
        tool_remote: DevopsPlatformGateway,
        dict_args,
    ):
        self.tool_remote = tool_remote
        self.dict_args = dict_args

    def get_remote_config(self, file_path):
        """
        Get remote configuration
        Return: dict: Remote configuration
        """
        return self.tool_remote.get_remote_config(
            self.dict_args["remote_config_repo"], file_path
        )

    def get_variable(self, variable):
        """
        Get variable.

        Returns:
            dict: Remote variable.
        """
        return self.tool_remote.get_variable(variable)
    
    def handle_skip_tool(self, exclusions, pipeline_name):
        """
        Handle skip tool.

        Return: bool: True -> skip tool, False -> not skip tool.
        """
        if (pipeline_name in exclusions) and (
            exclusions[pipeline_name].get("SKIP_TOOL", 0)
        ):
            return True
        else:
            return False

    def process_handle_skip_tool(self):
        """
        Process handle skip tool.

        Return: bool: True -> skip tool, False -> not skip tool.
        """
        return self.handle_skip_tool(
            self.get_remote_config("SCA/CONTAINER/Exclusions/Exclusions.json"),
            self.get_variable("release_name"),
        )