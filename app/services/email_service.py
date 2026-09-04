import httpx

from app.core.config import settings


class EmailService:

    async def send_email(
        self,
        *,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str | None = None,
    ) -> dict:

        payload = {
            "from": {
                "email": settings.MAILERSEND_FROM_EMAIL,
                "name": settings.MAILERSEND_FROM_NAME,
            },
            "to": [
                {
                    "email": to_email,
                }
            ],
            "subject": subject,
            "html": html_content,
        }

        if text_content:
            payload["text"] = text_content

        headers = {
            "Authorization": f"Bearer {settings.MAILERSEND_API_TOKEN}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.MAILERSEND_API_URL,
                json=payload,
                headers=headers,
            )

        if response.status_code not in (200, 202):
            raise Exception(
                f"MailerSend error: "
                f"{response.status_code} - {response.text}"
            )

        return {
            "success": True,
            "message": "Email sent successfully",
        }