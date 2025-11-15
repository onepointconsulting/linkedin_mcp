import logging

from mcp.server.fastmcp import Context
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from linkedin_mcp.config.config import cfg
from linkedin_mcp.model.linkedin_person import Person
from linkedin_mcp.model.linkedin_profile import (
    Interest,
    Profile,
    ProfileSearchResult,
    Skill,
)

from linkedin_mcp.service.browser_scraper.cookie_manager import login_with_cookies
from linkedin_mcp.service.browser_scraper.linkedin_search import PersonSearchScraper
from linkedin_mcp.service.browser_scraper.profile_scraper import Scraper
from linkedin_mcp.utils.linkedin_util_functions import correct_linkedin_url


logger = logging.getLogger(__name__)


def _create_driver(headless: bool = True) -> webdriver.Chrome:  #
    # Configure Chrome options
    options = Options()
    if headless:
        options.add_argument("--headless=new")  # 'new' mode for Chrome >= 109
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )


def _convert_to_consultant(person: Person | None) -> Profile | None:
    if not person:
        return None
    names = person.name.split(" ")
    if len(names) == 0:
        return None
    if len(names) == 1:
        surname = ""
    else:
        surname = names[1]
    return Profile(
        given_name=names[0],
        surname=surname,
        email="",
        cv=person.about if person.about else "",
        industry_name=person.headline,
        geo_location=person.location,
        linkedin_profile_url=person.linkedin_url,
        experiences=person.experiences,
        educations=person.educations,
        skills=[Skill(name=s) for s in person.skills],
        interests=[
            Interest(name=i.name, linkedin_url=i.linkedin_url, type=i.type)
            for i in person.interests
        ],
    )


def perform_login(headless: bool = True, force_login: bool = False) -> webdriver.Chrome:
    driver = _create_driver(headless=headless)
    user, password = cfg.get_random_linkedin_credential()

    # Use cookie-based login (will fall back to regular login if cookies don't work)
    login_with_cookies(driver, user, password, force_login=force_login)
    logger.info("Logged in to LinkedIn")
    return driver


async def extract_profile(
    profile: str,
    force_login: bool = True,
    extract_educations: bool = False,
    extract_skills: bool = False,
    extract_interests: bool = False,
    headless: bool = True,
    ctx: Context = None,
) -> Profile | None:
    """
    Extract a LinkedIn profile using web scraping with Selenium.

    Args:
        profile: LinkedIn profile URL or username
        force_login: If True, skip cookie loading and force a fresh login
        extract_educations: If True, extract educations
        extract_experiences_from_homepage: If True, extract experiences from the homepage
    Returns:
        Profile object if successful, None otherwise
    """
    driver = perform_login(headless=headless, force_login=force_login)
    if ctx:
        await ctx.report_progress(
            progress=10, total=100, message="Finished logging in to LinkedIn"
        )
    else:
        logger.info("Logged in to LinkedIn")

    profile = correct_linkedin_url(profile)
    logger.info(f"Corrected LinkedIn URL: {profile}")
    scraper = Scraper(
        driver,
        profile,
        extract_educations=extract_educations,
        extract_skills=extract_skills,
        extract_interests=extract_interests,
    )

    if ctx:
        await ctx.report_progress(
            progress=10, total=100, message="About to scrape the profile"
        )
    else:
        logger.info("About to scrape the profile")
    scraper.scrape()
    if ctx:
        await ctx.report_progress(
            progress=10, total=100, message="Finished scraping the profile"
        )
    else:
        logger.info("Finished scraping the profile")
    person = scraper.person
    logger.info(f"Extracted profile: {person}")
    consultant = _convert_to_consultant(person)
    consultant.email = f"{profile.split('/')[-1]}@linkedin.com"
    return consultant


async def search_profiles_by_name(
    name: str,
    headless: bool = True,
    force_login: bool = True,
    ctx: Context = None,
) -> list[ProfileSearchResult]:
    driver = perform_login(headless=headless, force_login=force_login)
    if ctx:
        await ctx.report_progress(
            progress=10, total=100, message="Finished logging in to LinkedIn"
        )
    else:
        logger.info("Logged in to LinkedIn")
    scraper = PersonSearchScraper(driver)
    return scraper.search(name)
