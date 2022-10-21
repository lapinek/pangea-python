import os
import unittest

import pangea.exceptions as pe
from pangea import PangeaConfig
from pangea.response import ResponseStatus
from pangea.services import DomainIntel, FileIntel


class TestDomainIntel(unittest.TestCase):
    def setUp(self):
        token = os.getenv("PANGEA_TEST_INTEGRATION_TOKEN")
        config_id = os.getenv("INTEL_INTEGRATION_CONFIG_TOKEN")
        domain = os.getenv("PANGEA_TEST_INTEGRATION_ENDPOINT")
        config = PangeaConfig(domain=domain, config_id=config_id)
        self.intel_domain = DomainIntel(token, config=config)

    def test_domain_lookup(self):
        response = self.intel_domain.lookup(
            domain="737updatesboeing.com", provider="domaintools", verbose=True, raw=True
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result.data.verdict, "malicious")

    def test_domain_lookup_with_bad_auth_token(self):
        token = "noarealtoken"
        config_id = os.getenv("INTEL_INTEGRATION_CONFIG_TOKEN")
        domain = os.getenv("PANGEA_TEST_INTEGRATION_ENDPOINT")
        config = PangeaConfig(domain=domain, config_id=config_id)
        badintel_domain = DomainIntel(token, config=config)

        with self.assertRaises(pe.UnauthorizedException):
            badintel_domain.lookup(domain="737updatesboeing.com", provider="domaintools")

    def test_domain_lookup_with_no_provider(self):
        with self.assertRaises(pe.PangeaAPIException):
            self.intel_domain.lookup(domain="teoghehofuuxo.su")


class TestFileIntel(unittest.TestCase):
    def setUp(self):
        token = os.getenv("PANGEA_TEST_INTEGRATION_TOKEN")
        config_id = os.getenv("INTEL_INTEGRATION_CONFIG_TOKEN")
        domain = os.getenv("PANGEA_TEST_INTEGRATION_ENDPOINT")
        config = PangeaConfig(domain=domain, config_id=config_id)
        self.intel_file = FileIntel(token, config=config)

    def test_file_lookup(self):
        response = self.intel_file.lookup(
            hash="142b638c6a60b60c7f9928da4fb85a5a8e1422a9ffdc9ee49e17e56ccca9cf6e",
            hash_type="sha256",
            provider="reversinglabs",
            verbose=True,
            raw=True,
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result.data.verdict, "malicious")

    def test_file_lookup_with_bad_auth_token(self):
        token = "noarealtoken"
        config_id = os.getenv("INTEL_INTEGRATION_CONFIG_TOKEN")
        domain = os.getenv("PANGEA_TEST_INTEGRATION_ENDPOINT")
        config = PangeaConfig(domain=domain, config_id=config_id)
        badintel_domain = FileIntel(token, config=config)

        with self.assertRaises(pe.UnauthorizedException):
            badintel_domain.lookup(
                hash="142b638c6a60b60c7f9928da4fb85a5a8e1422a9ffdc9ee49e17e56ccca9cf6e",
                hash_type="sha256",
                provider="reversinglabs",
            )

    def test_file_lookup_with_no_provider(self):
        with self.assertRaises(pe.PangeaAPIException):
            self.intel_file.lookup(
                hash="142b638c6a60b60c7f9928da4fb85a5a8e1422a9ffdc9ee49e17e56ccca9cf6e", hash_type="sha256"
            )

    def test_file_lookup_with_bad_hash(self):
        with self.assertRaises(pe.PangeaAPIException):
            self.intel_file.lookup(hash="notarealhash", hash_type="sha256", provider="reversinglabs")

    def test_file_lookup_with_no_provider(self):
        with self.assertRaises(pe.PangeaAPIException):
            self.intel_file.lookup(
                hash="142b638c6a60b60c7f9928da4fb85a5a8e1422a9ffdc9ee49e17e56ccca9cf6e",
                hash_type="notavalidhashtype",
                provider="reversinglabs",
            )