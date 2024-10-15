# Copyright 2022 Pangea Cyber Corporation
# Author: Pangea Cyber Corporation
from __future__ import annotations

import datetime
import unittest

import pangea.exceptions as pe
import pangea.services.authn.models as m
from pangea import PangeaConfig, PangeaResponse
from pangea.services.authn.authn import AuthN
from pangea.tools import TestEnvironment, get_test_domain, get_test_token, logger_set_pangea_config
from tests.test_tools import load_test_environment

TEST_ENVIRONMENT = load_test_environment(AuthN.service_name, TestEnvironment.LIVE)

TIME = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
EMAIL_TEST = f"user.email+test{TIME}@pangea.cloud"
EMAIL_DELETE = f"user.email+delete{TIME}@pangea.cloud"
PASSWORD_OLD = "My1s+Password"
PASSWORD_NEW = "My1s+Password_new"
PROFILE_OLD = m.Profile(first_name="Name", last_name="Last")
PROFILE_NEW = m.Profile(first_name="NameUpdate")
EMAIL_INVITE_DELETE = f"user.email+invite_del{TIME}@pangea.cloud"
EMAIL_INVITE_KEEP = f"user.email+invite_keep{TIME}@pangea.cloud"
USER_ID = None  # Will be set once user is created
CB_URI = "https://someurl.com/callbacklink"

# tests that should be run in order are named with <letter><number>.
# Letter to make tests groups and number to order them inside that group


class TestAuthN(unittest.TestCase):
    def setUp(self) -> None:
        self.token = get_test_token(TEST_ENVIRONMENT)
        domain = get_test_domain(TEST_ENVIRONMENT)
        self.config = PangeaConfig(domain=domain)
        self.authn = AuthN(self.token, config=self.config, logger_name="pangea")
        logger_set_pangea_config(logger_name=self.authn.logger.name)

    def test_authn_a1_user_create_with_password(self):
        try:
            self.create_n_login(EMAIL_TEST, PASSWORD_OLD)
            self.create_n_login(EMAIL_DELETE, PASSWORD_OLD)
        except pe.PangeaAPIException as e:
            print(e)
            self.assertTrue(False)

    def test_authn_a2_user_delete(self):
        response = self.authn.user.delete(email=EMAIL_DELETE)
        self.assertEqual(response.status, "Success")
        self.assertIsNone(response.result)

    def flow_handle_password_phase(self, flow_id, password):
        return self.authn.flow.update(
            flow_id=flow_id,
            choice=m.FlowChoice.PASSWORD,
            data=m.FlowUpdateDataPassword(password=password),
        )

    def flow_handle_profile_phase(self, flow_id):
        data = m.FlowUpdateDataProfile(profile=PROFILE_OLD)
        return self.authn.flow.update(flow_id=flow_id, choice=m.FlowChoice.PROFILE, data=data)

    def flow_handle_agreements_phase(self, flow_id, response):
        for flow_choice in response.result.flow_choices:
            agreed = []
            if flow_choice.choice == m.FlowChoice.AGREEMENTS.value:
                agreements = dict(**flow_choice.data["agreements"])
                for _, v in agreements.items():
                    agreed.append(v["id"])

        data = m.FlowUpdateDataAgreements(agreed=agreed)
        return self.authn.flow.update(flow_id=flow_id, choice=m.FlowChoice.AGREEMENTS, data=data)

    def choice_is_available(self, response, choice):
        for c in response.result.flow_choices:
            if c.choice == choice:
                return True
        return False

    def create_n_login(self, email, password) -> PangeaResponse[m.FlowCompleteResult]:
        response = self.authn.flow.start(email=email, flow_types=[m.FlowType.SIGNUP, m.FlowType.SIGNIN], cb_uri=CB_URI)
        assert response.result
        flow_id = response.result.flow_id

        while response.result.flow_phase != "phase_completed":
            if self.choice_is_available(response, m.FlowChoice.PASSWORD.value):
                response = self.flow_handle_password_phase(flow_id=flow_id, password=password)
            elif self.choice_is_available(response, m.FlowChoice.PROFILE.value):
                response = self.flow_handle_profile_phase(flow_id=flow_id)
            elif self.choice_is_available(response, m.FlowChoice.AGREEMENTS.value):
                response = self.flow_handle_agreements_phase(flow_id=flow_id, response=response)
            else:
                assert response.result
                print(f"Phase {response.result.flow_choices} not handled")
                break

        return self.authn.flow.complete(flow_id=flow_id)

    def login(self, email, password):
        start_resp = self.authn.flow.start(email=email, flow_types=[m.FlowType.SIGNIN], cb_uri=CB_URI)
        self.authn.flow.update(
            flow_id=start_resp.result.flow_id,
            choice=m.FlowChoice.PASSWORD,
            data=m.FlowUpdateDataPassword(password=password),
        )
        return self.authn.flow.complete(flow_id=start_resp.result.flow_id)

    def test_authn_a3_login_n_password_change(self):
        # This could (should) fail if test_authn_a1_user_create_with_password failed
        try:
            # login
            response_login = self.login(email=EMAIL_TEST, password=PASSWORD_OLD)
            self.assertEqual(response_login.status, "Success")
            self.assertIsNotNone(response_login.result)
            self.assertIsNotNone(response_login.result.active_token)
            self.assertIsNotNone(response_login.result.refresh_token)

        except pe.PangeaAPIException as e:
            print(e)
            self.assertTrue(False)

    def test_authn_a4_user_profile(self):
        global USER_ID
        # This could (should) fail if test_authn_a1_user_create_with_password failed
        try:
            # Get profile by email. Should be empty because it was created without profile parameter
            response = self.authn.user.profile.get(email=EMAIL_TEST)
            self.assertEqual(response.status, "Success")
            self.assertIsNotNone(response.result)
            USER_ID = response.result.id
            self.assertEqual(EMAIL_TEST, response.result.email)
            self.assertEqual(PROFILE_OLD, response.result.profile)

            response = self.authn.user.profile.get(id=USER_ID)
            self.assertEqual(response.status, "Success")
            self.assertIsNotNone(response.result)
            self.assertEqual(USER_ID, response.result.id)
            self.assertEqual(EMAIL_TEST, response.result.email)
            self.assertEqual(PROFILE_OLD, response.result.profile)

            # Add one new field to profile
            response = self.authn.user.profile.update(id=USER_ID, profile=PROFILE_NEW)
            self.assertEqual(response.status, "Success")
            self.assertIsNotNone(response.result)
            self.assertEqual(USER_ID, response.result.id)
            self.assertEqual(EMAIL_TEST, response.result.email)
            final_profile: dict[str, str] = {}
            final_profile.update(PROFILE_OLD)
            final_profile.update(PROFILE_NEW)
            self.assertEqual(m.Profile(**final_profile), response.result.profile)
        except pe.PangeaAPIException as e:
            print(e)
            raise

    def test_authn_a5_user_update(self):
        response = self.authn.user.update(email=EMAIL_TEST, disabled=False)
        self.assertEqual(response.status, "Success")
        self.assertIsNotNone(response.result)
        self.assertEqual(USER_ID, response.result.id)
        self.assertEqual(EMAIL_TEST, response.result.email)
        self.assertEqual(False, response.result.disabled)

    def test_authn_b1_user_invite(self):
        # This could (should) fail if test_authn_a1_user_create_with_password failed
        response = self.authn.user.invite(
            inviter=EMAIL_TEST,
            email=EMAIL_INVITE_KEEP,
            callback=CB_URI,
            state="whatshoulditbe",
        )
        self.assertEqual(response.status, "Success")
        self.assertIsNotNone(response.result)

        response = self.authn.user.invite(
            inviter=EMAIL_TEST,
            email=EMAIL_INVITE_DELETE,
            callback=CB_URI,
            state="whatshoulditbe",
        )
        self.assertEqual(response.status, "Success")
        self.assertIsNotNone(response.result)

        # Delete invite
        response_delete = self.authn.user.invites.delete(response.result.id)
        self.assertEqual(response.status, "Success")
        self.assertIsNone(response_delete.result)

    def test_authn_b2_user_invite_list(self):
        filter = m.UserInviteListFilter()
        filter.email__contains = ["user.email"]
        response = self.authn.user.invites.list(filter=filter)
        self.assertEqual(response.status, "Success")
        self.assertIsNotNone(response.result)
        self.assertGreater(len(response.result.invites), 0)

        # Filter with dictionary
        filter = {"email__contains": ["user.email"]}
        response = self.authn.user.invites.list(filter=filter)
        self.assertEqual(response.status, "Success")
        self.assertIsNotNone(response.result)
        self.assertGreater(len(response.result.invites), 0)

    def test_authn_c1_login_n_some_validations(self):
        # This could (should) fail if test_authn_a1_user_create_with_password failed
        try:
            response_login = self.login(email=EMAIL_TEST, password=PASSWORD_OLD)
            self.assertEqual(response_login.status, "Success")
            self.assertIsNotNone(response_login.result)
            self.assertIsNotNone(response_login.result.active_token)
            self.assertIsNotNone(response_login.result.refresh_token)

            tokens = response_login.result
            # check token
            response = self.authn.client.token_endpoints.check(token=tokens.active_token.token)
            self.assertEqual(response.status, "Success")

            # refresh
            response_refresh = self.authn.client.session.refresh(
                refresh_token=tokens.refresh_token.token, user_token=tokens.active_token.token
            )
            self.assertEqual(response_refresh.status, "Success")
            tokens = response_refresh.result

            # logout
            response_logout = self.authn.client.session.logout(token=tokens.active_token.token)
            self.assertEqual(response_logout.status, "Success")

        except pe.PangeaAPIException as e:
            print(e)
            self.assertTrue(False)

    def test_authn_c2_login_n_session_invalidate(self):
        # This could (should) fail if test_authn_a1_user_create_with_password failed
        try:
            response_login = self.login(email=EMAIL_TEST, password=PASSWORD_OLD)
            self.assertEqual(response_login.status, "Success")
            self.assertIsNotNone(response_login.result)
            self.assertIsNotNone(response_login.result.active_token)
            self.assertIsNotNone(response_login.result.refresh_token)

            # list sessions
            filter = m.SessionListFilter()
            response = self.authn.session.list(filter=filter)
            self.assertEqual(response.status, "Success")
            self.assertIsNotNone(response.result)
            self.assertGreater(len(response.result.sessions), 0)
            for session in response.result.sessions:
                try:
                    self.authn.session.invalidate(session_id=session.id)
                except pe.PangeaAPIException:
                    print(f"Fail to invalidate session_id: {session.id}")
                    pass

        except pe.PangeaAPIException as e:
            print(e)
            raise

    def test_authn_c2_login_n_client_session_invalidate(self) -> None:
        # This could (should) fail if test_authn_a1_user_create_with_password failed
        try:
            response_login = self.login(email=EMAIL_TEST, password=PASSWORD_OLD)
            self.assertEqual(response_login.status, "Success")
            self.assertIsNotNone(response_login.result)
            self.assertIsNotNone(response_login.result.active_token)
            self.assertIsNotNone(response_login.result.refresh_token)
            token = response_login.result.active_token.token

            # list sessions
            response = self.authn.client.session.list(token=token, filter={})
            self.assertEqual(response.status, "Success")
            self.assertIsNotNone(response.result)
            self.assertGreater(len(response.result.sessions), 0)

            for session in response.result.sessions:
                try:
                    self.authn.client.session.invalidate(token=token, session_id=session.id)
                except pe.PangeaAPIException as e:
                    print(f"Fail to invalidate session_id[{session.id}] token[{token}]")
                    print(e)
                    pass

        except pe.PangeaAPIException as e:
            print(e)
            raise

    def test_authn_c3_login_n_logout_sessions(self) -> None:
        # This could (should) fail if test_authn_a1_user_create_with_password failed
        try:
            response_login = self.login(email=EMAIL_TEST, password=PASSWORD_OLD)
            self.assertEqual(response_login.status, "Success")
            self.assertIsNotNone(response_login.result)
            self.assertIsNotNone(response_login.result.active_token)
            self.assertIsNotNone(response_login.result.refresh_token)

            # session logout
            response_logout = self.authn.session.logout(user_id=response_login.result.active_token.id)
            self.assertEqual(response_logout.status, "Success")

            # Expire password.
            expire_response = self.authn.client.password.expire(USER_ID)
            self.assertEqual(expire_response.status, "Success")

        except pe.PangeaAPIException as e:
            print(e)
            raise

    def test_authn_z1_user_list(self) -> None:
        response = self.authn.user.list(filter={})
        self.assertEqual(response.status, "Success")
        self.assertIsNotNone(response.result)
        assert response.result
        self.assertGreaterEqual(len(response.result.users), 0)
        for user in response.result.users:
            try:
                self.authn.user.delete(email=user.email)
            except pe.PangeaAPIException:
                print(f"Fail to delete user email: {user.email}")
                pass

    def agreements_cycle(self, type: m.AgreementType):
        name = f"{type}_{TIME}"
        text = "This is agreement text"
        active = False

        # Create agreement
        response = self.authn.agreements.create(type=type, name=name, text=text, active=active)
        assert response.result
        self.assertEqual(response.result.type, str(type))
        self.assertEqual(response.result.name, name)
        self.assertEqual(response.result.text, text)
        self.assertEqual(response.result.active, active)
        id = response.result.id
        self.assertIsNotNone(id)

        # Update agreement
        new_name = f"{name}_v2"
        new_text = f"{text} v2"

        response = self.authn.agreements.update(type=type, id=id, name=new_name, text=new_text, active=active)  # type: ignore[assignment]
        assert response.result
        self.assertEqual(response.result.name, new_name)
        self.assertEqual(response.result.text, new_text)
        self.assertEqual(response.result.active, active)

        # List
        list_response = self.authn.agreements.list(filter={})
        assert list_response.result
        self.assertGreater(list_response.result.count, 0)
        self.assertGreater(len(list_response.result.agreements), 0)
        count = list_response.result.count  # save current value

        # delete
        self.authn.agreements.delete(type=type, id=id)

        # List again
        list_response = self.authn.agreements.list()
        assert list_response.result
        self.assertEqual(list_response.result.count, count - 1)

    def test_agreements_eula(self):
        self.agreements_cycle(m.AgreementType.EULA)

    def test_agreements_privacy_policy(self):
        self.agreements_cycle(m.AgreementType.PRIVACY_POLICY)
