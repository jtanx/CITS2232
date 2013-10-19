This has been made using Django 1.5.2, with Python 2.

Installation:
* Delete unchained.db3, if present.
* Run: python manage.py syncdb
  --> Say 'no' to creating a superuser

To run the application:
python manage.py runserver


Folders:
unchained : django project settings
sportsrec : our app! (this django project only has one app so far)
static : All static stuff (styles, js etc) - stick in this folder.

Files:
initial_data.json: The fixtures that installs the test data. 
		   Order is important.
fixture_to_sql.py: Converts a fixture for our app into the relevant SQL
                   commands.
shell-idle.py: For ease of access to do stuff with django from IDLE
python2console.bat: Easy access to python2 console on windows.