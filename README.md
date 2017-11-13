# Item Catalog Project - The Shelf Life of Foods    
This project is a web application that will provide information about the shelf life of foods. Foods are divided into broad categories. Categories can be added/updated/deleted. Individual items (for example - apples, raw chicken, pasta, etc.) can be added/updated/deleted by category. 

All categories and items are visible to anyone. However, in order to update/delete a category, you must have been the creator (using OAuth and Google). In order to add/update/delete an item, you must have been the category creator. 

API endpoints are also provided in JSON format. 

## Getting Started
In order to get a copy of the project up and running on your local machine for development and testing please see the instructions below.

### Prerequisites
- Python 2.7.13 installed. To download - go to [Python.org](https://www.python.org/downloads/release/python-2713/).

- [Firefox](https://www.mozilla.org/en-US/firefox/new/) or [Google Chrome](https://www.google.com/chrome/browser/features.html?brand=CHBD&gclid=CjwKCAjw_dTMBRBHEiwApIzn_LkIhLMmU2yEU8pU-EfT_9fzVZ2YfH0S3Pk63j-6YulHZt-buUfuohoC7hIQAvD_BwE&dclid=CImvofPc3tUCFRfdYgodupMCzw) browser installed.

- Virtual machine (if using) configured. See this [Vagrantfile](correct url) for use.

- SQLite.

- Google account.

### Installing
Download [Item Catalog - The Shelf Life of Foods](https://github.com/doobieroo/Item-Catalog).

## Unit Testing
To test this code, ensure you are connected to the virtual machine, then from a console window (like Git Bash) run shelflife.py from the vagrant directory (or shared virtual machine directory).

Next, pull up a web browser and navigate to http://localhost:8000. From there you will be able to see both the public (read-only) views and if you login (using your Google account) - you'll see the add/update/delete views.

## API endpoints
Three different API endpoints are provided in JSON format. They are:

1. List of all categories
Request: http://localhost:8000/categories/JSON

2. All items from a specific category
Request: http://localhost:8000/category/CATEGORY_ID/JSON

3. One specific item from one specific category
Request: http://localhost:8000/category/CATEGORY_ID/ITEM_ID/JSON

## License
This project is licensed under the GNU General Public License. See the [LICENSE.md](https://github.com/doobieroo/Item-Catalog/blob/master/LICENSE) for details.




