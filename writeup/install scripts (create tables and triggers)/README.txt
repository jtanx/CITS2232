create_tables.sql contains the install scripts for the tables of this
application only.

It does NOT contain the install scripts for the User relation, as the application
uses Django's User model. 

These scripts are provided for reference only - triggers for the application
are installed via a hook into the post_syncdb signal (see models.py), because
of a limitation of Django's SQL parser. 