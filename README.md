flaskyelp
=========

First application to learn flask and feel less rusted about python programming.

# Configure!
1. Install flask
2. Export the name of your app using ```export FLASK_APP=flaskyelp```
3. Run flask for initializing your database ```python -m flask initdb```

If you have a tricky python environment, you can use virtualenv to install all the necessary dependencies.

```
virtualenv venv
. ./venv/bin/activate
pip install flask
python -m flask initdb
python -m flask run
```

# Run it!
1. Install flask (for example ```apt-get install python-flask```)
2. Export the name of your app using ```export FLASK_APP=flaskyelp```
3. Run flask for your app ```flask run``` or ```python -m flask run```

# Test it!
```
python setup.py test
```

# Debug & Feedback
E-mail at julien@gunnnm.org - git push request greatly appreciated!


# References
 * Flask: http://flask.pocoo.org
