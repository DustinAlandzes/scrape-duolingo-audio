# Scraping audio from duolingo with Selenium

Using the mandarin chinese course to test this. Haven't tried on others

## usage
##### setup environment and install dependencies
```bash
git clone ...
cd ...
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

##### download geckodriver and put in directory
* You can download the version for your OS here: https://github.com/mozilla/geckodriver/releases

##### set username and password environment variables and run get_json_files.py
```bash
export username=dustin
export password=secretpass
python get_json_files.py
```

#### run parse_json_files.py
```bash
python parse_json_files.py
```

## todo
* automatically create data folder if it doesn't exist
* exception handling, close browser on exception
* match audio links to words/phrases
* download audio
* create anki deck with genanki
* setup dockerfile and make headless