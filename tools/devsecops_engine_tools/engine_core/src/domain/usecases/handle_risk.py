from devsecops_engine_tools.engine_core.src.domain.model.gateway.vulnerability_management_gateway import (
    VulnerabilityManagementGateway,
)
from devsecops_engine_tools.engine_core.src.domain.model.gateway.secrets_manager_gateway import (
    SecretsManagerGateway,
)
from devsecops_engine_tools.engine_core.src.domain.model.gateway.devops_platform_gateway import (
    DevopsPlatformGateway,
)
from devsecops_engine_tools.engine_core.src.domain.model.gateway.printer_table_gateway import (
    PrinterTableGateway,
)
from devsecops_engine_tools.engine_risk.src.applications.runner_engine_risk import (
    runner_engine_risk,
)
from devsecops_engine_tools.engine_core.src.domain.model.customs_exceptions import (
    ExceptionGettingFindings,
)
from devsecops_engine_tools.engine_core.src.domain.model.input_core import (
    InputCore
)
import re

from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()


class HandleRisk:
    def __init__(
        self,
        vulnerability_management: VulnerabilityManagementGateway,
        secrets_manager_gateway: SecretsManagerGateway,
        devops_platform_gateway: DevopsPlatformGateway,
        print_table_gateway: PrinterTableGateway,
    ):
        self.vulnerability_management = vulnerability_management
        self.secrets_manager_gateway = secrets_manager_gateway
        self.devops_platform_gateway = devops_platform_gateway
        self.print_table_gateway = print_table_gateway

    def _get_all_from_vm(self, dict_args, secret_tool, remote_config, service):
        try:
            return self.vulnerability_management.get_all(
                service,
                dict_args,
                secret_tool,
                remote_config,
            )
        except ExceptionGettingFindings as e:
            logger.error(
                "Error getting finding list in handle risk: {0}".format(str(e))
            )

    def _filter_engagements(self, engagements, service, risk_config):
        filtered_engagements = []
        words = [word for word in service.split('_') if len(word) > 3]
        words += risk_config["HANDLE_SERVICE_NAME"]["ADD_WORD_TO_CHECK"]
        add_service_regex = risk_config["HANDLE_SERVICE_NAME"]["REGEX_ADD_SERVICE"]
        for engagement in engagements:
            if service.lower() in engagement.name.lower():
                filtered_engagements += [engagement.name]
            elif re.search(add_service_regex, engagement.name.lower()) and (sum(1 for word in words if word.lower() in engagement.name.lower()) >= 2):
                filtered_engagements += [engagement.name]
        return filtered_engagements

    def process(self, dict_args: any, remote_config: any):
        secret_tool = None
        if dict_args["use_secrets_manager"] == "true":
            secret_tool = self.secrets_manager_gateway.get_secret(remote_config)

        risk_config = self.devops_platform_gateway.get_remote_config(
            dict_args["remote_config_repo"], "engine_risk/ConfigTool.json"
        )

        pipeline_name = self.devops_platform_gateway.get_variable("pipeline_name")
        service = pipeline_name
        engagement_list = []

        if risk_config["HANDLE_SERVICE_NAME"]["ENABLED"].lower() == "true":
            service = next((pipeline_name.replace(ending, "") for ending in risk_config["HANDLE_SERVICE_NAME"]["ERASE_SERVICE_ENDING"] if pipeline_name.endswith(ending)), pipeline_name)
            match_service_code = re.match(risk_config["HANDLE_SERVICE_NAME"]["REGEX_SERVICE_CODE"], service)
            if match_service_code:
                engagements = self.vulnerability_management.get_active_engagements(
                    match_service_code.group(0),
                    dict_args,
                    secret_tool,
                    remote_config
                )
                engagement_list += self._filter_engagements(
                    engagements, service, risk_config
                )

        engagement_list += [service]

        match_parent = re.match(risk_config["PARENT_ANALYSIS"]["REGEX_PARENT"], service)
        if (
            risk_config["PARENT_ANALYSIS"]["ENABLED"].lower() == "true"
            and match_parent
        ):
            parent_service = match_parent.group(0)
            if parent_service not in engagement_list:
                engagement_list += [parent_service]

        engagement_list = list(set(engagement_list))
        print(f"Services to analyze: {engagement_list}")
        logger.info(f"Services to analyze: {engagement_list}")

        findings = []
        exclusions = []
        for service in engagement_list:
            findings_list, exclusions_list = self._get_all_from_vm(
                dict_args, secret_tool, remote_config, service
            )
            findings += findings_list
            exclusions += exclusions_list

        result = runner_engine_risk(
            dict_args,
            findings,
            exclusions,
            self.devops_platform_gateway,
            self.print_table_gateway,
        )
        input_core = InputCore(
            [],
            {},
            "",
            "",
            pipeline_name,
            self.devops_platform_gateway.get_variable("stage").capitalize(),
        )
        return result, input_core
