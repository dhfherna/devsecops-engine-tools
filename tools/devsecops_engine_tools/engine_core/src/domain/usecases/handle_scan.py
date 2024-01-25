from devsecops_engine_tools.engine_sast.engine_iac.src.applications.runner_iac_scan import (
    runner_engine_iac,
)
from devsecops_engine_tools.engine_core.src.domain.model.gateway.vulnerability_management_gateway import (
    VulnerabilityManagementGateway,
)
from devsecops_engine_tools.engine_core.src.domain.model.gateway.secrets_manager_gateway import (
    SecretsManagerGateway,
)
from devsecops_engine_tools.engine_core.src.domain.model.gateway.devops_platform_gateway import (
    DevopsPlatformGateway,
)
from devsecops_engine_tools.engine_core.src.domain.model.vulnerability_management import (
    VulnerabilityManagement,
)
from devsecops_engine_tools.engine_core.src.domain.model.customs_exceptions import (
    ExceptionVulnerabilityManagement,
    ExceptionFindingsRiskAcceptance,
)
from devsecops_engine_tools.engine_sca.engine_container.src.applications.runner_container_scan import (
    runner_engine_container,
)
from devsecops_engine_tools.engine_sca.engine_dependencies.src.applications.runner_dependencies_scan import (
    runner_engine_dependencies,
)

from devsecops_engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_utilities import settings

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()

from devsecops_engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_utilities import settings

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()


MESSAGE_ENABLED = "not yet enabled"


class HandleScan:
    def __init__(
        self,
        vulnerability_management: VulnerabilityManagementGateway,
        secrets_manager_gateway: SecretsManagerGateway,
        devops_platform_gateway: DevopsPlatformGateway
    ):
        self.vulnerability_management = vulnerability_management
        self.secrets_manager_gateway = secrets_manager_gateway
        self.devops_platform_gateway = devops_platform_gateway

    def process(self, dict_args: any, config_tool: any):
        secret_tool = None
        if dict_args["use_secrets_manager"] == "true":
            secret_tool = self.secrets_manager_gateway.get_secret(config_tool)
        if "engine_iac" in dict_args["tool"]:
            findings_list, input_core = runner_engine_iac(
                dict_args,
                config_tool["ENGINE_IAC"]["TOOL"],
                secret_tool
            )
            if dict_args["use_vulnerability_management"] == "true":
                try:
                    self.vulnerability_management.send_vulnerability_management(
                        VulnerabilityManagement(
                            config_tool["ENGINE_IAC"]["TOOL"],
                            input_core,
                            dict_args,
                            secret_tool,
                            config_tool,
                            self.devops_platform_gateway.get_source_code_management_uri(),
                            self.devops_platform_gateway.get_variable("branch_name"),
                            self.devops_platform_gateway.get_base_compact_remote_config_url(
                                dict_args["remote_config_repo"]
                            ),
                            self.devops_platform_gateway.get_variable("access_token"),
                            self.devops_platform_gateway.get_variable("build_execution_id"),
                            self.devops_platform_gateway.get_variable("build_id"),
                            self.devops_platform_gateway.get_variable("branch_tag"),
                            self.devops_platform_gateway.get_variable("commit_hash"),
                            self.devops_platform_gateway.get_variable("environment"),
                        )
                    )
                except ExceptionVulnerabilityManagement as ex1:
                    logger.error(str(ex1))
                try:
                    input_core.totalized_exclusions.extend(
                        self.vulnerability_management.get_findings_risk_acceptance(
                            input_core.scope_pipeline,
                            dict_args,
                            secret_tool,
                            config_tool,
                        )
                    )
                except ExceptionFindingsRiskAcceptance as ex2:
                    logger.error(str(ex2))

            return findings_list, input_core
        elif "engine_container" in dict_args["tool"]:
            secret_sca=""
            if secret_tool is not None:
                secret_sca=secret_tool["token_prisma_cloud"]
            else:
                secret_sca=dict_args["token_engine_container"]
            findings_list, input_core =runner_engine_container(dict_args, config_tool, secret_sca)
            return findings_list, input_core
        elif "engine_dast" in dict_args["tool"]:
            print(MESSAGE_ENABLED)
        elif "engine_secret" in dict_args["tool"]:
            print(MESSAGE_ENABLED)
        elif "engine_dependencies" in dict_args["tool"]:
            secret_sca=""
            if secret_tool is not None:
                secret_sca=secret_tool["token_xray"]
            else:
                secret_sca = dict_args["token_engine_dependencies"]
            findings_list, input_core = runner_engine_dependencies(dict_args, config_tool, secret_sca)
            return findings_list, input_core
