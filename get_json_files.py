import logging
import os
import time
from typing import List

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver

logging.basicConfig(filename='info.log', level=logging.INFO)

DATA_DIR: str = 'data'


def login(browser: WebDriver, wait: WebDriverWait):
    username = os.environ['username']
    password = os.environ['password']

    # open the homepage
    browser.get("https://www.duolingo.com/")

    # wait until we see a skill
    login_button = wait.until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'I ALREADY HAVE AN ACCOUNT')]"))
    )

    # click the login button (it says "I ALREADY HAVE AN ACCOUNT")
    login_button.click()

    # type the username into the username field
    username_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Email or username']")))
    username_field.send_keys(username)

    # password into the password field
    password_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']")))
    password_field.send_keys(password)

    # having a problem with "Wrong Password" maybe because I'm clicking too fast
    time.sleep(1)

    # submit the form
    password_field.submit()


def get_list_of_skill_names(browser: WebDriver, wait: WebDriverWait) -> List[str]:
    # get a list of all the skill buttons
    skills: List[WebElement] = wait.until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[@data-test='skill']"))
    )

    # get list of each skill name
    skill_names: List[str] = []
    for skill in skills:
        name: str = skill.find_element_by_xpath("./div/div/div[2]").text
        color: str = skill.find_element_by_xpath("./div/div/div[2]/span").value_of_css_property('color')

        # don't click skills not yet unlocked
        if color == "rgb(153, 153, 153)":
            logging.info(f"Skipping {name} because it is locked!")
            continue

        logging.info(f"Found button for {name}")
        skill_names.append(name)

    return skill_names


def scrape_duolingo():
    options = Options()
    options.headless = True

    # using seleniumwire.webdriver so I can intercept the http requests sent from/to the javascript client
    browser = webdriver.Firefox(options=options, executable_path='./geckodriver')

    # the json files containing links to the audio files are all from cloudfront
    browser.scopes = [
        '.*cloudfront.*'
    ]

    wait = WebDriverWait(browser, 20)

    logging.info("Started webdriver.")

    try:
        login(browser, wait)
        skill_names = get_list_of_skill_names(browser, wait)
        logging.info(f"Got this list of skills: {skill_names}")

        # find each skill name, click the button, download the json data, go back, close the tooltip
        for skill in skill_names:
            # remove all the requests previous to this
            del browser.requests

            # find name, and the button is the first div two parents above it
            skill_button = wait.until(
                EC.presence_of_element_located((By.XPATH, f"//span[text()='{skill}']/../../div[1]")))
            skill_button.click()

            tips_button = wait.until(EC.presence_of_element_located((By.XPATH, "//img[@alt='Tips and notes']/..")))
            tips_button.click()

            # keeping this sleep here to wait for the request to complete
            # maybe there's some kind of wait in seleniumwire I can use
            # or use a while loop to keep checking browser.requests for the json
            time.sleep(2)

            # idea: add to redis queue?
            for r in browser.requests:
                if '.json' in r.path:
                    with open(f'{DATA_DIR}/{skill}.json', 'wb') as f:
                        f.write(r.response.body)

            logging.info(f"Got json for {skill}")
            # click back to the skill tree
            home_button = browser.find_element_by_xpath("//a[@href='/']")
            home_button.click()

            # click skill button again to get rid of tips tooltip
            skill_button = wait.until(
                EC.presence_of_element_located((By.XPATH, f"//span[text()='{skill}']/../../div[1]")))
            skill_button.click()
    except (NoSuchElementException, TimeoutException) as e:
        logging.error(e)
    finally:
        browser.close()


if __name__ == "__main__":
    scrape_duolingo()
