import logging
import requests
import json
import time

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import pangea
from pangea.response import Response


logger = logging.getLogger(__name__)


class Request(object):
    def __init__(self, token: str = "", service: str = "", version: str = ""):
        self.token = token
        self.service = service
        self.version = version

        # TODO: allow overriding these
        self.retries = 3
        self.backoff = 1
        self.timeout = 5

        # number of async fetch attempts, with exponential backoff (4 -> 1 + 4 + 9 + 16  = 30 seconds of sleep)
        self.async_retries = 4

        # Async request support flag
        self._async = True

        self.request = self._init_request()

    def asyncMode(self, value: bool):
        if value:
            self._async = value
        return self._async

    def post(self, endpoint: str = "", data: dict = {}) -> Response:
        url = self._url(endpoint)

        requests_response = self.request.post(
            url, headers=self._headers(), data=json.dumps(data)
        )

        if self._async and requests_response.status_code == 202:
            response_json = requests_response.json()
            request_id = response_json.get("request_id", None)
            # raise exception if request_id is None
            pangea_response = self._handle_async(request_id)
        else:
            pangea_response = Response(requests_response)

        return pangea_response

    def get(self, endpoint: str, path: str) -> Response:
        url = self._url(f"{endpoint}/{path}")

        requests_response = self.request.get(url, headers=self._headers())

        pangea_response = Response(requests_response)

        return pangea_response

    def _handle_async(self, request_id: str) -> Response:
        retry_count = 0

        while True:
            pangea_response = self.get("request", request_id)

            if pangea_response.code == 202 and retry_count < self.async_retries:
                retry_count += 1
                time.sleep(retry_count * retry_count)
            else:
                return pangea_response

    def _init_request(self) -> requests.models.Request:
        retry_config = Retry(
            total=self.retries,
            backoff_factor=self.backoff,
        )

        adapter = HTTPAdapter(max_retries=retry_config)
        request = requests.Session()

        if pangea.insecure:
            request.mount("http://", adapter)
        else:
            request.mount("https://", adapter)

        return request

    def _url(self, path: str) -> str:
        protocol = "http://" if pangea.insecure else "https://"
        domain = (
            pangea.base_domain
            if pangea.environment == "local"
            else f"{self.service}.{pangea.base_domain}"
        )

        url = f"{protocol}{domain}/{ str(self.version) + '/' if self.version else '' }{path}"

        return url

    def _headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"Pangea Python v{pangea.__version__}",
            "Authorization": f"Bearer {self.token}",
        }

        return headers
