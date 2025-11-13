def correct_linkedin_url(url: str) -> str:
    if not url.startswith("https://www.linkedin.com/in/"):
        url = f"https://www.linkedin.com/in/{url}"
    return url


def extract_profile_id(url: str) -> str:
    if url.endswith("/"):
        url = url[:-1]
    return url.split("/")[-1]
