#!/usr/bin/python


"""
flaskyelp

A simple yelp application using flask.
More information: http://github.com/juli1/flaskyelp

:copyright: (c) Julien Delange
"""

import os
import sqlite3
from flask import Flask, render_template, request, session, g, redirect, flash, url_for
from werkzeug import check_password_hash, generate_password_hash

app = Flask (__name__)
app.config.from_object (__name__)
app.config.update (dict(
    DATABASE=os.path.join(app.root_path, 'flaskyelp.db'),
    SECRET_KEY="my development key"
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def get_db():
    """
    Open a connection with the sqlite3 driver.
    See http://flask.pocoo.org/docs/0.11/patterns/sqlite3/ for more info.
    """
    db = getattr(g, 'database', None)
    if db is None:
        db = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
        g.database = db
    return db

def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv


def get_place_by_id(id):
    """Convenience method to look up the id for a username."""
    rv = query_db('select * from places where place_id = ?',
                  [id])
    return rv[0] if rv else None

def get_user_id(username):
    """Convenience method to look up the id for a username."""
    rv = query_db('select user_id from users where username = ?',
                  [username], one=True)
    return rv[0] if rv else None

def init_db():
    print 'Initialize the database ...'
    db = get_db()
    with app.open_resource ('dbschema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    print 'Database initialization done'

@app.before_request
def before_request():
    """ Before the request, we check is the user is logged """
    g.is_logged = False
    if 'user_id' in session:
        g.user_id = session['user_id']
        g.is_logged = True

    if 'username' in session:
        g.username = session['username']
    else:
        g.username = "Unknwon user"

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'database'):
        g.database.close()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database from the command line"""
    init_db()

@app.route('/')
@app.route('/index')
def index():
    """main page, display the last reviews and places"""
    last_places=query_db('''select * from places ORDER BY place_id DESC LIMIT 10''')
    last_reviews=query_db('''select places.name, places.place_id, review_id, title FROM reviews, places WHERE places.place_id=reviews.place_id ORDER BY review_id DESC LIMIT 10''')
    return render_template('main.html', places=last_places, reviews=last_reviews)



@app.route('/place/<id>')
def show_place(id):

    """Show the place which has the id as parameter """

    theplace = query_db('''select places.name, places.address, places.city, places.zipcode, places.place_id AS pid, AVG(rating) AS avgrating from places, reviews WHERE places.place_id=? AND reviews.place_id=places.place_id''', [id], one=True)
    reviews = query_db('''select * from reviews WHERE place_id=?''', id)
    return render_template('place.html', pid=theplace['pid'] , place=theplace, reviews=reviews)


@app.route('/place/<id>/comment/new', methods=['POST','GET'])
def newcomment(id):
    """Add a new comment for the restaurant which has the id as parameter """

    if g.is_logged == False:
        flash ("You need to be logged in")
        return redirect(url_for('show_place', id=id))

    if request.method == 'POST':
        rating = request.form['rating']

        if rating.isdigit() == False:
            flash ("Rating must be between a number between 0 and 5 (inclusive)")
        elif int(rating) < 0 or int(rating) > 5:
            flash ("Rating must be between 0 and 5 (inclusive)")
        else:
            db = get_db()
            db.execute('''insert into reviews (rating, title, message, user_id, place_id) values (?, ?, ?,?,?)''', [rating, request.form['title'], request.form['content'], g.user_id, id])
            db.commit()

            flash('Your comment was successfully added')
    return redirect(url_for('show_place', id=id))


@app.route('/place/<id>/comment/<cid>/delete', methods=['POST','GET'])
def comment_delete(id,cid):
    """Delete a comment """

    if g.is_logged == False:
        flash ("You need to be logged in")
        return redirect(url_for('show_place', id=id))

    if request.method == 'GET':
        db = get_db()
        db.execute('''delete from reviews where user_id=? AND place_id=? AND review_id=?''', [g.user_id, id, cid])
        db.commit()

        flash('Review deleted')
    return redirect(url_for('show_place', id=id))


@app.route('/account')
def account():
    """View account with all reviews"""
    my_reviews=query_db('''select places.name, places.place_id, review_id, title FROM reviews, places WHERE places.place_id=reviews.place_id AND reviews.user_id=? ORDER BY review_id''', [g.user_id])
    return render_template('account.html', reviews=my_reviews)


@app.route('/place/new', methods=['GET', 'POST'])
def place_new():
    """Add a new place in the database"""
    if g.is_logged == False:
        flash ("You need to be logged in")
        return redirect(url_for('index'))

    if request.method == 'POST':
        db = get_db()
        db.execute('''insert into places (name, address, city, zipcode) values (?, ?, ?, ?)''', [request.form['name'], request.form['address'], request.form['city'], request.form['zipcode']])
        db.commit()

        flash('The restaurant was succesfully added')
        return redirect(url_for('index'))
    else:

        return render_template('newplace.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user"""
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif get_user_id(request.form['username']) is not None:
            error = 'The username is already taken'
        else:
            db = get_db()
            db.execute('''insert into users (
              username, email, password) values (?, ?, ?)''',
              [request.form['username'], request.form['email'],
               generate_password_hash(request.form['password'])])
            db.commit()
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)



@app.route('/logout')
def logout():
    """Logout and remove the active session"""
    session.pop('username', None)
    session.pop('user_id', None)
    flash ("You are logged out")
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login and fill the user session"""
    error = None
    if request.method == 'POST':
        user = query_db('''select * from users where
            username = ?''', [request.form['username']], one=True)
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user['password'],
                                     request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            return redirect(url_for('index'))
    return render_template('login.html', error=error)
