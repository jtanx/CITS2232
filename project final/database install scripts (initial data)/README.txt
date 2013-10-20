This file contains the SQL commands necessary to insert the test values into
the database, *assuming* that the users are already present.

Users have not been included in this install script as this application is
dependent on the Django framework, and uses the in-built User model, so it
would not make much sense to include this here.

It should be noted that all this initial data is already installed when 
syncdb is called via Django's fixtures, so this is only necessary if you
wish to manually insert this data into the database.

As this init script assumes the presence of installed triggers, the order
of execution of the insert statements *is* important.