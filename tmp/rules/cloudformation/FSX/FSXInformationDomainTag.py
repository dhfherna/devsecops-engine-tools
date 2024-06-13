from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from Common import verified_listValues, verified_tag

class FSXInstanceInformationDomainTag(BaseResourceCheck):
    def __init__(self):
        name = "Ensure FSX Instance has information domain tag"
        id = "CKV_AWS_218"
        supported_resources = ['AWS::FSx::FileSystem']
        categories = [CheckCategories.APPLICATION_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        count=0
        if 'Properties' in conf.keys():
            if 'Tags' in conf['Properties'].keys():
                if isinstance(conf['Properties']['Tags'], list):
                    for item in conf['Properties']['Tags']:
                        if 'Key' in item.keys() and 'Value' in item.keys():
                            listValues = ["canales", "productos", "activos", "financiera", "contable", "legal", "riesgos", "seguridad", "no", "servicios", "tecnologia", "cumplimento"]
                            if item['Key'] in verified_tag("dominio-informacion") and verified_listValues(listValues, item['Value'].split("-")):
                                return CheckResult.PASSED

        return CheckResult.FAILED

check = FSXInstanceInformationDomainTag()