import logging
import os
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver

logging.basicConfig(filename='info.log', level=logging.INFO)


def login(browser):
    username = os.environ['username']
    password = os.environ['password']

    # open the homepage
    browser.get("https://www.duolingo.com/")
    time.sleep(2)

    # click the login button (it says "I ALREADY HAVE AN ACCOUNT")
    try:
        login_button = browser.find_element_by_xpath("//a[contains(text(), 'I ALREADY HAVE AN ACCOUNT')]")
        login_button.click()
    except NoSuchElementException:
        logging.debug("Couldn't find login_button")
        browser.close()
        exit()

    time.sleep(2)

    # type the username into the username field
    username_field = browser.find_element_by_xpath("//input[@placeholder='Email or username']")
    username_field.send_keys(username)

    # password into the password field
    password_field = browser.find_element_by_xpath("//input[@placeholder='Password']")
    password_field.send_keys(password)

    # submit the form
    password_field.submit()


def scrape_duolingo():
    # using seleniumwire.webdriver so I can get information from network tab in chrome
    browser = webdriver.Firefox(executable_path='./geckodriver')

    # the json files containing links to the audio files are all from cloudfront
    browser.scopes = [
        '.*cloudfront.*'
    ]

    login(browser)

    # wait until we see a tree-section
    try:
        WebDriverWait(browser, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-test='tree-section']"))
        )
    finally:
        print("hello")

    # get a list of all the skill buttons
    skills = browser.find_elements_by_xpath("//div[@data-test='skill']")

    # get list of each skill name
    skill_names = []
    for skill in skills:
        name = skill.find_element_by_xpath("./div/div/div[2]").text

        if name == 'Duo':
            color = skill.find_element_by_xpath("./div/div/div[2]/span").value_of_css_property('color')
            if color == "rgb(153, 153, 153)":
                logging.info(f"Skipping {name} because it is locked!")
                continue

        logging.info(f"Found button for {name}")
        skill_names.append(name)

    # find each skill name, click the button, download the json data, go back, close the tooltip
    for skill in skill_names:
        # remove all the requests previous to this
        del browser.requests

        # find name, and the button is the first div two parents above it
        skill_button = browser.find_element_by_xpath(f"//span[text()='{skill}']/../../div[1]")
        skill_button.click()
        time.sleep(2)

        tips_button = browser.find_element_by_xpath("//img[@alt='Tips and notes']/..")
        tips_button.click()
        time.sleep(2)

        for r in browser.requests:
            if '.json' in r.path:
                with open(f'{skill}.json', 'wb') as f:
                    f.write(r.response.body)

        # click back to the skill tree
        browser.find_element_by_xpath("//a[@href='/']").click()

        # click skill button again to get rid of tips tooltip
        skill_button = browser.find_element_by_xpath(f"//span[text()='{skill}']/../../div[1]")
        skill_button.click()

        time.sleep(2)

    browser.close()


if __name__ == "__main__":
    scrape_duolingo()
