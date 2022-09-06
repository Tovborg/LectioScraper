
# LectioScraper

LectioScraper is a python package for helping you scrape lectio.dk with ease. It uses requests for the actual scraping and beautifulsoup for parsing the html. Scraping lectio.dk can be a tedious task, as it requires so much different html elements to be parsed. and lectio is a big website so there are a lot of different pages to scrape. Here you have everything configured and all you need to do is to import lectioscraper and start scraping (see the whole documentation below).


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install lectioscraper.

```bash
pip install lectioscraper
```

## Usage

```python
import lectioscraper

# Initializes the class
client = lectioscraper.Lectio("username", "password", "schoolId")

# returns your schedule for the day in a json format
client.getTodaysSchedule(to_json=True)

```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.



## Documentation
You can find the full documentation at [https://lectioscraper.readthedocs.io/en/latest/?](https://lectioscraper.readthedocs.io/en/latest/?) and it's strongly recommended as it's easy to read and gives you a good understanding at how to use this package
