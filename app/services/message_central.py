import base64
import json
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

    @staticmethod
    def _safe_error_details(result: Any) -> str:
        """
        Extract useful error details without logging credentials
        or authentication tokens.
        """
        if not isinstance(result, dict):
            return str(result)[:1000]

        safe_result = {}

        for key in (
            "status",
            "responseCode",
            "message",
            "error",
            "errorMessage",
            "error_description",
            "timestamp",
            "path",
        ):
            if key in result:
                value = result[key]

                # Do not expose token-like values.
                if key.lower() in {
                    "token",
                    "authtoken",
                    "accesstoken",
                    "password",
                    "key",
                }:
                    continue

                safe_result[key] = value

        return json.dumps(safe_result, default=str)[:1000]

    async def generate_auth_token(self) -> str:
        """
        Generate an authentication token using Message Central.
        """

        if not all(
            [
                self.customer_id,
                self.email,
                self.password,
                self.country,
            ]
        ):
            raise RuntimeError(
                "Message Central configuration is incomplete. "
                "Check the MESSAGECENTRAL environment variables."
            )

        encoded_password = base64.b64encode(
            self.password.encode("utf-8")
        ).decode("utf-8")

        url = (
            f"{self.BASE_URL}/auth/v1/authentication/token"
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

        try:
            async with httpx.AsyncClient(
                timeout=30.0
            ) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=headers,
                )

        except httpx.TimeoutException as exc:
            print(
                "Message Central AUTH error: "
                "Request timed out."
            )
            raise RuntimeError(
                "Message Central authentication timed out."
            ) from exc

        except httpx.RequestError as exc:
            # Do not print the request URL because it contains
            # encoded credentials in its query parameters.
            print(
                "Message Central AUTH connection error:",
                type(exc).__name__,
            )
            raise RuntimeError(
                "Unable to connect to Message Central."
            ) from exc

        try:
            result = response.json()
        except ValueError:
            result = None

        if response.is_error:
            print(
                "Message Central AUTH HTTP status:",
                response.status_code,
            )

            if result is not None:
                print(
                    "Message Central AUTH provider error:",
                    self._safe_error_details(result),
                )
            else:
                print(
                    "Message Central AUTH returned "
                    "a non-JSON error response."
                )

            raise RuntimeError(
                "Message Central authentication failed "
                f"(HTTP {response.status_code}). "
                "Check the provider error in backend logs."
            )

        if not isinstance(result, dict):
            print(
                "Message Central AUTH error: "
                "Response was not a JSON object."
            )
            raise RuntimeError(
                "Message Central returned an unexpected "
                "authentication response."
            )

        # Support common token response formats.
        token = result.get("token")

        if not token and isinstance(result.get("data"), dict):
            token = result["data"].get("token")

        if not token:
            print(
                "Message Central AUTH status:",
                str(result.get("status", "Unknown"))[:200],
            )

            print(
                "Message Central AUTH provider error:",
                self._safe_error_details(result),
            )

            raise RuntimeError(
                "Message Central did not return an "
                "authentication token. Check provider "
                "credentials and the response format."
            )

        return str(token)

    async def send_otp(
        self,
        phone: str,
    ) -> dict[str, Any]:
        """
        Send a six-digit SMS OTP to an Indian mobile number.
        """

        phone = (
            phone.strip()
            .replace(" ", "")
            .replace("-", "")
        )

        if phone.startswith("+91"):
            phone = phone[3:]
        elif phone.startswith("91") and len(phone) == 12:
            phone = phone[2:]

        if not phone.isdigit() or len(phone) != 10:
            raise ValueError(
                "Please enter a valid 10-digit Indian "
                "mobile number."
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

        try:
            async with httpx.AsyncClient(
                timeout=30.0
            ) as client:
                response = await client.post(
                    url,
                    params=params,
                    headers=headers,
                )

        except httpx.TimeoutException as exc:
            print(
                "Message Central SEND error: "
                "Request timed out."
            )
            raise RuntimeError(
                "The OTP provider request timed out."
            ) from exc

        except httpx.RequestError as exc:
            print(
                "Message Central SEND connection error:",
                type(exc).__name__,
            )
            raise RuntimeError(
                "Unable to connect to the OTP provider."
            ) from exc

        try:
            result = response.json()
        except ValueError:
            result = None

        if response.is_error:
            print(
                "Message Central SEND HTTP status:",
                response.status_code,
            )

            if result is not None:
                print(
                    "Message Central SEND provider error:",
                    self._safe_error_details(result),
                )

            raise RuntimeError(
                "Message Central failed to send the OTP. "
                f"HTTP status: {response.status_code}."
            )

        if not isinstance(result, dict):
            raise RuntimeError(
                "Message Central returned an unexpected "
                "OTP response."
            )

        response_code = str(result.get("responseCode", ""))

        print(
            "Message Central SEND response code:",
            response_code or "Missing",
        )

        if response_code != "200":
            print(
                "Message Central SEND provider error:",
                self._safe_error_details(result),
            )

            raise RuntimeError(
                "Message Central rejected the OTP request. "
                "Check the provider error in backend logs."
            )

        data = result.get("data")

        if (
            not isinstance(data, dict)
            or not data.get("verificationId")
        ):
            print(
                "Message Central SEND error: "
                "verificationId is missing."
            )
            raise RuntimeError(
                "Message Central did not return a "
                "verification ID."
            )

        return result

    async def verify_otp(
        self,
        verification_id: str,
        otp: str,
    ) -> dict[str, Any]:
        """
        Verify the OTP using the provider's verification ID.
        """

        verification_id = verification_id.strip()
        otp = otp.strip()

        if not verification_id:
            raise ValueError(
                "Verification ID is required."
            )

        if not otp.isdigit() or len(otp) != 6:
            raise ValueError(
                "Please enter a valid six-digit OTP."
            )

        auth_token = await self.generate_auth_token()

        url = (
            f"{self.BASE_URL}/verification/v3/validateOtp"
        )

        params = {
            "verificationId": verification_id,
            "code": otp,
        }

        headers = {
            "accept": "*/*",
            "authToken": auth_token,
        }

        try:
            async with httpx.AsyncClient(
                timeout=30.0
            ) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=headers,
                )

        except httpx.TimeoutException as exc:
            print(
                "Message Central VERIFY error: "
                "Request timed out."
            )
            raise RuntimeError(
                "OTP verification timed out."
            ) from exc

        except httpx.RequestError as exc:
            print(
                "Message Central VERIFY connection error:",
                type(exc).__name__,
            )
            raise RuntimeError(
                "Unable to connect to the OTP provider "
                "for verification."
            ) from exc

        try:
            result = response.json()
        except ValueError:
            result = None

        if response.is_error:
            print(
                "Message Central VERIFY HTTP status:",
                response.status_code,
            )

            if result is not None:
                print(
                    "Message Central VERIFY provider error:",
                    self._safe_error_details(result),
                )

            raise RuntimeError(
                "Message Central OTP verification request "
                f"failed (HTTP {response.status_code})."
            )

        if not isinstance(result, dict):
            raise RuntimeError(
                "Message Central returned an unexpected "
                "verification response."
            )

        print(
            "Message Central VERIFY response code:",
            str(result.get("responseCode", "Missing")),
        )

        return result
