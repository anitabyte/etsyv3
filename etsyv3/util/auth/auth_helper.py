import base64
import hashlib
import secrets
from typing import List, Optional, Tuple

from etsyv3 import BadRequest
from requests_oauthlib import OAuth2Session  # type: ignore[import]


class AuthHelper:
    def __init__(
        self,
        keystring: str,
        redirect_uri: str,
        scopes: Optional[List[str]] = None,
        code_verifier: Optional[str] = None,
        state: Optional[str] = None,
    ):
        self.keystring = keystring
        self.redirect_url = redirect_uri
        self.scopes = scopes
        if code_verifier is None:
            self.code_verifier = secrets.token_urlsafe(32)
        else:
            self.code_verifier = code_verifier
        self.code_challenge = AuthHelper._generate_challenge(self.code_verifier)
        self.oauth = OAuth2Session(
            keystring, redirect_uri=self.redirect_url, scope=scopes
        )
        self.state = secrets.token_urlsafe(16) if state is None else state
        self.auth_code: Optional[str] = None
        self.token: Optional[str] = None

    def get_auth_code(self) -> Tuple[str, str]:
        authorisation_url, state = self.oauth.authorization_url(
            "https://www.etsy.com/oauth/connect",
            state=self.state,
            code_challenge=self.code_challenge,
            code_challenge_method="S256",
        )
        return authorisation_url, state

    def set_authorisation_code(self, code: str, state: str) -> None:
        if state == self.state:
            self.auth_code = code
        else:
            # etsy follows RFC 6749, per spec bad state should raise invalid request, https://datatracker.ietf.org/doc/html/rfc6749#section-5.2
            raise BadRequest(
                {"error": "invalid_request", "error_description": "State mismatch"}
            )

    def get_access_token(self) -> Optional[str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "x-api-key": self.keystring,
        }
        self.token = self.oauth.fetch_token(
            "https://api.etsy.com/v3/public/oauth/token",
            code=self.auth_code,
            code_verifier=self.code_verifier,
            include_client_id=True,
            headers=headers,
        )
        return self.token

    @staticmethod
    def _generate_challenge(code_verifier: str) -> str:
        m = hashlib.sha256(code_verifier.encode("utf-8"))
        b64_encode = base64.urlsafe_b64encode(m.digest()).decode("utf-8")
        # per https://docs.python.org/3/library/base64.html, there may be a trailing '=' - get rid of it
        return b64_encode.split("=")[0]
