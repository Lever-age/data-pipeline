# Leverage Data Pipeline

Data scraping and cleaning for the Leverage project. This repository contains code that extracts campaign finance data from the Philadelphia Board of Ethics and ultimately stores it in a database. 

This currently uses Python 2.7. Sorry, SQLAlchemy wasn't working with version 3.

Easiest thing, for now, is to just create a MySQL database just like I did. Future versions will allow these to be changed in settings.

db name: pa_philly_campaign_finance
db user: finance_user
db pass: finance_pass
db host: localhost

Then source the database structure from pa_philly_campaign_finance.sql, load the requirements.txt file, and execute the import.py script.

###Cicero Import:

Set your environment variables. For instance, edit .bashrc for bash shell on *nix systems. 

export CICERO_USER='user'
export CICERO_PASS='pass'

SELECT * FROM `political_donation` WHERE donation_date >= '2017-01-01'

DELETE FROM `political_donation` WHERE donation_date >= '2017-01-01'

