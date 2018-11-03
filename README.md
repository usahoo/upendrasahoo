##Item Catalog Project
It is an item catalog that allows all users to view categories and items, and allows authorized users to create, edit and delete items. It uses Python 3, Flask and SQLAlchemy.

## How to download Item Catalog Project Source code
Copy itemCatalogProject.zip file to any of your device. You will need to unzip this file after downloading it under /home/vagrant/catalog directory. This zip file contains the following 15 files:

1. database_setup.py
2. mock_data.py
3. application.py
4. client_secrets.json
5. /static/styles.css
6. /static/catalogLogo.png
7. /templates/base.html
8. /templates/login.html
9. /templates/home.html
10. /templates/category.html
11. /templates/item.html
12. /templates/newItem.html
13. /templates/editItem.html
14. /templates/deleteItem.html
15. README.md

<br>
**Note:** You may need to modify **client_secrets.json** and **login.html** files with your Google oAuth client_id and client_secret to add/edit/delete a catalog item. However, you can view the catalog item without authenticate with your Google account.
If you need to create a client_id and client_secret, obtain OAuth 2.0 credentials from the **[Google API Console](https://console.developers.google.com/)**.

##How to run the program
- Install Linux-based **[virtual machine](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1)** and **[vagrant 1.8.5](https://www.vagrantup.com/)**.
If vagrant is successfully installed, you will able to see vagrant version by running <code>vagrant --version<code>.
- Install **[Git ssh client](https://git-scm.com/downloads)**
- Add C:\Program Files\Git\usr\bin to your PC PATH env variable
- Download the **[VM configuration](https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip)**
- After unzip the fsnd-virtual-machine.zip file, navigate to FSND-Virtual-Machine directory and then cd into vagrant directory.
- Run vagrant init
- Run vagrant up
- Run vagrant ssh
- cd catalog

```
If it is your first time running the project, create the database with:
python3 database_setup.py
```

```
You can add db records with given mock data, or you can create your own with: 
python3 mock_data.py
``` 

```
Start the application with:
python3 application.py
```

```
To login to the Catalog App, copy & paste the following url from your browser:
http://localhost:5000/login
Then, click on Google login button.
```

```
To logout, click on "Logout" button on top right corner.
```

```
To view categories and 10 most recent items:
http://localhost:5000/catalog
```

```
To get catalog data as JSON:
http://localhost:5000/JSON
or
http://localhost:5000/catalog/JSON
```

```
To get items for a category:
http://localhost:5000/catalog/category_name/items
```

```
To get items for a category as JSON:
http://localhost:5000/catalog/category_name/items/JSON
```

```
To view an item:
http://localhost:5000/catalog/category_name/item_name
```

```
To get item data as JSON:
http://localhost:5000/catalog/category_name/item_name/JSON
```

```
Form to create a new item (requires authentication):
http://localhost:5000/catalog/item/new/
```

```
Form to edit an item (requires authorization):
http://localhost:5000/catalog/category_name/item_name/edit 
```

```
Form to delete an item (requires authorization):
http://localhost:5000/catalog/category_name/item_name/delete 
```

<br>
## Please do write your feedback to:
**Upendra Sahoo** <us9452@att.com><br>
Currently pursuing a Nanodegree program with Udacity<br>

_Company: AT&T Inc._<br>
200 S. Laurel Ave.<br>
Room A4-4C09<br>
Middletown, NJ 07748<br>
(732) 420-8618 (Office), (732) 970-5163 (Cell)

## Licensing Information
Copyright 2018 AT&T - All rights reserved.
