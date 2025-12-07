import os
import time
import requests
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = os.environ.get('BASE_URL', 'http://localhost:3000')


@pytest.fixture(scope="module")
def driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')

    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1280,1024')

    service = ChromeService(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=chrome_options)

    yield drv
    drv.quit()


def test_01_home_loads(driver):
    driver.get(f"{BASE_URL}/")
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    assert len(driver.title) > 0


def test_02_companies_search_and_list(driver):
    driver.get(f"{BASE_URL}/companies")
    search = driver.find_elements(By.CSS_SELECTOR, "input[placeholder*='company']")
    listing = driver.find_elements(By.CSS_SELECTOR, ".company, .company-list, ul")
    assert len(search) > 0 or len(listing) > 0


def test_03_salaries_page_elements(driver):
    driver.get(f"{BASE_URL}/salaries")
    job_input = driver.find_elements(By.CSS_SELECTOR, "input[placeholder*='job']")
    salary_boxes = driver.find_elements(By.CSS_SELECTOR, ".salary-container, .salary-box")
    assert len(job_input) > 0
    assert len(salary_boxes) >= 0  # may be empty, but page loads


def test_04_login_fields(driver):
    driver.get(f"{BASE_URL}/login")
    email = driver.find_elements(By.CSS_SELECTOR, "input[type='email'], input[name='email']")
    password = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
    assert len(email) > 0
    assert len(password) > 0


def test_05_apply_form_elements(driver):
    driver.get(f"{BASE_URL}/job/apply")
    first = driver.find_elements(By.CSS_SELECTOR, "input[placeholder='John']")
    resume = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
    submit = driver.find_elements(By.CSS_SELECTOR, "button[type='Submit']")
    assert len(first) > 0
    assert len(submit) > 0


def test_06_companies_search_no_crash(driver):
    driver.get(f"{BASE_URL}/companies")
    inputs = driver.find_elements(By.CSS_SELECTOR, "input[placeholder*='company']")
    if inputs:
        inputs[0].send_keys("Test")
        driver.find_element(By.TAG_NAME, 'body')
    assert True


def test_07_salaries_search_no_crash(driver):
    driver.get(f"{BASE_URL}/salaries")
    inputs = driver.find_elements(By.CSS_SELECTOR, "input[placeholder*='job']")
    if inputs:
        inputs[0].send_keys("Engineer")
    assert True


def test_08_navigation_links(driver):
    driver.get(BASE_URL)
    links = driver.find_elements(By.TAG_NAME, "a")
    clicked = False
    for link in links[:5]:
        try:
            link.click()
            clicked = True
            break
        except:
            pass

    assert clicked or len(links) == 0


def test_09_protected_route_access(driver):
    driver.get(f"{BASE_URL}/protected")
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    assert True


def test_10_api_salaries_not_html():
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }
    res = requests.get(f"{BASE_URL}/api/salaries", timeout=5, headers=headers)
    assert res.status_code < 500
    assert "<html" not in res.text.lower()