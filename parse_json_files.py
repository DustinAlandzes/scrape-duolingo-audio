import json
import logging
import os
from typing import List

import requests
from requests import HTTPError

DATA_DIR = "./data"  # change to json dir, move to settings.py
AUDIO_DIR = "./audio"

logging.basicConfig(filename='info.log', level=logging.INFO)

def load_files() -> List[dict]:
    tmp = []
    for json_file in os.listdir(DATA_DIR):
        with open(f"{DATA_DIR}/{json_file}", "r") as f:
            tmp.append(json.load(f))
    return tmp


def get_hint_text_and_audio(skill: dict) -> List[dict]:
    title = skill.get('title', '')
    logging.info(title)
    hints = []

    # resources to prefetch
    resourcesToPrefetch = skill.get('resourcesToPrefetch', [])
    for resource in resourcesToPrefetch:
        required = resource.get('required')
        type = resource.get('type')
        url = resource.get('url')

        if type != 'mp3':
            continue
        logging.info((required, type, url))

    # elements
    elements: List = skill.get('elements', [])
    for element in elements:
        # we only want elements that are of the type 'text'
        element_type: str = element.get('type', '')
        if element_type != 'text':
            continue

        # meta
        autoPlayableTTS: List = element.get('meta', {}).get('autoPlayableTTS', [])
        sectionIndex: int = element.get('meta', {}).get('sectionIndex')

        # element.hints
        hintLinks = element.get('element', {}).get('hints', {}).get('hintLinks', [])
        hints_hints = element.get('element', {}).get('hints', {}).get('hints', [])
        for link in hintLinks:
            index = link.get('index')
            rangeEnd = link.get('rangeEnd')
            rangeStart = link.get('rangeStart')
            logging.info((index, rangeEnd, rangeStart))

        # element.styledString
        text: str = element.get('element', {}).get('styledString', {}).get('text', '')
        styling = element.get('element', {}).get('styledString', {}).get('styledString', '')

        # element.tokenTTS
        tokenTTSCollection = element.get('element', {}).get('tokenTTS', {}).get('tokenTTSCollection', [])
        for tokenTTS in tokenTTSCollection:
            endIndex = tokenTTS.get('endIndex')
            startIndex = tokenTTS.get('startIndex')
            ttsURL = tokenTTS.get('ttsURL')
            logging.info((endIndex, startIndex, ttsURL, text[startIndex:endIndex], text[startIndex]))
            hints.append({
                # sometimes startIndex and endIndex are the same, meaning it's one character at that index
                'text': text[startIndex:endIndex] or text[startIndex],
                'ttsURL': ttsURL
            })
    return hints


if __name__ == "__main__":
    files = load_files()

    skills = {}

    for skill in files:
        hints = get_hint_text_and_audio(skill)
        for hint in hints:
            try:
                response = requests.get(hint.get('ttsURL'))
                response.raise_for_status()
                with open(f"{AUDIO_DIR}/{hint.get('text')}.mp3", "wb") as f:
                    f.write(response.content)
            except HTTPError as e:
                logging.error(f"{str(e)} from {hint}")
