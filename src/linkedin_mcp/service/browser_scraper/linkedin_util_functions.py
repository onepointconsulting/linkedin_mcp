from datetime import datetime
import re


def correct_linkedin_url(url: str) -> str:
    if not url.startswith("https://www.linkedin.com/in/"):
        url = f"https://www.linkedin.com/in/{url}"
    return url


def extract_profile_id(url: str) -> str:
    if url.endswith("/"):
        url = url[:-1]
    return url.split("/")[-1]


def convert_linkedin_date(date_str: str | None) -> datetime | None:
    """
    Convert a LinkedIn date string to a datetime object.
    Example: "Oct 2009" -> datetime(2009, 10, 1)
    """
    if not date_str:
        return None
    if re.match(r"^[a-zA-Z]+ \d{4}$", date_str):
        return datetime.strptime(date_str, "%b %Y")
    return None
