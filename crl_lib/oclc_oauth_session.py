import oauthlib
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
from time import time


TOKEN_URL = 'https://oauth.oclc.org/token'


class OclcClientCredentialsGrant:

    def __init__(
        self, 
        api_key: str, 
        api_secret: str, 
        scope: str='WorldCatMetadataAPI'
        ) -> None:

        self.api_key = api_key
        self.api_secret = api_secret
        self.scope = scope

        self.oauth_session = None
        self.auth = None
        self.create_oauth_session()

    def create_oauth_session(self) -> None:
        self.auth = HTTPBasicAuth(self.api_key, self.api_secret)
        client = oauthlib.oauth2.BackendApplicationClient(
            client_id=self.api_key, scope=self.scope)
        self.oauth_session = OAuth2Session(client=client)

    def fetch_token(self) -> None:
        try:
            self._token = self.oauth_session.fetch_token(
                token_url=TOKEN_URL, auth=self.auth)
        except BaseException as err:
            print(err)

    def check_for_valid_token(self) -> None:
        """
        If the token is set to expire in under 20 seconds, refresh it.
        If there is no toke, create one.
        """
        try:
            current_time = time()
            if self._token['expires_at'] - current_time < 20:
                self.fetch_token()
        except AttributeError:
            self.fetch_token()

    @property
    def token(self) -> oauthlib.oauth2.rfc6749.tokens.OAuth2Token:
        return self._token

    @token.getter
    def token(self) -> oauthlib.oauth2.rfc6749.tokens.OAuth2Token:
        """
        Getter for the token.
        Refresh token if it's expired or is going to expire in under 20 seconds.
        """
        self.fetch_token()
        return self._token
