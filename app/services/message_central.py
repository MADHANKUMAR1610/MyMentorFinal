import base64
import httpx
from typing import Any


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

    # ============================================================
    # GENERATE AUTH TOKEN
    # ============================================================

    async def generate_auth_token(self) -> str:

        encoded_password = base64.b64encode(
            self.password.encode("utf-8")
        ).decode("utf-8")

        url = (
            f"{self.BASE_URL}"
            "/auth/v1/authentication/token"
        )

        params = {
            "customerId": self.customer_id,
            "key": encoded_password,
            "scope": "NEW",
            "country": self.country,
            "email": self.email,
        }

        headers = {
            "accept": "*/*",
        }

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.get(
                url,
                params=params,
                headers=headers,
            )

        response.raise_for_status()

        data = response.json()

        token = data.get("token")

        if not token:
            raise RuntimeError(
                f"Message Central token generation failed: {data}"
            )

        return token

    # ============================================================
    # SEND OTP
    # ============================================================

    async def send_otp(
        self,
        phone: str,
    ) -> dict[str, Any]:

        auth_token = await self.generate_auth_token()

        # --------------------------------------------------------
        # CLEAN PHONE
        # --------------------------------------------------------

        phone = phone.strip()

        phone = phone.replace(
            " ",
            "",
        ).replace(
            "-",
            "",
        )

        if phone.startswith("+91"):
            phone = phone[3:]

        elif (
            phone.startswith("91")
            and len(phone) == 12
        ):
            phone = phone[2:]

        if not phone.isdigit():
            raise ValueError(
                "Phone number must contain only digits."
            )

        if len(phone) != 10:
            raise ValueError(
                "Please enter a valid 10-digit Indian mobile number."
            )

        # --------------------------------------------------------
        # SEND API
        # --------------------------------------------------------

        url = (
            f"{self.BASE_URL}"
            "/verification/v3/send"
        )

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

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.post(
                url,
                params=params,
                headers=headers,
            )

        response.raise_for_status()

        data = response.json()

        print(
            "Message Central SEND response:",
            data,
        )

        if data.get("responseCode") != 200:
            raise RuntimeError(
                f"Message Central OTP send failed: {data}"
            )

        return data

    # ============================================================
    # VERIFY OTP
    # ============================================================

    async def verify_otp(
        self,
        verification_id: str,
        otp: str,
    ) -> dict[str, Any]:

        auth_token = await self.generate_auth_token()

        url = (
            f"{self.BASE_URL}"
            "/verification/v3/validateOtp"
        )

        params = {
            "verificationId": verification_id,
            "code": otp,
        }

        headers = {
            "accept": "*/*",
            "authToken": auth_token,
        }

        # Message Central uses GET for validateOtp
        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.get(
                url,
                params=params,
                headers=headers,
            )

        print(
            "Message Central VERIFY status:",
            response.status_code,
        )

        print(
            "Message Central VERIFY response:",
            response.text,
        )

        response.raise_for_status()

        data = response.json()

        # IMPORTANT
        # Always return the response
        if data is None:
            raise RuntimeError(
                "Message Central returned an empty response."
            )

        return data