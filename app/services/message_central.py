
import base64
from typing import Any

import httpx


class MessageCentralService:
    BASE_URL = "https://cpaas.messagecentral.com"

    def __init__(
        self,
        customer_id: str,
        email: str,
        password: str,
        country: str = "91",
    ):
        self.customer_id = customer_id
        self.email = email
        self.password = password
        self.country = country

    async def generate_auth_token(self) -> str:
        if not all(
            [
                self.customer_id,
                self.email,
                self.password,
                self.country,
            ]
        ):
            raise RuntimeError(
                "Message Central configuration is incomplete."
            )

        encoded_password = base64.b64encode(
            self.password.encode("utf-8")
        ).decode("utf-8")

        url = f"{self.BASE_URL}/auth/v1/authentication/token"

        params = {
            "customerId": self.customer_id,
            "key": encoded_password,
            "scope": "NEW",
            "country": self.country,
            "email": self.email,
        }

        headers = {"accept": "*/*"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                params=params,
                headers=headers,
            )

        if response.is_error:
            print(
                "Message Central AUTH HTTP error:",
                response.status_code,
                response.text[:1000],
            )
            response.raise_for_status()

        try:
            result = response.json()
        except ValueError as exc:
            raise RuntimeError(
                "Message Central authentication returned invalid JSON."
            ) from exc

        if not isinstance(result, dict):
            raise RuntimeError(
                "Unexpected Message Central authentication response."
            )

        # Support the common top-level and nested token response shapes.
        token = result.get("token")
        if not token and isinstance(result.get("data"), dict):
            token = result["data"].get("token")

        if not token:
            # Do not print the full response because it may contain secrets.
            print(
                "Message Central authentication returned no token. "
                "Response keys:",
                list(result.keys()),
            )
            raise RuntimeError(
                "Message Central did not return an authentication token."
            )

        return str(token)

    async def send_otp(self, phone: str) -> dict[str, Any]:
        phone = phone.strip().replace(" ", "").replace("-", "")

        if phone.startswith("+91"):
            phone = phone[3:]
        elif phone.startswith("91") and len(phone) == 12:
            phone = phone[2:]

        if not phone.isdigit() or len(phone) != 10:
            raise ValueError(
                "Please enter a valid 10-digit Indian mobile number."
            )

        auth_token = await self.generate_auth_token()

        url = f"{self.BASE_URL}/verification/v3/send"

        params = {
            "countryCode": self.country,
            "flowType": "SMS",
            "mobileNumber": phone,
            "otpLength": 6,
        }

        headers = {
            "accept": "*/*",
            "authToken": auth_token,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                params=params,
                headers=headers,
            )

        if response.is_error:
            print(
                "Message Central SEND HTTP error:",
                response.status_code,
                response.text[:1000],
            )
            response.raise_for_status()

        try:
            result = response.json()
        except ValueError as exc:
            raise RuntimeError(
                "Message Central returned invalid JSON when sending OTP."
            ) from exc

        if not isinstance(result, dict):
            raise RuntimeError(
                "Unexpected Message Central OTP response."
            )

        print(
            "Message Central SEND response code:",
            result.get("responseCode"),
        )

        # Some APIs serialize response codes as strings.
        if str(result.get("responseCode")) != "200":
            print(
                "Message Central rejected OTP request:",
                str(result.get("message", "No message provided"))[:500],
            )
            raise RuntimeError(
                "Message Central rejected the OTP request. "
                "Check backend logs for the provider response."
            )

        data = result.get("data")
        if not isinstance(data, dict) or not data.get("verificationId"):
            print(
                "Message Central OTP response is missing verificationId."
            )
            raise RuntimeError(
                "Message Central did not return a verification ID."
            )

        return result

    async def verify_otp(
        self,
        verification_id: str,
        otp: str,
    ) -> dict[str, Any]:
        auth_token = await self.generate_auth_token()

        url = f"{self.BASE_URL}/verification/v3/validateOtp"

        params = {
            "verificationId": verification_id,
            "code": otp,
        }

        headers = {
            "accept": "*/*",
            "authToken": auth_token,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                params=params,
                headers=headers,
            )

        if response.is_error:
            print(
                "Message Central VERIFY HTTP error:",
                response.status_code,
                response.text[:1000],
            )
            response.raise_for_status()

        try:
            result = response.json()
        except ValueError as exc:
            raise RuntimeError(
                "Message Central returned invalid verification JSON."
            ) from exc

        if not isinstance(result, dict):
            raise RuntimeError(
                "Unexpected Message Central verification response."
            )

        return result
