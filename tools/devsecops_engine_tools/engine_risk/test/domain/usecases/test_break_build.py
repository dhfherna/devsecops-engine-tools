from unittest.mock import MagicMock, patch
from devsecops_engine_tools.engine_risk.src.domain.usecases.break_build import (
    BreakBuild,
)
from devsecops_engine_tools.engine_core.src.domain.model.report import (
    Report,
)
from devsecops_engine_tools.engine_core.src.domain.model.exclusions import (
    Exclusions,
)


@patch(
    "devsecops_engine_tools.engine_risk.src.domain.usecases.break_build.BreakBuild._remediation_rate_control"
)
@patch(
    "devsecops_engine_tools.engine_risk.src.domain.usecases.break_build.BreakBuild._apply_exclusions"
)
@patch(
    "devsecops_engine_tools.engine_risk.src.domain.usecases.break_build.BreakBuild._tag_blacklist_control"
)
@patch(
    "devsecops_engine_tools.engine_risk.src.domain.usecases.break_build.BreakBuild._risk_score_control"
)
@patch(
    "devsecops_engine_tools.engine_risk.src.domain.usecases.break_build.BreakBuild._print_exclusions"
)
@patch(
    "devsecops_engine_tools.engine_risk.src.domain.usecases.break_build.BreakBuild._map_applied_exclusion"
)
@patch(
    "devsecops_engine_tools.engine_risk.src.domain.usecases.break_build.BreakBuild._breaker"
)
@patch("copy.deepcopy")
def test_process(
    deepcopy,
    breaker,
    map_applied_exclusion,
    print_exclusions,
    risk_score_control,
    tag_blacklist_control,
    apply_exclusions,
    remediation_rate_control,
):
    report_list = [Report(risk_score=10)]
    exclusions = [Exclusions(severity="severity", id="id", reason="reason")]
    remote_config = {"MESSAGE_INFO": "message"}
    apply_exclusions.return_value = (report_list, exclusions)

    break_build = BreakBuild(
        MagicMock(),
        MagicMock(),
        remote_config,
        [],
        [],
        [],
        [],
        {}
    )
    break_build.break_build = True
    break_build.process()

    remediation_rate_control.assert_called_once()
    apply_exclusions.assert_called_once()
    deepcopy.assert_called_once()
    tag_blacklist_control.assert_called_once()
    risk_score_control.assert_called_once()
    print_exclusions.assert_called_once()
    map_applied_exclusion.assert_called_once()
    breaker.assert_called_once()


def test_breaker_break():
    devops_platform_gateway = MagicMock()
    break_build = BreakBuild(
        devops_platform_gateway,
        MagicMock(),
        {},
        [],
        [],
        [],
        [],
        {}
    )
    break_build.break_build = True
    break_build._breaker()

    devops_platform_gateway.result_pipeline.assert_called_with("failed")


def test_breaker_not_break():
    devops_platform_gateway = MagicMock()
    break_build = BreakBuild(
        devops_platform_gateway,
        MagicMock(),
        {},
        [],
        [],
        [],
        [],
        {}
    )
    break_build.break_build = False
    break_build._breaker()

    devops_platform_gateway.result_pipeline.assert_called_with("succeeded")


def test_remediation_rate_control_greater():
    all_report = [
        Report(mitigated=True),
        Report(mitigated=False),
        Report(mitigated=False),
    ]
    remediation_rate_value = round((1 / 3) * 100, 3)
    risk_threshold = 10
    devops_platform_gateway = MagicMock()
    break_build = BreakBuild(
        devops_platform_gateway,
        MagicMock(),
        {},
        [],
        [],
        [],
        [],
        {"REMEDIATION_RATE": 10}
    )
    break_build._remediation_rate_control(all_report)

    devops_platform_gateway.message.assert_called_with(
        "succeeded",
        f"Remediation rate {remediation_rate_value}% is greater than {risk_threshold}%",
    )


def test_remediation_rate_control_close():
    all_report = [
        Report(mitigated=True),
        Report(mitigated=False),
        Report(mitigated=False),
    ]
    remediation_rate_value = round((1 / 3) * 100, 3)
    risk_threshold = 30
    devops_platform_gateway = MagicMock()
    break_build = BreakBuild(
        devops_platform_gateway,
        MagicMock(),
        {},
        [],
        [],
        [],
        [],
        {"REMEDIATION_RATE": 30},
    )
    break_build._remediation_rate_control(all_report)

    devops_platform_gateway.message.assert_called_with(
        "warning",
        f"Remediation rate {remediation_rate_value}% is close to {risk_threshold}%",
    )


def test_remediation_rate_control_less():
    all_report = [
        Report(mitigated=True),
        Report(mitigated=False),
        Report(mitigated=False),
    ]
    remediation_rate_value = round((1 / 3) * 100, 3)
    risk_threshold = 50
    devops_platform_gateway = MagicMock()
    break_build = BreakBuild(
        devops_platform_gateway,
        MagicMock(),
        {},
        [],
        [],
        [],
        [],
        {"REMEDIATION_RATE": 50},
    )
    break_build._remediation_rate_control(all_report)

    devops_platform_gateway.message.assert_called_with(
        "error",
        f"Remediation rate {remediation_rate_value}% is less than {risk_threshold}%",
    )


def test_map_applied_exclusion():
    exclusions = [
        Exclusions(
            severity="severity",
            id="id",
            where="where",
            create_date="create_date",
            expired_date="expired_date",
            reason="reason",
            vm_id="vm_id",
            vm_id_url="vm_id_url",
            service="service",
            tags=["tags"],
        )
    ]
    expected = [
        {
            "severity": "severity",
            "id": "id",
            "where": "where",
            "create_date": "create_date",
            "expired_date": "expired_date",
            "reason": "reason",
            "vm_id": "vm_id",
            "vm_id_url": "vm_id_url",
            "service": "service",
            "tags": ["tags"],
        }
    ]

    break_build = BreakBuild(
        MagicMock(),
        MagicMock(),
        {},
        [],
        [],
        [],
        [],
        {},
    )
    result = break_build._map_applied_exclusion(exclusions)

    assert result == expected


def test_apply_exclusions_vuln_id_from_tool():
    report_list = [Report(vuln_id_from_tool="id", where="all")]
    exclusions = [Exclusions(id="id", where="all")]
    break_build = BreakBuild(
        MagicMock(),
        MagicMock(),
        {},
        [],
        [],
        [],
        [],
        {},
    )
    break_build.exclusions = exclusions

    result = break_build._apply_exclusions(report_list)

    assert result == ([], exclusions)


def test_apply_exclusions_id():
    report_list = [Report(id="id", where="all")]
    exclusions = [Exclusions(id="id", where="all")]
    break_build = BreakBuild(
        MagicMock(),
        MagicMock(),
        {},
        [],
        [],
        [],
        [],
        {},
    )
    break_build.exclusions = exclusions

    result = break_build._apply_exclusions(report_list)

    assert result == ([], exclusions)


def test_tag_blacklist_control_error():
    report_list = [
        Report(
            vuln_id_from_tool="id1",
            tags=["blacklisted"],
            age=10,
            vm_id="vm_id",
            vm_id_url="vm_id_url",
        )
    ]
    remote_config = {
        "TAG_BLACKLIST": ["blacklisted"]
    }
    tag_age_threshold = 5
    mock_devops_platform_gateway = MagicMock()
    break_build = BreakBuild(
        mock_devops_platform_gateway,
        MagicMock(),
        remote_config,
        [],
        [],
        [],
        [],
        {"TAG_MAX_AGE": 5}
    )
    break_build._tag_blacklist_control(report_list)

    mock_devops_platform_gateway.message.assert_called_once_with(
        "error",
        f"Report {report_list[0].vm_id} with tag {report_list[0].tags[0]} is blacklisted and age {report_list[0].age} is above threshold {tag_age_threshold}",
    )


def test_tag_blacklist_control_warning():
    report_list = [
        Report(
            vuln_id_from_tool="id2",
            tags=["blacklisted"],
            age=3,
            vm_id="vm_id",
            vm_id_url="vm_id_url",
        )
    ]
    remote_config = {
        "TAG_BLACKLIST": ["blacklisted"]
    }
    tag_age_threshold = 5
    mock_devops_platform_gateway = MagicMock()
    break_build = BreakBuild(
        mock_devops_platform_gateway,
        MagicMock(),
        remote_config,
        [],
        [],
        [],
        [],
        {"TAG_MAX_AGE": 5}
    )
    break_build._tag_blacklist_control(report_list)

    mock_devops_platform_gateway.message.assert_called_once_with(
        "warning",
        f"Report {report_list[0].vm_id} with tag {report_list[0].tags[0]} is blacklisted but age {report_list[0].age} is below threshold {tag_age_threshold}",
    )


def test_risk_score_control_break():
    report_list = [Report(severity="high", epss_score=0, age=0, tags=["tag"])]
    remote_config = {
        "WEIGHTS": {
            "severity": {"high": 5},
            "epss_score": 1,
            "age": 1,
            "max_age": 1,
            "tags": {"tag": 1},
        },
    }
    risk_score_threshold = 4
    devops_platform_gateway = MagicMock()
    break_build = BreakBuild(
        devops_platform_gateway,
        MagicMock(),
        remote_config,
        [],
        [],
        [],
        [],
        {"RISK_SCORE": 4}
    )
    break_build._risk_score_control(report_list)

    devops_platform_gateway.message.assert_called_once_with(
        "error",
        f"There are findings with risk score greater than {risk_score_threshold}",
    )


def test_risk_score_control_not_break():
    report_list = [Report(severity="low", epss_score=0, age=0, tags=["tag"])]
    remote_config = {
        "WEIGHTS": {
            "severity": {"high": 1},
            "epss_score": 1,
            "age": 1,
            "max_age": 1,
            "tags": {"tag": 1},
        },
    }
    risk_score_threshold = 4
    devops_platform_gateway = MagicMock()
    break_build = BreakBuild(
        devops_platform_gateway,
        MagicMock(),
        remote_config,
        [],
        [],
        [],
        [],
        {"RISK_SCORE": 4}
    )
    break_build._risk_score_control(report_list)

    devops_platform_gateway.message.assert_called_once_with(
        "succeeded",
        f"There are no findings with risk score greater than {risk_score_threshold}",
    )


def test_print_exclusions():
    applied_exclusions = [
        {
            "severity": "severity",
            "id": "id",
            "where": "where",
            "create_date": "create_date",
            "expired_date": "expired_date",
            "reason": "reason",
        }
    ]
    devops_platform_gateway = MagicMock()
    break_build = BreakBuild(
        devops_platform_gateway,
        MagicMock(),
        {},
        [],
        [],
        [],
        [],
        {}
    )
    break_build._print_exclusions(applied_exclusions)

    devops_platform_gateway.message.assert_called_once_with(
        "warning",
        "Bellow are all findings that were excepted",
    )
