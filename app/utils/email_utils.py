from urllib.parse import urlparse


# ============================================================
# PERSONAL EMAIL DOMAINS
# ============================================================

PUBLIC_EMAIL_DOMAINS = {
    "gmail.com",
    "googlemail.com",
    "yahoo.com",
    "yahoo.co.in",
    "hotmail.com",
    "outlook.com",
    "live.com",
    "icloud.com",
    "protonmail.com",
    "proton.me",
    "rediffmail.com",
}


# ============================================================
# GET EMAIL DOMAIN
# ============================================================

def get_email_domain(email: str) -> str:

    email = email.strip().lower()

    if "@" not in email:
        raise ValueError(
            "Invalid email address."
        )

    local_part, domain = email.rsplit("@", 1)

    if not local_part or not domain:
        raise ValueError(
            "Invalid email address."
        )

    return domain


# ============================================================
# GET WEBSITE DOMAIN
# ============================================================

def get_website_domain(
    website: str,
) -> str:

    website = website.strip().lower()

    if not website.startswith(
        ("http://", "https://")
    ):
        website = "https://" + website

    parsed = urlparse(website)

    domain = parsed.hostname

    if not domain:
        raise ValueError(
            "Invalid company website."
        )

    if domain.startswith("www."):
        domain = domain[4:]

    return domain


# ============================================================
# VALIDATE OFFICIAL COMPANY EMAIL
# ============================================================

def validate_official_company_email(
    email: str,
    website: str,
) -> str:

    email = email.strip().lower()

    # --------------------------------------------------------
    # GET ADMIN EMAIL DOMAIN
    # --------------------------------------------------------

    email_domain = get_email_domain(
        email
    )

    # --------------------------------------------------------
    # BLOCK PERSONAL EMAIL
    # --------------------------------------------------------

    if email_domain in PUBLIC_EMAIL_DOMAINS:
        raise ValueError(
            "Admin email must be an official company email. "
            "Gmail, Yahoo, Outlook and other personal email "
            "providers are not allowed."
        )

    # --------------------------------------------------------
    # GET COMPANY WEBSITE DOMAIN
    # --------------------------------------------------------

    company_domain = get_website_domain(
        website
    )

    # --------------------------------------------------------
    # CHECK DOMAIN
    # --------------------------------------------------------

    if email_domain != company_domain:
        raise ValueError(
            f"Admin email must use the official company "
            f"domain @{company_domain}."
        )

    return email