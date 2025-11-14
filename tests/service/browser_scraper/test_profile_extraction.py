from pathlib import Path
import json
import asyncio

from linkedin_mcp.service.browser_scraper.profile_extraction import (
    extract_profile,
    search_profiles_by_name,
)

"""Tests for actions module."""


def test_extract_profile_full():
    profile = asyncio.run(
        extract_profile(
            "gil-palma-fernandes",
            headless=False,
            extract_educations=True,
            extract_skills=True,
            extract_interests=True,
        )
    )
    assert profile is not None, "The profile cannot be retrieved."
    assert (
        profile.cv is not None and profile.cv != ""
    ), "The curriculum vitae cannot be retrieved."
    assert (
        profile.experiences is not None and len(profile.experiences) > 0
    ), "The experiences cannot be retrieved."
    assert (
        profile.educations is not None and len(profile.educations) > 0
    ), "The educations cannot be retrieved."
    assert (
        profile.skills is not None and len(profile.skills) > 0
    ), "The skills cannot be retrieved."
    assert (
        profile.interests is not None and len(profile.interests) > 0
    ), "The interests cannot be retrieved."
    Path("profiles").mkdir(exist_ok=True)
    with open(Path("profiles") / f"{profile.email}.json", "w") as f:
        json.dump(profile.model_dump(), f)


def test_extract_profile_mkhere():
    _basic_tester("mkhere")


def test_extract_profile_robertbaldock():
    _basic_tester("robertbaldock")


def test_extract_profile_shashinbshah():
    _basic_tester("shashinbshah")


def _basic_tester(profile_id: str):
    profile = asyncio.run(extract_profile(profile_id, headless=False, force_login=True))
    assert profile is not None, "The profile cannot be retrieved."
    assert (
        profile.cv is not None and profile.cv != ""
    ), "The curriculum vitae cannot be retrieved."
    assert (
        profile.experiences is not None and len(profile.experiences) > 0
    ), "The experiences cannot be retrieved."


def test_search_consultants_by_name_alexander_polev():
    consultants = asyncio.run(
        search_profiles_by_name("alexander polev", headless=False, force_login=False)
    )
    assert consultants is not None, "The consultants cannot be retrieved."
    assert len(consultants) > 0, "The consultants cannot be retrieved."


def test_search_consultants_by_name_gil_palma_fernandes():
    consultants = asyncio.run(
        search_profiles_by_name("gil fernandes", headless=False, force_login=True)
    )
    assert consultants is not None, "The consultants cannot be retrieved."
    assert len(consultants) > 0, "The consultants cannot be retrieved."
    Path("profiles").mkdir(exist_ok=True)
    with open(
        Path("profiles") / f"search_consultants_by_name_gil_palma_fernandes.json", "w"
    ) as f:
        json.dump([c.model_dump() for c in consultants], f)


def test_search_consultants_by_name_murtaza_hassani():
    consultants = asyncio.run(
        search_profiles_by_name("murtaza hassani", headless=False, force_login=True)
    )
    assert consultants is not None, "The consultants cannot be retrieved."
    assert len(consultants) > 0, "The consultants cannot be retrieved."
