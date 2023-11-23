from devsecops_engine_utilities.utils.api_error import ApiError
from devsecops_engine_utilities.defect_dojo.domain.request_objects.finding import FindingRequest
from devsecops_engine_utilities.defect_dojo.domain.models.finding import Finding, FindingList
from devsecops_engine_utilities.defect_dojo.infraestructure.driver_adapters.settings.settings import VERIFY_CERTIFICATE
from devsecops_engine_utilities.utils.session_manager import SessionManager
from devsecops_engine_utilities.settings import SETTING_LOGGER
from devsecops_engine_utilities.utils.logger_info import MyLogger
import json

logger = MyLogger.__call__(**SETTING_LOGGER).get_logger()


class FindingRestConsumer:
    def __init__(self, session: SessionManager):
        self.__token = session._token
        self.__host = session._host
        self.__session = session._instance

    def get(self, request):
        url = f"{self.__host}/api/v2/findings/"
        headers = {"Authorization": f"Token {self.__token}", "Content-Type": "application/json"}
        try:
            response = self.__session.get(url, headers=headers, data={}, params=request, verify=VERIFY_CERTIFICATE)
            if response.status_code != 200:
                raise ApiError(response.json())
            findings = FindingList.from_dict(response.json())
        except Exception as e:
            raise ApiError(e)
        return findings

    def close(self, request, id):
        url = f"{self.__host}/api/v2/findings/{id}/close/"
        headers = {"Authorization": f"Token {self.__token}", "Content-Type": "application/json"}
        try:
            response = self.__session.post(url, headers=headers, data=json.dumps(request), verify=VERIFY_CERTIFICATE)
            if response.status_code == 404:
                raise ApiError(message=f"Finding whit id {id} not found")
            if response.status_code != 200:
                raise ApiError(response.json())
            logger.debug(response)
        except Exception as e:
            logger.debug(response.json())
            logger.error(e)
            raise ApiError(e)
        return response
