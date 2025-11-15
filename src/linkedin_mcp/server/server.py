import logging

from mcp.server.fastmcp import FastMCP, Context
from linkedin_mcp.config.config import cfg
from linkedin_mcp.service.browser_scraper.profile_extraction import (
    extract_profile,
    search_profiles_by_name,
)


logger = logging.getLogger(__name__)

mcp = FastMCP(name="linkedin-mcp", host=cfg.mcp_host, port=cfg.mcp_port)


@mcp.tool()
async def linkedin_profile(
    profile: str,
    extract_educations: bool = False,
    extract_skills: bool = False,
    extract_interests: bool = False,
    ctx: Context = None,
) -> dict:
    """
    Extract a LinkedIn profile using web scraping with Selenium.

    Args:
        profile: The LinkedIn profile URL or username
        extract_educations: If True, extract educations
        extract_skills: If True, extract skills
        extract_interests: If True, extract the profile interests

    Returns:
        The LinkedIn profile as a dictionary

    Example output in case of success:
        {
            "given_name": "Gil",
            "surname": "Fernandes",
            "email": "gil-palma-fernandes@linkedin.com",
            "cv": "A Software Engineer and data scientist with over 25 years of professional experience in different companies. I spent a good part of my professional career working in projects related to the aviation industry and the rest as developer in Talend and Java based projects.\nIn 2019 I commenced my learning on Artificial Intelligence and Deep Learning and related technologies and participated in several Kaggle competitions.\nI dedicate my weekends to my pet projects for UK charities which promote well-being and meditation.",
            "summary": "",
            "industry_name": "Software Engineer at Onepoint Consulting",
            "geo_location": "London Area, United Kingdom",
            "linkedin_profile_url": "https://www.linkedin.com/in/gil-palma-fernandes",
            "experiences": [
                {
                    "institution_name": "Onepoint Consulting \u00b7 Full-time",
                    "linkedin_url": "https://www.linkedin.com/company/309728/",
                    "website": "",
                    "industry": "",
                    "type": "",
                    "headquarters": "", ...

    Example output in case of error:
    {
        "error": "Error extracting profile: Error extracting profile"
    }
    """
    try:
        if ctx:
            await ctx.report_progress(
                progress=10,
                total=100,
                message="Starting Selenium browser and logging in...",
            )
        profile = await extract_profile(
            profile,
            extract_educations=extract_educations,
            extract_skills=extract_skills,
            extract_interests=extract_interests,
            force_login=True,
        )
        return profile.model_dump()
    except Exception as e:
        logger.error(f"Error extracting profile: {e}")
        return {"error": str(e)}


@mcp.tool()
async def profile_search(name: str, ctx: Context = None) -> list[dict] | dict:
    """
    Search for LinkedIn profiles by name.

    Args:
        name: The name to search for

    Returns:
        A list of LinkedIn profiles as dictionaries

    Example output in case of success:
        [
        {
            "person_name": "Gil Fernandes",
            "person_linkedin_url": "https://www.linkedin.com/in/gil-palma-fernandes/",
            "profile_id": "gil-palma-fernandes",
            "title": "Software Engineer at Onepoint Consulting"
        },
        {
            "person_name": "Gil Fernandes",
            "person_linkedin_url": "https://www.linkedin.com/in/gil-fernandes-a7578334a/",
            "profile_id": "gil-fernandes-a7578334a",
            "title": "Passionate Holistic Therapist and Dynamic Team Leader with over 12 years of experience across diverse care settings. Skilled in crisis management and dedicated to fostering well-being in every aspect of care!"
        } ...

    Example output in case of error:
        {
            "error": "Error searching profiles: Error searching profiles"
        }
    """
    try:
        if ctx:
            await ctx.report_progress(
                progress=10, total=100, message="Starting LinkedIn profile search..."
            )
        results = await search_profiles_by_name(name, headless=True, force_login=True)
        return [result.model_dump() for result in results]
    except Exception as e:
        logger.error(f"Error searching profiles: {e}")
        return {"error": str(e)}


@mcp.prompt()
async def profile_search_by_name(name: str) -> str:
    """Returns a prompt that you can use to search for a LinkedIn profile by name."""
    return f"""
Can you search for a LinkedIn profile by name? The name is {name}. Can you list the names with corresponding titles and linkedin urls?
    """


@mcp.prompt()
async def profile_experiences_by_profile_id(profile_id: str) -> str:
    """Returns a prompt that you can use to list the experiences of a LinkedIn profile by profile id."""
    return f"""
Can you list the professional experiences of the LinkedIn user with this profile id: {profile_id}
    """


if __name__ == "__main__":
    import sys

    transport = sys.argv[1] if len(sys.argv) > 1 else cfg.mcp_transport
    logger.info(
        f"Starting MCP server on {cfg.mcp_host}:{cfg.mcp_port} with transport {cfg.mcp_transport}"
    )
    mcp.run(transport=transport)
