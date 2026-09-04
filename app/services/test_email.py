import asyncio

from app.services.email_service import EmailService


async def main():
    service = EmailService()

    result = await service.send_email(
        to_email="your_verified_test_recipient@gmail.com",
        subject="MyMentor Email Test",
        html_content="<h2>Hello from MyMentor</h2><p>Email service is working.</p>",
        text_content="Hello from MyMentor. Email service is working.",
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())