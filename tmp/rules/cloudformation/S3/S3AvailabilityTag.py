from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from Common import verified_tag

class S3AvailabilityTag(BaseResourceCheck):
    def __init__(self):
        name = "Ensure S3 has availability tag"
        id = "CKV_AWS_228"
        supported_resources = ['AWS::S3::Bucket']
        categories = [CheckCategories.APPLICATION_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'Properties' in conf.keys():
            if 'Tags' in conf['Properties'].keys():
                if isinstance(conf['Properties']['Tags'], list):
                    for item in conf['Properties']['Tags']:
                        if 'Key' in item.keys() and 'Value' in item.keys():
                            if item['Key'] in verified_tag("clasificacion-disponibilidad") and str(item['Value']) in ["sin-impacto","impacto-tolerable","impacto-moderado","impacto-critico","sin impacto","impacto tolerable","impacto moderado","impacto critico"]:
                                return CheckResult.PASSED
        return CheckResult.FAILED

check = S3AvailabilityTag()