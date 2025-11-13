import getpass
import logging

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)


VERIFY_LOGIN_ID = "global-nav__primary-link"
REMEMBER_PROMPT = "remember-me-prompt__form-primary"


def __prompt_email_password():
    u = input("Email: ")
    p = getpass.getpass(prompt="Password: ")
    return (u, p)


def page_has_loaded(driver: webdriver.Chrome) -> bool:
    page_state = driver.execute_script("return document.readyState;")
    return page_state == "complete"


def login(driver: webdriver.Chrome, email=None, password=None, cookie=None, timeout=10):
    if cookie is not None:
        return _login_with_cookie(driver, cookie)

    if not email or not password:
        email, password = __prompt_email_password()

    driver.get("https://www.linkedin.com/login")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

    email_elem = driver.find_element(By.ID, "username")
    email_elem.send_keys(email)

    password_elem = driver.find_element(By.ID, "password")
    password_elem.send_keys(password)

    try:
        remember = driver.find_element(By.CSS_SELECTOR, "label[for='rememberMeOptIn-checkbox']")
        if remember:
            remember.click()
    except Exception as e:
        logger.error(f"Failed to click remember me checkbox: {e}")

    password_elem.submit()

    if driver.current_url == "https://www.linkedin.com/checkpoint/lg/login-submit":
        remember = driver.find_element(By.ID, REMEMBER_PROMPT)
        if remember:
            remember.submit()

    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CLASS_NAME, VERIFY_LOGIN_ID))
    )


def _login_with_cookie(driver, cookie):
    driver.get("https://www.linkedin.com/login")
    driver.add_cookie({"name": "li_at", "value": cookie})
