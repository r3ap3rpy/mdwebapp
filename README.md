# Welcome to Mardown Renderer

This is a python based webapp which works from folders and renders the markdown files in the folders to the page.

In order to use it install 2 modules.

```bash
pip install flask
pip install Flask-BasicAuth
```

The username is ***user*** and password is ***start!123***

You can create new folders and upload new markdowns to those folders.

You can simply use it by issuing the following commands:

```bash
git clone https://github.com/r3ap3rpy/mdwebapp
cd mdwebapp
virtualenv webappenv
webappenv\scripts\activate
pip install -r requirements.txt
python MDWebApp.py
```