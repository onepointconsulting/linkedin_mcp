from dataclasses import dataclass
import logging

from webbrowser import Chrome
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from tenacity import retry, stop_after_attempt, wait_fixed


from linkedin_mcp.model.linkedin_person import Person
from linkedin_mcp.model.linkedin_profile import Education, Experience
from linkedin_mcp.service.browser_scraper.linkedin_util_functions import (
    convert_linkedin_date,
)
from linkedin_mcp.service.browser_scraper.scraper_base import ScraperBase

logger = logging.getLogger(__name__)


"""Copied from linkedin_scraper"""


@dataclass
class Scraper(ScraperBase):
    __TOP_CARD = "main"
    TOP_CARD = "pv-top-card"

    def __init__(
        self,
        driver: Chrome = None,
        linkedin_url: str = None,
        extract_educations: bool = False,
        extract_skills: bool = False,
    ):
        super().__init__(driver)
        self.linkedin_url = linkedin_url
        self.person = Person(linkedin_url=linkedin_url)
        self.extract_educations = extract_educations
        self.extract_skills = extract_skills

    def scroll_to_half(self):
        self.driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));"
        )

    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def scroll_class_name_element_to_page_percent(
        self, class_name: str, page_percent: float
    ):
        self.driver.execute_script(
            f'elem = document.getElementsByClassName("{class_name}")[0]; elem.scrollTo(0, elem.scrollHeight*{str(page_percent)});'
        )

    def __find_element_by_class_name__(self, class_name):
        try:
            self.driver.find_element(By.CLASS_NAME, class_name)
            return True
        except:
            pass
        return False

    def __find_element_by_xpath__(self, tag_name):
        try:
            self.driver.find_element(By.XPATH, tag_name)
            return True
        except:
            pass
        return False

    def __find_enabled_element_by_xpath__(self, tag_name):
        try:
            elem = self.driver.find_element(By.XPATH, tag_name)
            return elem.is_enabled()
        except:
            pass
        return False

    @classmethod
    def __find_first_available_element__(cls, *args):
        for elem in args:
            if elem:
                return elem[0]

    def scrape(self, close_on_complete=True):
        if self.is_signed_in():
            self.driver.get(self.linkedin_url)
            self.scrape_logged_in(close_on_complete=close_on_complete)
        else:
            raise Exception("you are not logged in!")

    def scrape_logged_in(self, close_on_complete=True):
        driver = self.driver
        WebDriverWait(driver, self.WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.presence_of_element_located(
                (
                    By.TAG_NAME,
                    self.__TOP_CARD,
                )
            )
        )
        self.focus()
        self.wait(5)

        # get name and location
        self.get_name_and_location()
        self.person.open_to_work = self.is_open_to_work()
        self.get_about()
        self.reposition_on_screen()
        # get experience
        self.get_experiences()
        if self.extract_educations:
            self.get_educations()
        if self.extract_skills:
            self.get_skills()

    def get_name_and_location(self):
        top_panel = self.driver.find_element(By.XPATH, "//*[@class='mt2 relative']")
        person = self.person
        person.name = top_panel.find_element(By.TAG_NAME, "h1").text
        person.location = top_panel.find_element(
            By.XPATH, "//*[@class='text-body-small inline t-black--light break-words']"
        ).text
        person.headline = top_panel.find_element(
            By.CSS_SELECTOR, ".ph5 .text-body-medium.break-words"
        ).text

    def is_open_to_work(self):
        try:
            return "#OPEN_TO_WORK" in self.driver.find_element(
                By.CLASS_NAME, "pv-top-card-profile-picture"
            ).find_element(By.TAG_NAME, "img").get_attribute("title")
        except:
            return False

    def get_about(self):
        person = self.person
        try:
            person.about = (
                self.driver.find_element(By.ID, "about")
                .find_element(By.XPATH, "..")
                .find_element(By.CLASS_NAME, "display-flex")
                .text
            )
        except NoSuchElementException:
            person.about = ""

    def reposition_on_screen(self):
        self.driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));"
        )
        self.driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/1.5));"
        )

    def get_experiences(self):
        url = f"{self.linkedin_url}/details/experience"
        self.driver.get(url)
        self.focus()
        main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
        self.scroll_to_half()
        self.scroll_to_bottom()
        main_list = self.wait_for_element_to_load(name="pvs-list__container", base=main)
        try:
            for position in main_list.find_elements(
                By.CLASS_NAME, "pvs-list__paged-list-item"
            ):
                position = position.find_element(
                    By.CSS_SELECTOR, "div[data-view-name='profile-component-entity']"
                )
                profile_component_elems = position.find_elements(By.XPATH, "*")
                if len(profile_component_elems) < 2:
                    continue
                company_logo_elem = profile_component_elems[0]
                position_details = profile_component_elems[1]

                # company elem
                company_linkedin_url = company_logo_elem.find_element(
                    By.XPATH, "*"
                ).get_attribute("href")
                if not company_linkedin_url:
                    continue

                # position details
                position_details_list = position_details.find_elements(By.XPATH, "*")
                position_summary_details = (
                    position_details_list[0] if len(position_details_list) > 0 else None
                )
                position_summary_text = (
                    position_details_list[1] if len(position_details_list) > 1 else None
                )
                outer_positions = position_summary_details.find_element(
                    By.XPATH, "*"
                ).find_elements(By.XPATH, "*")

                if len(outer_positions) == 4:
                    position_title = (
                        outer_positions[0].find_element(By.TAG_NAME, "span").text
                    )
                    company = outer_positions[1].find_element(By.TAG_NAME, "span").text
                    work_times = (
                        outer_positions[2].find_element(By.TAG_NAME, "span").text
                    )
                    location = outer_positions[3].find_element(By.TAG_NAME, "span").text
                elif len(outer_positions) == 3:
                    if "·" in outer_positions[2].text:
                        position_title = (
                            outer_positions[0].find_element(By.TAG_NAME, "span").text
                        )
                        company = (
                            outer_positions[1].find_element(By.TAG_NAME, "span").text
                        )
                        work_times = (
                            outer_positions[2].find_element(By.TAG_NAME, "span").text
                        )
                        location = ""
                    else:
                        position_title = ""
                        company = (
                            outer_positions[0].find_element(By.TAG_NAME, "span").text
                        )
                        work_times = (
                            outer_positions[1].find_element(By.TAG_NAME, "span").text
                        )
                        location = (
                            outer_positions[2].find_element(By.TAG_NAME, "span").text
                        )
                else:
                    position_title = ""
                    company = outer_positions[0].find_element(By.TAG_NAME, "span").text
                    work_times = ""
                    location = ""

                times = work_times.split("·")[0].strip() if work_times else ""
                duration = (
                    work_times.split("·")[1].strip()
                    if len(work_times.split("·")) > 1
                    else None
                )

                from_date = " ".join(times.split(" ")[:2]) if times else ""
                to_date = " ".join(times.split(" ")[3:]) if times else ""
                if position_summary_text and any(
                    element.get_attribute("pvs-list__container")
                    for element in position_summary_text.find_elements(By.TAG_NAME, "*")
                ):
                    inner_positions = (
                        position_summary_text.find_element(
                            By.CLASS_NAME, "pvs-list__container"
                        )
                        .find_element(By.XPATH, "*")
                        .find_element(By.XPATH, "*")
                        .find_element(By.XPATH, "*")
                        .find_elements(By.CLASS_NAME, "pvs-list__paged-list-item")
                    )
                else:
                    inner_positions = []
                if len(inner_positions) > 1:
                    descriptions = inner_positions
                    for description in descriptions:
                        res = description.find_element(By.TAG_NAME, "a").find_elements(
                            By.XPATH, "*"
                        )
                        position_title_elem = res[0] if len(res) > 0 else None
                        work_times_elem = res[1] if len(res) > 1 else None
                        location_elem = res[2] if len(res) > 2 else None

                        location = (
                            location_elem.find_element(By.XPATH, "*").text
                            if location_elem
                            else None
                        )
                        position_title = (
                            position_title_elem.find_element(By.XPATH, "*")
                            .find_element(By.TAG_NAME, "*")
                            .text
                            if position_title_elem
                            else ""
                        )
                        work_times = (
                            work_times_elem.find_element(By.XPATH, "*").text
                            if work_times_elem
                            else ""
                        )
                        times = work_times.split("·")[0].strip() if work_times else ""
                        duration = (
                            work_times.split("·")[1].strip()
                            if len(work_times.split("·")) > 1
                            else None
                        )
                        from_date = " ".join(times.split(" ")[:2]) if times else ""
                        to_date = " ".join(times.split(" ")[3:]) if times else ""

                        experience = Experience(
                            position_title=position_title,
                            from_date=from_date,
                            to_date=to_date,
                            duration=duration,
                            location=location,
                            description=description,
                            institution_name=company,
                            linkedin_url=company_linkedin_url,
                        )
                        self.person.add_experience(experience)
                else:
                    description = (
                        position_summary_text.text if position_summary_text else ""
                    )

                    experience = Experience(
                        position_title=position_title,
                        from_date=from_date,
                        to_date=to_date,
                        duration=duration,
                        location=location,
                        description=description,
                        institution_name=company,
                        linkedin_url=company_linkedin_url,
                    )
                    self.person.add_experience(experience)
        except Exception as e:
            logger.error(f"Error getting experiences: {e}")

    def _extract_multiple_positions(
        self, position: WebElement
    ) -> tuple[WebElement, WebElement]:
        position_elements = position.find_elements(By.XPATH, "*")
        logo = position_elements[0] if len(position_elements) > 0 else None
        details = position_elements[1] if len(position_elements) > 1 else None
        return logo, details

    def get_educations(self):
        try:
            self._get_educations()
        except Exception as e:
            logger.error(f"Error getting educations: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def _get_educations(self) -> None:
        url = f"{self.linkedin_url}/details/education"
        self.driver.get(url)
        self.focus()
        main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
        self.scroll_to_half()
        self.scroll_to_bottom()
        self.wait(3)
        main_list = self.wait_for_element_to_load(name="pvs-list__container", base=main)
        for position in main_list.find_elements(
            By.CLASS_NAME, "pvs-list__paged-list-item"
        ):
            position = position.find_element(
                By.XPATH, "//div[@data-view-name='profile-component-entity']"
            )
            institution_logo_elem, position_details = self._extract_multiple_positions(
                position
            )
            if not institution_logo_elem or not position_details:
                continue

            # company elem
            institution_linkedin_url = institution_logo_elem.find_element(
                By.XPATH, "*"
            ).get_attribute("href")

            # position details
            position_details_list = position_details.find_elements(By.XPATH, "*")
            position_summary_details = (
                position_details_list[0] if len(position_details_list) > 0 else None
            )
            position_summary_text = (
                position_details_list[1] if len(position_details_list) > 1 else None
            )
            outer_positions = position_summary_details.find_element(
                By.XPATH, "*"
            ).find_elements(By.XPATH, "*")

            institution_name = outer_positions[0].find_element(By.TAG_NAME, "span").text
            if len(outer_positions) > 1:
                degree = outer_positions[1].find_element(By.TAG_NAME, "span").text
            else:
                degree = None

            if len(outer_positions) > 2:
                times = outer_positions[2].find_element(By.TAG_NAME, "span").text

                if times != "":
                    from_date = (
                        times.split(" ")[times.split(" ").index("-") - 1]
                        if len(times.split(" ")) > 3
                        else times.split(" ")[0]
                    )
                    to_date = times.split(" ")[-1]
            else:
                from_date = None
                to_date = None

            description = position_summary_text.text if position_summary_text else ""

            education = Education(
                start=convert_linkedin_date(from_date),
                end=convert_linkedin_date(to_date),
                description=description,
                degree=degree,
                institution_name=institution_name,
                linkedin_url=institution_linkedin_url,
            )
            self.person.add_education(education)

    def get_skills(self):
        try:
            url = f"{self.linkedin_url}/details/skills"
            self.driver.get(url)
            self.focus()
            main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
            self.scroll_to_half()
            self.scroll_to_bottom()
            main_list = self.wait_for_element_to_load(
                name="pvs-list__container", base=main
            )
            for position in main_list.find_elements(
                By.CSS_SELECTOR, "a[data-field=skill_page_skill_topic]"
            ):
                position = position.find_element(By.CLASS_NAME, "hoverable-link-text")
                self.person.add_skill(position.find_element(By.XPATH, "*").text)
        except Exception as e:
            logger.error(f"Error getting skills: {e}")
