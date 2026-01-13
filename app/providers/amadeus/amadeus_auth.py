import os
import time
import requests

class AmadeusAuth:

    TOKEN_URL = "/v1/security/oauth2/token"

    def __init__(self):
        self.base_url = os.getenv("AMADEUS_BASE_URL")
        self.client_id = os.getenv("AMADEUS_CLIENT_ID")
        self.client_secret = os.getenv("AMADEUS_CLIENT_SECRET")

        self._access_token = None
        self._expires_at = 0

    def get_token(self) -> str:
        if self._access_token and time.time() < self._expires_at:
            return self._access_token

        response = requests.post(
            f"{self.base_url}{self.TOKEN_URL}",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            },
            timeout=10
        )

        response.raise_for_status()
        payload = response.json()

        self._access_token = payload["access_token"]
        self._expires_at = time.time() + payload["expires_in"] - 30  # margem

        return self._access_token
