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

##### set username and password environment variables and run main.py
```bash
export username=dustin
export password=secretpass
python main.py
```

## todo
* replace time.sleep and try excepts with selenium waits
* parse tips for all skills
* download audio files, match to words/phrases
* create anki deck with genanki