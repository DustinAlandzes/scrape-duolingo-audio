import json
import logging
import os
import random
from pathlib import Path
from typing import List

import genanki
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

        # element.styledString
        text: str = element.get('element', {}).get('styledString', {}).get('text', '')
        styling = element.get('element', {}).get('styledString', {}).get('styling', '')

        # element.hints
        hintLinks = element.get('element', {}).get('hints', {}).get('hintLinks', [])
        hints_hints = element.get('element', {}).get('hints', {}).get('hints', [])
        for link in hintLinks:
            index = link.get('index')
            rangeEnd = link.get('rangeEnd')
            rangeStart = link.get('rangeStart')
            logging.info((index, rangeEnd, rangeStart, text[rangeStart:rangeEnd + 1]))
            print(text[rangeStart:rangeEnd + 1], hints_hints[index])

        # element.tokenTTS
        tokenTTSCollection = element.get('element', {}).get('tokenTTS', {}).get('tokenTTSCollection', [])
        for tokenTTS in tokenTTSCollection:
            endIndex = tokenTTS.get('endIndex')
            startIndex = tokenTTS.get('startIndex')
            ttsURL = tokenTTS.get('ttsURL')
            logging.info((endIndex, startIndex, ttsURL, text[startIndex:endIndex + 1]))

            # find hint link with same start and end as this token
            for link in hintLinks:
                if link.get("rangeEnd") is endIndex and link.get("rangeStart") is startIndex:
                    index = link.get('index')
                    hint = hints_hints[index]
                    hints.append({
                        # sometimes startIndex and endIndex are the same, meaning it's one character at that index
                        'text': text[startIndex:endIndex + 1],
                        'hint': hint,
                        'ttsURL': ttsURL
                    })
    return hints


def create_deck():
    files = load_files()
    if not os.path.exists(AUDIO_DIR):
        os.mkdir(AUDIO_DIR)

    model_id = random.randrange(1 << 30, 1 << 31)
    model = genanki.Model(
        model_id,
        'Simple Model with Media',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
            {'name': 'AnswerSound'}
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Question}}<br>',
                'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}<br>{{AnswerSound}}',
            },
        ])

    deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), "Duolingo Mandrin Chinese")
    media_files = []
    for skill in files:

        hints: List = get_hint_text_and_audio(skill)
        for hint in hints:
            try:
                ttsURL = hint.get('ttsURL')
                hint_text = hint.get('text')
                hint_hint = hint.get('hint')

                # download audio
                response = requests.get(ttsURL)
                response.raise_for_status()

                # write audio to file
                file_name = f"{hint_text}.mp3"
                with open(file_name, "wb") as f:
                    f.write(response.content)

                # add audio file to media files list
                media_files.append(file_name)
                deck.add_note(genanki.Note(model=model,
                                           fields=[f"{hint_text}",
                                                   f"{hint_hint}",
                                                   f"[sound:{file_name}]"
                                                   ]))
                logging.info(f"Created note for {hint_text} / {hint_hint}.")
            except HTTPError as e:
                logging.error(f"Got {str(e)} from {hint}")

    package = genanki.Package(deck)
    package.media_files = media_files
    package.write_to_file('output.apkg')
    logging.info("Finished creating deck.")

    for p in Path(".").glob("*.mp3"):
        p.unlink()
    logging.info("Removed .mp3 files")


if __name__ == "__main__":
    create_deck()
