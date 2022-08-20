LectioScraper
-----------------
LectioScraper is a python package for helping you scrape lectio.dk with ease. It uses requests for the actual scraping and beautifulsoup for parsing the html. Scraping lectio.dk can be a tedious task, as it requires so much different html elements to be parsed. and lectio is a big website so there are a lot of different pages to scrape. Here you have everything configured and all you need to do is to import lectioscraper and start scraping (see the whole documentation below).

Installation
-----------------
You can install the latest version of lectioScraper with the pip command:

.. create a code block with the following code: pip install lectioScraper
.. code-block:: python
    :caption: How to install the latest stable version of lectioScraper

    pip install lectioscraper
    
    

and for installing a specific version you can use the version command:

::
    pip install lectioscraper==version

Usage
-----------------

.. Automodule:: lectioscraper.Lectio
    :members: __init__, getSchedule, getAbsence, getAllHomework

-----------------

LectioScraper is developed and maintained by Emil Tovborg-Jensen

License
-----------------

LectioScraper is released under the GNU General Public License v3.0. You can find a copy of the license in the LICENSE file or at:
`<https://www.gnu.org/licenses/gpl-3.0.html>`_.

