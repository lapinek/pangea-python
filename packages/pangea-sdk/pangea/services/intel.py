# Copyright 2022 Pangea Cyber Corporation
# Author: Pangea Cyber Corporation
from typing import Dict, List, Optional

from pangea.response import APIRequestModel, APIResponseModel, PangeaResponse, PangeaResponseResult

from .base import ServiceBase


class FileLookupRequest(APIRequestModel):
    """
    TODO: complete

    file_hash (str): Hash of the file to be looked up
    hash_type (str): Type of hash, can be "sha256", "sha" or "md5"
    provider (str, optional): Provider of the reputation information.  ("reversinglabs"). Default provider defined by the configuration.
    verbose (bool, optional): Echo back the parameters of the API in the response
    raw (bool, optional): Return additional details from the provider.
    """

    hash: str
    hash_type: str
    verbose: Optional[bool] = None
    raw: Optional[bool] = None
    provider: Optional[str] = None


class FileLookupData(APIResponseModel):
    """
    TODO: complete
    """

    category: List[str]
    score: int
    verdict: str


class FileLookupResult(PangeaResponseResult):
    """
    TODO: complete
    """

    data: FileLookupData
    parameters: Optional[Dict] = None
    raw_data: Optional[Dict] = None


class DomainLookupRequest(APIRequestModel):
    """
    TODO: complete

    domain (str): Domain address to be looked up
    provider (str, optional): Provider of the reputation information. ("domaintools"). Default provider defined by the configuration.
    verbose (bool, optional): Echo back the parameters of the API in the response
    raw (bool, optional): Return additional details from the provider.
    """

    domain: str
    verbose: Optional[bool] = None
    raw: Optional[bool] = None
    provider: Optional[str] = None


class DomainLookupData(APIResponseModel):
    """
    TODO: complete
    """

    category: List[str]
    score: int
    verdict: str


class DomainLookupResult(PangeaResponseResult):
    """
    TODO: complete
    """

    data: DomainLookupData
    parameters: Optional[Dict] = None
    raw_data: Optional[Dict] = None


class URLLookupRequest(APIRequestModel):
    """
    TODO: complete

    url (str): URL address to be looked up
    provider (str, optional): Provider of the reputation information. ("crowdstrike"). Default provider defined by the configuration.
    verbose (bool, optional): Echo back the parameters of the API in the response
    raw (bool, optional): Return additional details from the provider.
    """

    url: str
    verbose: Optional[bool] = None
    raw: Optional[bool] = None
    provider: Optional[str] = None


class URLLookupData(APIResponseModel):
    """
    TODO: complete
    """

    category: List[str]
    score: int
    verdict: str


class URLLookupOutput(PangeaResponseResult):
    """
    TODO: complete
    """

    data: URLLookupData
    parameters: Optional[Dict] = None
    raw_data: Optional[Dict] = None


class FileIntel(ServiceBase):
    """File Intel service client

    Provides methods to interact with [Pangea File Intel Service](https://pangea.cloud/docs/api/file-intel)

    The following information is needed:
        PANGEA_TOKEN - service token which can be found on the Pangea User
            Console at [https://console.pangea.cloud/project/tokens](https://console.pangea.cloud/project/tokens)

    Examples:
        import os

        # Pangea SDK
        from pangea.config import PangeaConfig
        from pangea.services import FileIntel

        PANGEA_TOKEN = os.getenv("PANGEA_INTEL_TOKEN")

        file_intel_config = PangeaConfig(domain="pangea.cloud")

        # Setup Pangea File Intel service
        file_intel = FileIntel(token=PANGEA_TOKEN, config=file_intel_config)
    """

    service_name = "file-intel"
    version = "v1"

    def lookup(
        self,
        hash: str,
        hash_type: str,
        provider: Optional[str] = None,
        verbose: Optional[bool] = None,
        raw: Optional[bool] = None,
    ) -> PangeaResponse[FileLookupResult]:
        """
        Look up a file

        Retrieve file reputation from a provider, using the file's hash.

        Args:
            input (FileLookupInput): input with file information to perform request

        Raises:
            PangeaAPIException: If an API Error happens

        Returns:
            A PangeaResponse where the sanctioned source(s) are in the
                response.result field.  Available response fields can be found in our [API documentation](https://pangea.cloud/docs/api/file-intel).

        Examples:
            response = file_intel.lookup(FileLookupInput(hash="142b638c6a60b60c7f9928da4fb85a5a8e1422a9ffdc9ee49e17e56ccca9cf6e", hash_type="sha256", provider="reversinglabs"))

            \"\"\"
            response contains:
            {
                "request_id": "prq_snooq62g4jsolhhpm4ze6pgzhmguflnl",
                "request_time": "2022-10-10T21:54:19.392Z",
                "response_time": "2022-10-10T21:54:19.933Z",
                "status": "Success",
                "summary": "Hash was found",
                "result": {
                    "data": {
                        "category": [
                            "Trojan"
                        ],
                        "score": 100,
                        "verdict": "malicious"
                    }
                }
            }
            \"\"\"
        """
        input = FileLookupRequest(hash=hash, hash_type=hash_type, verbose=verbose, raw=raw, provider=provider)
        response = self.request.post("lookup", data=input.dict(exclude_none=True))
        response.result = FileLookupResult(**response.raw_result)
        return response


class DomainIntel(ServiceBase):
    """Domain Intel service client

    Provides methods to interact with [Pangea Domain Intel Service](https://pangea.cloud/docs/api/domain-intel)

    The following information is needed:
        PANGEA_TOKEN - service token which can be found on the Pangea User
            Console at [https://console.pangea.cloud/project/tokens](https://console.pangea.cloud/project/tokens)

    Examples:
        import os

        # Pangea SDK
        from pangea.config import PangeaConfig
        from pangea.services import DomainIntel

        PANGEA_TOKEN = os.getenv("PANGEA_INTEL_TOKEN")

        domain_intel_config = PangeaConfig(domain="pangea.cloud")

        # Setup Pangea Domain Intel service
        domain_intel = DomainIntel(token=PANGEA_TOKEN, config=domain_intel_config)
    """

    service_name = "domain-intel"
    version = "v1"

    def lookup(
        self, domain: str, verbose: Optional[bool] = None, raw: Optional[bool] = None, provider: Optional[str] = None
    ) -> PangeaResponse[DomainLookupResult]:
        """
        Look up a domain

        Retrieve Domain reputation from a provider.

        Args:
            input (URLLookupInput): input with domain information to perform request

        Raises:
            PangeaAPIException: If an API Error happens

        Returns:
            A PangeaResponse where the sanctioned source(s) are in the
                response.result field.  Available response fields can be found in our [API documentation](https://pangea.cloud/docs/api/domain-intel).

        Examples:
            response = domain_intel.lookup(DomainLookupInput(domain="737updatesboeing.com", provider="domaintools"))

            \"\"\"
            response contains:
            {
                "request_id": "prq_gs5konqehibr5zflkxeqe2l2z7haeirx",
                "request_time": "2022-10-10T21:57:08.860Z",
                "response_time": "2022-10-10T21:57:09.539Z",
                "status": "Success",
                "summary": "Domain was found",
                "result": {
                    "data": {
                        "category": [
                            "sinkhole",
                            "proximity",
                            "threat_profile",
                            "threat_profile_phishing",
                            "threat_profile_malware",
                            "threat_profile_spam"
                        ],
                        "score": 100,
                        "verdict": "malicious"
                    }
                }
            }
            \"\"\"
        """
        input = DomainLookupRequest(domain=domain, verbose=verbose, provider=provider, raw=raw)
        response = self.request.post("lookup", data=input.dict(exclude_none=True))
        response.result = DomainLookupResult(**response.raw_result)
        return response


class UrlIntel(ServiceBase):
    """URL Intel service client.

    Provides methods to interact with [Pangea URL Intel Service](/docs/api/url-intel)

    The following information is needed:
        PANGEA_TOKEN - service token which can be found on the Pangea User
            Console at [https://console.pangea.cloud/project/tokens](https://console.pangea.cloud/project/tokens)
        URL_INTEL_CONFIG_ID - Configuration ID which can be found on the Pangea
            User Console at [https://console.pangea.cloud/service/url-intel](https://console.pangea.cloud/service/url-intel)

    Examples:
        import os

        # Pangea SDK
        from pangea.config import PangeaConfig
        from pangea.services import UrlIntel

        PANGEA_TOKEN = os.getenv("PANGEA_TOKEN")
        URL_INTEL_CONFIG_ID = os.getenv("URL_INTEL_CONFIG_ID")

        url_intel_config = PangeaConfig(domain="pangea.cloud",
                                        config_id=URL_INTEL_CONFIG_ID)

        # Setup Pangea URL Intel service
        url_intel = UrlIntel(token=PANGEA_TOKEN, config=url_intel_config)
    """

    service_name = "url-intel"
    version = "v1"

    def lookup(
        self, url: str, verbose: Optional[bool] = None, raw: Optional[bool] = None, provider: Optional[str] = None
    ) -> PangeaResponse[URLLookupOutput]:
        """
        Retrieve URL address reputation from a provider.

        Args:
            input (URLLookupInput): input with URL information to perform request

        Raises:
            PangeaAPIException: If an API Error happens

        Returns:
            A PangeaResponse where the sanctioned source(s) are in the
                response.result field.  Available response fields can be found in our [API documentation](/docs/api/url-intel)

        Examples:
            response = url_intel.lookup(URLLookupInput(url="http://113.235.101.11:54384", provider="crowdstrike"))

            \"\"\"
            response contains:
            {
                "request_id": "prq_5ugxruda7vmsgioup6vjvaqmnmvxzbqv",
                "request_time": "2022-08-23T03:40:03.549Z",
                "response_time": "2022-08-23T03:40:03.694Z",
                "status": "success",
                "summary": "Url was found",
                "result": {
                    "data": {
                        "category": [
                            "Not Provided"
                        ],
                        "score": 80,
                        "verdict": "malicious"
                    }
                }
            }
            \"\"\"
        """

        input = URLLookupRequest(url=url, provider=provider, verbose=verbose, raw=raw)
        response = self.request.post("lookup", data=input.dict(exclude_none=True))
        response.result = URLLookupOutput(**response.raw_result)
        return response
