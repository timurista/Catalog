# Catalog Website using Flask Server implemented in python
## How to Run

### Initialization
First you must install vagrant or another virtual system to run Postgres or psql.

After you have a virtual machine up and running, make sure to set up the database by typing the following and then hit enter:

    python data_base.py

Then (optionally) to populate the db with values type

    python init_database.py

If the database at any point becomes faulty, you can delete the "catalog.db" file and redue the above process to reset all values.

Finally, type the following to get the server up and running at localhost:8000/

    python application.py

Type "\q" to exit.

### Overview of the Catalog
The catalog initially display the latest items and the categories they blong to. Clicking on a category name will take the user to all the items in that category (with a list of price, description, title, picture and the user which created the item). A button on the top left will take the user to the latest items view again. To edit any category or catalog item, the user needs to sign in through the top right button which uses google account sign-in. Future updates will include facebook login as well. Once logged in, the user can add catalog items with pictures, update their own created content and add new items to different categories. 

Note: signed-in users can only edit their own content, and to prevent against cross site reference forgeries (csrf), websites which attempt to hijak users information and make url requests and posts, will be blocked and redirected using the flask extension SeaSurf. Hidden input items with nonce tokens are included with each form submission.


## What this code does
application.py -> runs the server on local host port 8000 or http://localhost:8000/ (NOTE: google sign-in is setup to work from this port, so keep it at 8000 only) 

database_setup.py -> configures a catalog.db file with the different tables and columns it needs to run.

init_database.py -> populates the database with 2 default users and a variety of items and categories created by those users

catalogapp_tests.py -> uses unittest framework to run tests on features such as decorators, etc., and if you uncomment the autocode fix section, python code is loaded and fixed to conorm to pep8 standards for better readability.

### Website urls
prefix the following with http://localhost:8000/ (if running locally) like so: http://localhost:8000/catalog

/catalog/ or / -> takes you to the latest items for display
/rss -> takes you to the rss feed for the latest items

all catalog item urls are composed in the following way: /category/<category name>/<catalog item>/<catalog id>

Example:
/category/Running/Saucony%20Men%20Cohesion%208%20Running%20Shoe/7 -> to display the item (public display)
/category/Running/Saucony%20Men%20Cohesion%208%20Running%20Shoe/edit/ -> will let you edit the item if you are logged in and have access to it

### Getting public JSON Files:
/category/Running/Saucony%20Men%20Cohesion%208%20Running%20Shoe/7/JSON -> will give you a public JSON object with the catalogItem
/category/Running/JSON -> will give you a JSON object with all catalog items in that category
/catalog/JSON -> will give you a JSON object with all catalog items

NOTE: Private JSON files
/users/JSON -> will give you a JSON object with all users if you have admin priveleges


