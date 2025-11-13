import datetime

from typing import Optional

from pydantic import BaseModel, Field


class Skill(BaseModel):
    name: str = Field(..., description="The name of the skill")


class Education(BaseModel):
    institution_name: str = Field(default="", description="The name of the institution")
    linkedin_url: str = Field(
        default="", description="The linkedin url of the institution"
    )
    degree: str = Field(default="", description="The degree of the education")
    start: Optional[datetime.datetime] = Field(
        None, description="The start of the education"
    )
    end: Optional[datetime.datetime] = Field(
        None, description="The end of the education"
    )
    description: str = Field(default="", description="The description of the education")


class Institution(BaseModel):
    institution_name: str = Field(default="", description="The name of the institution")
    linkedin_url: str = Field(
        default="", description="The linkedin url of the institution"
    )
    website: str = Field(default="", description="The website of the institution")
    industry: str = Field(default="", description="The industry of the institution")
    type: str = Field(default="", description="The type of the institution")
    headquarters: str = Field(
        default="", description="The headquarters of the institution"
    )
    company_size: int = Field(
        default="", description="The company size of the institution"
    )
    founded: int = Field(default="", description="The year the institution was founded")


class Experience(Institution):
    from_date: str = Field(default="", description="The start date of the experience")
    to_date: str = Field(default="", description="The end date of the experience")
    description: str = Field(
        default="", description="The description of the experience"
    )
    position_title: str = Field(
        default="", description="The position title of the experience"
    )
    duration: str = Field(default="", description="The duration of the experience")
    location: str = Field(default="", description="The location of the experience")


class ProfileSearchResult(BaseModel):
    person_name: str = Field(..., description="The name of the person")
    person_linkedin_url: str = Field(..., description="The linkedin url of the person")
    profile_id: str = Field(..., description="The profile id of the person")
    title: str = Field(default="", description="The title of the person")


class Profile(BaseModel):
    given_name: str = Field(..., description="The given name of the consultant")
    surname: str = Field(..., description="The surname of the consultant")
    email: str = Field(..., description="The email of the consultant")
    cv: str = Field(..., description="The curriculum vitae of the consultant")
    summary: str = Field(default="", description="The summary of the consultant")
    industry_name: str = Field(
        ..., description="The industry in which the consultant is working"
    )
    geo_location: str = Field(
        ..., description="The geographical location of the consultant"
    )
    linkedin_profile_url: str = Field(..., description="The linkedin profile")
    experiences: list[Experience] = Field(
        ..., description="The experiences of this user"
    )
    skills: list[Skill] = Field(..., description="The list of skills")
    educations: list[Education] = Field(
        default=[], description="The educations of this user"
    )
    photo_200: str | None = Field(
        default=None, description="The 200x200 photo of the consultant"
    )
    photo_400: str | None = Field(
        default=None, description="The 400x400 photo of the consultant"
    )
