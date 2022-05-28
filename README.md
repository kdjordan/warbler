## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [Testing](#testing)

## General info
This is a Twitter clone called Warblerm where a user can sign up and create 'warbles'. User can also like other user's Warbles and follow other users. Full test suit is included which tests both views and models.

![](warbler.gif)

## Technologies
* HTML5
* CSS3
* Python3
* Flask
* Bcrypt
* Postgres
* SQLalchemy
* Jinja2
	
## Setup
To run this application run the following commands :

```
$ git clone https://github.com/kdjordan/warbler
$ cd into directory
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ flask run

-- Then open 127.0.0.1:5000 in a browser
```
## Testing  
To test this application run the following commands :  
```
$ python -m unittest test_user_model.py
$ python -m unittest test_message_model.py
$ FLASK_ENV=production python -m unittest test_message_views.py
$ FLASK_ENV=production python -m unittest test_user_views.py
```
