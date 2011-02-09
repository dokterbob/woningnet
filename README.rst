Woningnet
=========

Django scraper for Woningnet

Usage
*****
1. Run prepare.sh to prepare environment, pull in dependencies and set up
   database and initial user.
2. Activate newly created environment::

       source env/bin/activate

3. Run the scraper::

       ./manage.py runjob woningnet_update

4. Behold the results from within the admin or from Django's databrowse
   application::

        ./manage.py runserver

5. Before each new scrape (for now) you will have to reset the database::

       ./manage.py reset woningscrape


