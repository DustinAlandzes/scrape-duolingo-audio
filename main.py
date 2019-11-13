import logging
import os
import time

from selenium.common.exceptions import NoSuchElementException
# from selenium import webdriver
from seleniumwire import webdriver

"""
https://github.com/wkeeling/selenium-wire#proxies

how to download json file:

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:70.0) Gecko/20100101 Firefox/70.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Origin': 'https://www.duolingo.com',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Referer': 'https://www.duolingo.com/skill/zs/Greeting/tips',
}

response = requests.get('https://d1btvuu4dwu627.cloudfront.net/ca58939518de9a7c6033b248992e26c1/33f1d8ceebf80f5baa5ca305afdcd399/web/3/1.json', headers=headers)
"""

logging.basicConfig(filename='info.log', level=logging.INFO)


def scrape_duolingo():
    username = os.environ['username']
    password = os.environ['password']
    browser = webdriver.Firefox(executable_path='./geckodriver')
    browser.scopes = [
        '.*cloudfront.*'
    ]
    browser.get("https://www.duolingo.com/")
    time.sleep(2)

    try:
        login_button = browser.find_element_by_xpath("//a[contains(text(), 'I ALREADY HAVE AN ACCOUNT')]")
        login_button.click()
    except NoSuchElementException:
        logging.debug("Couldn't find login_button")
        browser.close()
        exit()

    time.sleep(2)

    # add try except or waits for these

    username_field = browser.find_element_by_xpath("//input[@placeholder='Email or username']")
    username_field.send_keys(username)

    password_field = browser.find_element_by_xpath("//input[@placeholder='Password']")
    password_field.send_keys(password)

    password_field.submit()

    time.sleep(5)

    buttons = []
    skill_tree = browser.find_elements_by_xpath("//div[@data-test='tree-section']")
    for section in skill_tree:
        skills = section.find_elements_by_xpath("./div/div")
        for skill in skills:
            button = skill.find_element_by_xpath("./div/div/div[1]")
            name = skill.find_element_by_xpath("./div/div/div/div/div[2]").text
            if name == 'Duo':
                if button.find_element_by_xpath("./div/div[1]/div/div/div").value_of_css_property(
                        'color') == "rgb(153, 153, 153)":
                    logging.info(f"Skipping {name} because it is locked!")
                    continue
            logging.info(f"Found button for {name}")
            buttons.append(button)

    del browser.requests
    buttons[0].click()
    browser.find_element_by_xpath("//img[@alt='Tips and notes']/..").click()

    time.sleep(2)

    for r in browser.requests:
        if '.json' in r.path:
            with open('test.json', 'wb') as f:
                f.write(r.response.body)


if __name__ == "__main__":
    scrape_duolingo()
