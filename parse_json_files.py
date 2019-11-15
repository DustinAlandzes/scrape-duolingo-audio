import json
import logging
import os
from typing import List

DATA_DIR = "./data"


def load_files() -> List[dict]:
    tmp = []
    for json_file in os.listdir(DATA_DIR):
        with open(f"{DATA_DIR}/{json_file}", "r") as f:
            tmp.append(json.load(f))
    return tmp


if __name__ == "__main__":
    files = load_files()

    skills = {}

    for file in files:
        title = file.get('title', '')
        logging.info(title)
        skills[title] = {}

        resourcesToPrefetch = file.get('resourcesToPrefetch', [])
        skills[title]['resources'] = []

        for resource in resourcesToPrefetch:
            required = resource.get('required')
            type = resource.get('type')
            url = resource.get('url')

            if type != 'mp3':
                continue

            skills[title]['resources'].append(resource)
            logging.info(required, type, url)

        elements = file.get('elements', [])
        for element in elements:
            element_type = element.get('type', '')
            if element_type != 'text':
                continue

            # meta
            autoPlayableTTS = element.get('meta', {}).get('autoPlayableTTS', [])
            sectionIndex = element.get('meta', {}).get('sectionIndex', 0)

            # element
            hintLinks = element.get('element', {}).get('hints', {}).get('hintLinks', [])
            hints = element.get('element', {}).get('hints', {}).get('hints', [])

            # element styledString
            text = element.get('element', {}).get('styledString', {}).get('text', '')
            styling = element.get('element', {}).get('styledString', {}).get('styledString', '')

            # element tokenTTS
            tokenTTSCollection = element.get('tokenTTS', {}).get('tokenTTSCollection', [])

            for link in hintLinks:
                index = link.get('index')
                rangeEnd = link.get('rangeEnd')
                rangeStart = link.get('rangeStart')
                logging.info(index, rangeEnd, rangeStart)
