from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from Common import verified_tag

class EFSAvailabilityTag(BaseResourceCheck):
    def __init__(self):
        name = "Ensure EFS has availability tag"
        id = "CKV_AWS_202"
        supported_resources = ['AWS::EFS::FileSystem']
        categories = [CheckCategories.APPLICATION_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'Properties' in conf.keys():
            if 'FileSystemTags' in conf['Properties'].keys():
                if isinstance(conf['Properties']['FileSystemTags'], list):
                    for item in conf['Properties']['FileSystemTags']:
                        if 'Key' in item.keys() and 'Value' in item.keys():
                            if item['Key'] in verified_tag("clasificacion-disponibilidad") and str(item['Value']) in ["sin-impacto","impacto-tolerable","impacto-moderado","impacto-critico","sin impacto","impacto tolerable","impacto moderado","impacto critico"]:
                                return CheckResult.PASSED
        return CheckResult.FAILED

check = EFSAvailabilityTag()