import datetime
import unittest

import pangea.services.authz as m
from pangea import PangeaConfig
from pangea.services import AuthZ
from pangea.tools import TestEnvironment, get_test_domain, get_test_token, logger_set_pangea_config
from tests.test_tools import load_test_environment

TEST_ENVIRONMENT = load_test_environment(AuthZ.service_name, TestEnvironment.LIVE)

time_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
folder1 = "folder_1_" + time_str
folder2 = "folder_2_" + time_str
user1 = "user_1_" + time_str
user2 = "user_2_" + time_str

namespace_folder = "folder"
namespace_user = "user"
relation_owner = "owner"
relation_editor = "editor"
relation_reader = "reader"


class TestAuthZIntegration(unittest.TestCase):
    def setUp(self):
        self.token = get_test_token(TEST_ENVIRONMENT)
        self.domain = get_test_domain(TEST_ENVIRONMENT)
        config = PangeaConfig(domain=self.domain, custom_user_agent="sdk-test")
        self.authz = AuthZ(self.token, config=config, logger_name="pangea")
        logger_set_pangea_config(logger_name=self.authz.logger.name)

    def test_integration(self):
        # Create tuples
        r_create = self.authz.tuple_create(
            [
                {
                    "resource": {
                        "namespace": namespace_folder,
                        "id": folder1,
                    },
                    "relation": relation_reader,
                    "subject": {
                        "namespace": namespace_user,
                        "id": user1,
                    },
                },
                {
                    "resource": {
                        "namespace": namespace_folder,
                        "id": folder1,
                    },
                    "relation": relation_editor,
                    "subject": {
                        "namespace": namespace_user,
                        "id": user2,
                    },
                },
                {
                    "resource": {
                        "namespace": namespace_folder,
                        "id": folder2,
                    },
                    "relation": relation_editor,
                    "subject": {
                        "namespace": namespace_user,
                        "id": user1,
                    },
                },
                {
                    "resource": {
                        "namespace": namespace_folder,
                        "id": folder2,
                    },
                    "relation": relation_owner,
                    "subject": {
                        "namespace": namespace_user,
                        "id": user2,
                    },
                },
            ]
        )

        self.assertIsNone(r_create.result)

        # Tuple list with resource
        r_list_with_resource = self.authz.tuple_list(
            filter=m.TupleListFilter(resource_namespace=namespace_folder, resource_id=folder1)
        )

        self.assertIsNotNone(r_list_with_resource.result)
        self.assertEqual(len(r_list_with_resource.result.tuples), 2)

        # Tuple list with subject
        r_list_with_subject = self.authz.tuple_list(
            filter=m.TupleListFilter(subject_namespace=namespace_user, subject_id=user1)
        )

        self.assertIsNotNone(r_list_with_subject.result)
        self.assertEqual(len(r_list_with_subject.result.tuples), 2)

        # Tuple delete
        r_delete = self.authz.tuple_delete(
            tuples=[
                m.Tuple(
                    resource=m.Resource(namespace=namespace_folder, id=folder1),
                    relation=relation_reader,
                    subject=m.Subject(namespace=namespace_user, id=user1),
                )
            ]
        )

        self.assertIsNone(r_delete.result)

        # Check no debug
        r_check = self.authz.check(
            resource=m.Resource(namespace=namespace_folder, id=folder1),
            action="reader",
            subject=m.Subject(namespace=namespace_user, id=user2),
        )

        self.assertIsNotNone(r_check.result)
        self.assertFalse(r_check.result.allowed)
        self.assertIsNone(r_check.result.debug)
        self.assertIsNotNone(r_check.result.schema_id)
        self.assertIsNotNone(r_check.result.schema_version)

        # Check debug
        r_check = self.authz.check(
            resource=m.Resource(namespace=namespace_folder, id=folder1),
            action="editor",
            subject=m.Subject(namespace=namespace_user, id=user2),
            debug=True,
        )

        self.assertIsNotNone(r_check.result)
        self.assertTrue(r_check.result.allowed)
        self.assertIsNotNone(r_check.result.debug)
        self.assertIsNotNone(r_check.result.schema_id)
        self.assertIsNotNone(r_check.result.schema_version)

        r_check = self.authz.check(
            resource=m.Resource(namespace=namespace_folder, id=folder1),
            action="editor",
            subject=m.Subject(namespace=namespace_user, id=user2),
            debug=True,
        )

        self.assertIsNotNone(r_check.result)
        self.assertTrue(r_check.result.allowed)
        self.assertIsNotNone(r_check.result.debug)
        self.assertIsNotNone(r_check.result.schema_id)
        self.assertIsNotNone(r_check.result.schema_version)

        # List resources
        r_list_resources = self.authz.list_resources(
            namespace=namespace_folder, action=relation_editor, subject=m.Subject(namespace=namespace_user, id=user2)
        )

        self.assertIsNotNone(r_list_resources.result)
        self.assertEqual(len(r_list_resources.result.ids), 1)

        # List subjects
        r_list_subjects = self.authz.list_subjects(
            resource=m.Resource(namespace=namespace_folder, id=folder2), action=relation_editor
        )

        self.assertIsNotNone(r_list_subjects.result)
        self.assertEqual(len(r_list_subjects.result.subjects), 1)
