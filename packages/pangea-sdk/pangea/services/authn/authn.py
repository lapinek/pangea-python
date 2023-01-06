# Copyright 2022 Pangea Cyber Corporation
# Author: Pangea Cyber Corporation

from typing import Optional

from pangea.response import PangeaResponse
from pangea.services.authn.models import (
    IDProvider,
    PasswordUpdateRequest,
    PasswordUpdateResult,
    Profile,
    Scopes,
    UserCreateRequest,
    UserCreateResult,
    UserDeleteRequest,
    UserDeleteResult,
    UserinfoRequest,
    UserinfoResult,
    UserInviteDeleteRequest,
    UserInviteDeleteResult,
    UserInviteListResult,
    UserInviteRequest,
    UserInviteResult,
    UserListRequest,
    UserListResult,
    UserLoginRequest,
    UserLoginResult,
    UserProfileGetRequest,
    UserProfileGetResult,
    UserProfileUpdateRequest,
    UserProfileUpdateResult,
    UserUpdateRequest,
    UserUpdateResult,
)
from pangea.services.base import ServiceBase

SERVICE_NAME = "authn"
VERSION = "v1"


class AuthN(ServiceBase):
    """AuthN service client.

    Provides methods to interact with the [Pangea AuthN Service](https://pangea.cloud/docs/api/authn).

    The following information is needed:
        PANGEA_TOKEN - service token which can be found on the Pangea User
            Console at [https://console.pangea.cloud/project/tokens](https://console.pangea.cloud/project/tokens)

    Examples:
        import os

        # Pangea SDK
        from pangea.config import PangeaConfig
        from pangea.services import AuthN

        PANGEA_TOKEN = os.getenv("PANGEA_AUTHN_TOKEN")
        authn_config = PangeaConfig(domain="pangea.cloud")

        # Setup Pangea AuthN service
        authn = AuthN(token=PANGEA_TOKEN, config=authn_config)
    """

    service_name: str = SERVICE_NAME
    version: str = VERSION

    def __init__(
        self,
        token,
        config=None,
    ):
        super().__init__(token, config)
        self.user = AuthN.User(token, config)
        self.password = AuthN.Password(token, config)

    # https://dev.pangea.cloud/docs/api/authn/#complete-a-login # FIXME: Update url once in prod
    def userinfo(self, code: str) -> PangeaResponse[UserinfoResult]:
        input = UserinfoRequest(code=code)

        response = self.request.post("userinfo", data=input.dict(exclude_none=True))
        if response.raw_result is not None:
            response.result = UserinfoResult(**response.raw_result)
        return response

    class Password(ServiceBase):
        service_name: str = SERVICE_NAME
        version: str = VERSION

        def __init__(
            self,
            token,
            config=None,
        ):
            super().__init__(token, config)

        #   - path: authn::/v1/password/update
        # https://dev.pangea.cloud/docs/api/authn#change-a-users-password   # FIXME: Update url once in prod
        def update(self, email: str, old_secret: str, new_secret: str) -> PangeaResponse[PasswordUpdateResult]:
            input = PasswordUpdateRequest(email=email, old_secret=old_secret, new_secret=new_secret)
            response = self.request.post("password/update", data=input.dict(exclude_none=True))
            if response.raw_result is not None:
                response.result = PasswordUpdateResult(**response.raw_result)
            return response

    class User(ServiceBase):
        service_name: str = SERVICE_NAME
        version: str = VERSION

        def __init__(
            self,
            token,
            config=None,
        ):
            super().__init__(token, config)
            self.profile = AuthN.User.Profile(token, config)
            self.invites = AuthN.User.Invites(token, config)

        #   - path: authn::/v1/user/create
        # https://dev.pangea.cloud/docs/api/authn#create-user   # FIXME: Update url once in prod
        def create(
            self,
            email: str,
            authenticator: str,
            id_provider: IDProvider,
            verified: Optional[bool] = None,
            require_mfa: Optional[bool] = None,
            profile: Optional[Profile] = None,
            scopes: Optional[Scopes] = None,
        ) -> PangeaResponse[UserCreateResult]:

            input = UserCreateRequest(
                email=email,
                authenticator=authenticator,
                id_provider=id_provider,
                verified=verified,
                require_mfa=require_mfa,
                profile=profile,
                scopes=scopes,
            )
            response = self.request.post("user/create", data=input.dict(exclude_none=True))
            if response.raw_result is not None:
                response.result = UserCreateResult(**response.raw_result)
            return response

        #   - path: authn::/v1/user/delete
        # https://dev.pangea.cloud/docs/api/authn#delete-a-user # FIXME: Update url once in prod
        def delete(self, email: str) -> PangeaResponse[UserDeleteResult]:
            input = UserDeleteRequest(email=email)
            response = self.request.post("user/delete", data=input.dict(exclude_none=True))
            if response.raw_result is not None:
                response.result = UserDeleteResult(**response.raw_result)
            return response

        # https://dev.pangea.cloud/docs/api/authn/#administration-user-update # FIXME: Update url once in prod
        def update(
            self,
            identity: Optional[str] = None,
            email: Optional[str] = None,
            authenticator: Optional[str] = None,
            disabled: Optional[bool] = None,
            require_mfa: Optional[bool] = None,
        ) -> PangeaResponse[UserUpdateResult]:
            input = UserUpdateRequest(
                identity=identity,
                email=email,
                authenticator=authenticator,
                disabled=disabled,
                require_mfa=require_mfa,
            )

            response = self.request.post("user/update", data=input.dict(exclude_none=True))
            if response.raw_result is not None:
                response.result = UserUpdateResult(**response.raw_result)
            return response

        #   - path: authn::/v1/user/invite
        # https://dev.pangea.cloud/docs/api/authn#invite-a-user # FIXME: Update url once in prod
        def invite(
            self,
            inviter: str,
            email: str,
            callback: str,
            state: str,
            invite_org: Optional[str] = None,
            require_mfa: Optional[bool] = None,
        ) -> PangeaResponse[UserInviteResult]:
            input = UserInviteRequest(
                inviter=inviter,
                email=email,
                callback=callback,
                state=state,
                invite_org=invite_org,
                require_mfa=require_mfa,
            )
            response = self.request.post("user/invite", data=input.dict(exclude_none=True))
            if response.raw_result is not None:
                response.result = UserInviteResult(**response.raw_result)
            return response

        #   - path: authn::/v1/user/list
        # https://dev.pangea.cloud/docs/api/authn#list-users # FIXME: Update url once in prod
        def list(self, scopes: Scopes, glob_scopes: Scopes) -> PangeaResponse[UserListResult]:
            input = UserListRequest(scopes=scopes, glob_scopes=glob_scopes)
            response = self.request.post("user/list", data=input.dict(exclude_none=True))
            response.result = UserListResult(**response.raw_result)
            return response

        #   - path: authn::/v1/user/login
        # https://dev.pangea.cloud/docs/api/authn#user-login # FIXME: Update url once in prod
        def login(self, email: str, secret: str, scopes: Optional[Scopes] = None) -> PangeaResponse[UserLoginResult]:
            input = UserLoginRequest(email=email, secret=secret, scopes=scopes)
            response = self.request.post("user/login", data=input.dict(exclude_none=True))
            response.result = UserLoginResult(**response.raw_result)
            return response

        class Profile(ServiceBase):
            service_name: str = SERVICE_NAME
            version: str = VERSION

            def __init__(
                self,
                token,
                config=None,
            ):
                super().__init__(token, config)

            #   - path: authn::/v1/user/profile/get
            # https://dev.pangea.cloud/docs/api/authn#get-user # FIXME: Update url once in prod
            def get(
                self, identity: Optional[str] = None, email: Optional[str] = None
            ) -> PangeaResponse[UserProfileGetResult]:
                input = UserProfileGetRequest(identity=identity, email=email)
                response = self.request.post("user/profile/get", data=input.dict(exclude_none=True))
                if response.raw_result is not None:
                    response.result = UserProfileGetResult(**response.raw_result)
                return response

            #   - path: authn::/v1/user/profile/update
            # https://dev.pangea.cloud/docs/api/authn#update-user # FIXME: Update url once in prod
            def update(
                self,
                profile: Profile,
                identity: Optional[str] = None,
                email: Optional[str] = None,
                require_mfa: Optional[bool] = None,
                mfa_value: Optional[str] = None,
                mfa_provider: Optional[str] = None,
            ) -> PangeaResponse[UserProfileUpdateResult]:
                input = UserProfileUpdateRequest(
                    identity=identity,
                    email=email,
                    profile=profile,
                    require_mfa=require_mfa,
                    mfa_value=mfa_value,
                    mfa_provider=mfa_provider,
                )
                response = self.request.post("user/profile/update", data=input.dict(exclude_none=True))
                response.result = UserProfileUpdateResult(**response.raw_result)
                return response

        class Invites(ServiceBase):
            service_name: str = SERVICE_NAME
            version: str = VERSION

            def __init__(
                self,
                token,
                config=None,
            ):
                super().__init__(token, config)

            #   - path: authn::/v1/user/invite/list
            # https://dev.pangea.cloud/docs/api/authn#list-invites # FIXME: Update url once in prod
            def list(self) -> PangeaResponse[UserInviteListResult]:
                response = self.request.post("user/invite/list", data={})
                if response.raw_result is not None:
                    response.result = UserInviteListResult(**response.raw_result)
                return response

            #   - path: authn::/v1/user/invite/delete
            # https://dev.pangea.cloud/docs/api/authn#delete-an-invite # FIXME: Update url once in prod
            def delete(self, id: str) -> PangeaResponse[UserInviteDeleteResult]:
                input = UserInviteDeleteRequest(id=id)
                response = self.request.post("user/invite/delete", data=input.dict(exclude_none=True))
                if response.raw_result is not None:
                    response.result = UserInviteDeleteResult(**response.raw_result)
                return response
