from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceCheck


class CloudfrontCustomOriginConfigHTTPS(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Cloudfront CustomOriginConfig has https-only"
        id = "CKV_AWS_280"
        supported_resources = ['AWS::CloudFront::Distribution']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
 
        if 'Properties' in conf.keys():
            if 'DistributionConfig' in conf['Properties'].keys():
                if 'Origins' in conf['Properties']['DistributionConfig'].keys():
                    if isinstance(conf['Properties']['DistributionConfig']['Origins'], list):
                        for item in conf['Properties']['DistributionConfig']['Origins']:
                            if 'CustomOriginConfig' in item.keys():
                                if 'OriginProtocolPolicy' in item['CustomOriginConfig']:
                                    if 'https-only' not in item['CustomOriginConfig']['OriginProtocolPolicy']:
                                        return CheckResult.FAILED
                    
        return CheckResult.PASSED    

check = CloudfrontCustomOriginConfigHTTPS()