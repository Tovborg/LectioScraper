from setuptools import setup, find_packages
import os
# git
with open('README.md') as readme_file:
    README = readme_file.read()

VERSION = '0.0.8.0'
DESCRIPTION = 'A simple python package to scrape useful data from Lectio.dk'

# Setting up
# find_packages() finds all the packages in the current directory s
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
    install_requires=['beautifulsoup4', 'requests', 'lxml', 'pytz', 'google-api-python-client', 'google-auth-httplib2', 'google-auth-oauthlib', 'oauth2client',  'google-auth-credentials'],
    # credentials.json is located in the lectioscraper directory with all the other python files for the package. It is not included in the package. include it
    package_data={'lectioscraper': ['credentials.json']},
    include_package_data=True,

    
    
    keywords=['python', 'Lectio', 'Scraping', 'webscraping'],
)

 