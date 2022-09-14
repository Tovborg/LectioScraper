.. LectioScraper documentation master file, created by
   sphinx-quickstart on Fri Aug 19 23:17:27 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to LectioScraper's documentation!
=========================================


.. image:: twitter_header_photo_2.png
   :align: left

LectioScraper is a python package for helping you scrape lectio.dk with ease. It uses requests for the actual scraping and beautifulsoup for parsing the html. Scraping lectio.dk can be a tedious task, as it requires so much different html elements to be parsed. and lectio is a big website so there are a lot of different pages to scrape. Here you have everything configured and all you need to do is to import lectioscraper and start scraping (see the whole documentation below).



.. role:: raw-html(raw)
   :format: html


Getting help
==============
If you have any problems with the documentation or with the code, please feel free to contact me on my email, discord or open an issue on github. (see below).

e-mail: :raw-html:`<a href="mailto: emil@tovborg-jensen.dk">emil@tovborg-jensen.dk</a>`
:raw-html:`<br>`
discord: Tovborg#7914
:raw-html:`<br>`
github: :raw-html:`<a href="https://github.com/Tovborg/LectioScraper" target="_blank">Lectioscraper github</a>`


Quick start
============

You can install lectioscraper with pip:

.. code-block:: python

    pip install lectioscraper
   
and for installing a specific version using pip:

.. code-block:: python

      pip install lectioscraper==version

After installing lectioscraper you need to import the Lectio class and create an instance of the class with your login details

.. code-block:: python

   import lectioscraper

   client = lectioscraper.Lectio(username, password, schoolId)

   # after importing you can start scraping with the client object, see below for all functions

   # Example:
   # Scrape all classes for the current week
   client.getSchedule(to_json=True)

When initializing the client you can pass the following arguments: username, password, and a so called schoolId that is found by going to your school's page on lectio.dk and looking at the url.

Example:

https://www.lectio.dk/lectio/59/default.aspx

here the schoolId is 59, the schoolid will always be after /lectio/ 

Usage
============

.. automodule:: lectioscraper.Lectio
   :members: __init__, getSchedule, getAbsence, getAllHomework, getAssignments, getTodaysSchedule, addToGoogleCalendar, getUnreadMessages


Authors
============

Lectioscraper is developed and maintained by Emil Tovborg-Jensen.

   :raw-html:`<a href="https://github.com/Tovborg?tab=repositories" target="_blank">Github: Tovborg</a>`

License
============

lectioscraper is licensed under the GNU General Public License v3.0. You are free to modify and distribute as long as you give credit to the original author.

You can find the full license text either in the LICENSE file or on the following link:

      :raw-html:`<a href="https://www.gnu.org/licenses/gpl-3.0.en.html" target="_blank">GNU General Public License v3.0</a>`
   
   



   



