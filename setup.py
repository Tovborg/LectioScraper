from setuptools import setup, find_packages
import os
# git
with open('README.md') as readme_file:
    README = readme_file.read()

VERSION = '0.0.5.2'
DESCRIPTION = 'A simple python package to scrape useful data from Lectio.dk'

# Setting up
setup(
    name="lectioscraper",
    version=VERSION,
    author="Tovborg (Emil Tovborg-Jensen)",
    author_email="<emil@tovborg-jensen.dk>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=README,
    packages=find_packages(),
    license="GNU General Public License v3.0",
    url="https://github.com/Tovborg/LectioScraper",
    download_url="https://pypi.org/project/lectioscraper/",
    install_requires=['beautifulsoup4', 'requests', 'lxml', 'pytz'],
    keywords=['python', 'Lectio', 'Scraping', 'webscraping'],
)

