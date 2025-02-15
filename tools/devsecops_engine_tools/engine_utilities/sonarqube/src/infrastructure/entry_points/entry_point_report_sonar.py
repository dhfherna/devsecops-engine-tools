from devsecops_engine_tools.engine_utilities.sonarqube.src.domain.usecases.report_sonar import (
    ReportSonar
)
from devsecops_engine_tools.engine_utilities.utils.printers import (
    Printers,
)
from devsecops_engine_tools.engine_core.src.domain.usecases.metrics_manager import (
    MetricsManager,
)
import re
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()

def init_report_sonar(vulnerability_management_gateway, secrets_manager_gateway, devops_platform_gateway, sonar_gateway, metrics_manager_gateway, args):
    config_tool = devops_platform_gateway.get_remote_config(
        args["remote_config_repo"], "/engine_core/ConfigTool.json", args["remote_config_branch"]
    )
    report_config_tool = devops_platform_gateway.get_remote_config(
        args["remote_config_repo"], "/report_sonar/ConfigTool.json"
    )
    Printers.print_logo_tool(config_tool["BANNER"])

    pipeline_name = devops_platform_gateway.get_variable("pipeline_name")
    branch = devops_platform_gateway.get_variable("branch_name")
    is_valid_pipeline = not re.match(report_config_tool["IGNORE_SEARCH_PATTERN"], pipeline_name, re.IGNORECASE)
    is_valid_branch = branch in report_config_tool["TARGET_BRANCHES"]
    is_enabled = config_tool["REPORT_SONAR"]["ENABLED"] == "true"
    
    if is_enabled and is_valid_pipeline and is_valid_branch:
        input_core = ReportSonar(
            vulnerability_management_gateway,
            secrets_manager_gateway, 
            devops_platform_gateway, 
            sonar_gateway
        ).process(args)
        
        if args["send_metrics"] == "true":
            MetricsManager(devops_platform_gateway, metrics_manager_gateway).process(
                config_tool, input_core, {"tool": "report_sonar"}, ""
            )
    else:
        if not is_enabled: message = "DevSecOps Engine Tool - {0} in maintenance...".format("report_sonar")
        else: message = "Tool skipped by DevSecOps policy"

        print(
            devops_platform_gateway.message(
                "warning", message),
        )