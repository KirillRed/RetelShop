## Introduction
---
RetelShop is a new online shop developed by me. It is my training website, so it is not intended to be used in the real world. Feel free to share your ideas and suggestions on how to improve it. This repository only contains the website's **backend**, so you will need to use special software like Postman to test it.
## Getting started
---
First, download Python 3.8 or higher (note that Python 3.7 or less will not work) on this [link](https://www.python.org "python").  

Download the code and then navigate to the folder in your terminal.

Run the following command to download the requirements:
```
pip install -r requirements.txt
```
Migrate the database (migrations are already in the repository):
```
python manage.py migrate
```
Run the server and enjoy the website:
```
python manage.py runserver
```
## Technologies and features
---
The website is developed in [django](https://www.djangoproject.com "django"). I also use the [django rest framework](https://www.django-rest-framework.org "django rest framework") for APIs. There is a chat written via [django channels](https://channels.readthedocs.io/en/stable/introduction.html "django channels") and a chatbot written via  [chatterbot](https://chatterbot.readthedocs.io/en/stable/, "chatterbot"). And, of course, there are shop features like a list of comparisons, a cart, and a wish list.
