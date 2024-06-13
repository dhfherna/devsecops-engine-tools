from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from Common import verified_tag

class EBSLaunchTemplateIntegrityTag(BaseResourceCheck):
    def __init__(self):
        name = "Ensure EBS LaunchTemplate has integrity tag"
        id = "CKV_AWS_247"
        supported_resources = ['AWS::EC2::LaunchTemplate']
        categories = [CheckCategories.APPLICATION_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        flag = False
        if 'Properties' in conf.keys():
            if 'LaunchTemplateData' in conf['Properties'].keys():
                if 'BlockDeviceMappings' in conf['Properties']['LaunchTemplateData'].keys():    
                    if isinstance(conf['Properties']['LaunchTemplateData']['BlockDeviceMappings'], list):
                        for item in conf['Properties']['LaunchTemplateData']['BlockDeviceMappings']:
                            if 'Ebs' in item.keys():
                                flag = True
                if 'TagSpecifications' in conf['Properties']['LaunchTemplateData'].keys() and flag:
                    if isinstance(conf['Properties']['LaunchTemplateData']['TagSpecifications'], list):
                        for item in conf['Properties']['LaunchTemplateData']['TagSpecifications']:
                            if 'ResourceType' in item.keys() and item['ResourceType'] != 'volume':
                                return CheckResult.PASSED
                            else:
                                if 'Tags' in item.keys():
                                        for item2 in item['Tags']:
                                            if 'Key' in item2.keys() and 'Value' in item2.keys():
                                                if item2['Key'] in verified_tag("clasificacion-integridad") and item2['Value'] in ["sin impacto","impacto tolerable","impacto moderado","impacto critico"]:
                                                    return CheckResult.PASSED
                         
        if not flag:
            return CheckResult.PASSED
        else:
            return CheckResult.FAILED

check = EBSLaunchTemplateIntegrityTag()