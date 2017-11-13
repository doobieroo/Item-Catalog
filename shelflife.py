# ------------------------------------------------------
# ITEM CATALOG PROJECT
# ------------------------------------------------------
from flask import Flask, render_template, request, redirect
from flask import make_response, jsonify, url_for, flash
from flask import session as login_session

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from shelflife_models import Base, Category, Item, User

import random
import string
import httplib2
import json
import requests
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError


# Flask Instance
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']
APPLICATION_NAME = "Shelf Life App"

# Connect to Database and create database session
engine = create_engine('sqlite:///shelflife.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# ------------------------------------------------------
# LOGIN
# ------------------------------------------------------
# Create a state token to prevent request forgery.
# Store it in the session for later validation.
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# ------------------------------------------------------
# GOOGLE CONNECT
# ------------------------------------------------------
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain auth code
    code = request.data

    try:
        # Upgrade the auth code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the auth code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
           access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if the user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # See if user exists, if not create user
    user_id = getUserID(data['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style="width:150px;height:150px;border-radius:150px;'
    output += '-webkit-border-radius:150px;-moz-border-radius:150px;"> '

    flash('You are now logged in as %s' % login_session['username'])
    return output


# ------------------------------------------------------
# GOOGLE DISCONNECT
# ------------------------------------------------------
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user
    print('gdisconnect loop')
    access_token = login_session.get('access_token')
    print(access_token)
    if access_token is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print(result['status'])

    if result['status'] == '200':
        print('status was 200')
        # Reset the user's session
        del login_session['access_token']

        response = make_response(json.dumps('Successfully disconnected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    else:
        # For whatever reason, the given token was invalid
        response = make_response(json.dumps(
            'Failed to revoke token for given user'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# ------------------------------------------------------
# DISCONNECT BASED ON PROVIDER
# ------------------------------------------------------
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']

        flash('You have successfully been logged out.')
        return redirect(url_for('showCategories'))
    else:
        flash('You were not logged in to begin with.')
        return redirect(url_for('showCategories'))


# ------------------------------------------------------
# USER HELPER FUNCTIONS
# ------------------------------------------------------
# Get the user id for the session
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Get the user info based on the user id
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    print user_id
    return user


# Create a new user if there isn't one already there
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
        'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# ------------------------------------------------------
# JSON APIs to view Shelf Life Information
# ------------------------------------------------------
# View JSON info of all items from a specific category
@app.route('/category/<int:category_id>/JSON')
def categoryItemsJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(Items=[i.serialize for i in items])


# View JSON info of one specific item from one specific category
@app.route('/category/<int:category_id>/<int:item_id>/JSON')
def itemJSON(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)


# View JSON info of all categories
@app.route('/categories/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


# ------------------------------------------------------
# SHOW ALL CATEGORIES
# ------------------------------------------------------
@app.route('/')
@app.route('/categories/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name))

    # Check for logged in user
    if 'username' not in login_session:
        return render_template('publiccategories.html', categories=categories)
    else:
        return render_template('categories.html', categories=categories)


# ------------------------------------------------------
# CREATE NEW CATEGORY
# ------------------------------------------------------
@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    # Check for logged in user
    if 'username' not in login_session:
        return redirect('/login')

    if login_session['user_id'] == getUserID(login_session['email']):
        if request.method == 'POST':
            newCategory = Category(
                name=request.form['name'],
                user_id=login_session['user_id'])
            session.add(newCategory)
            flash('New Category %s Successfully Created' % newCategory.name)
            session.commit()
            return redirect(url_for('showCategories'))
        else:
            return render_template('newcategory.html')
    else:
        render_template('publiccategories.html')


# ------------------------------------------------------
# EDIT A CATEGORY
# ------------------------------------------------------
@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    editedCategory = session.query(Category).filter_by(id=category_id).one()

    # Check for logged in user
    if 'username' not in login_session:
        return redirect('/login')

    # Make sure user is the creator
    if editedCategory.user_id != login_session['user_id']:
        flash('You are not authorized to edit %s. \
            You must be the owner.' % editedCategory.name)
        return redirect(url_for('showCategories'))

    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            flash('Category Successfully Edited %s' % editedCategory.name)
            return redirect(url_for('showCategories'))
    else:
        return render_template('editcategory.html', category=editedCategory)


# ------------------------------------------------------
# DELETE A CATEGORY
# ------------------------------------------------------
@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    categoryToDelete = session.query(
        Category).filter_by(id=category_id).first()

    # Check for logged in user
    if 'username' not in login_session:
        return redirect('/login')

    # Make sure user is the creator
    if categoryToDelete.user_id != login_session['user_id']:
        flash('You are not authorized to delete %s. \
            You must be the owner.' % categoryToDelete.name)
        return redirect(url_for('showCategories'))

    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('%s Successfully Deleted' % categoryToDelete.name)
        session.commit()
        return redirect(url_for('showCategories', category_id=category_id))
    else:
        return render_template('deletecategory.html',
                               category=categoryToDelete)


# ------------------------------------------------------
# SHOW ALL ITEMS FOR A CATEGORY
# ------------------------------------------------------
@app.route('/category/<int:category_id>/')
def showCategoryItems(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    creator = getUserInfo(category.user_id)
    items = session.query(Item).filter_by(category_id=category_id).all()

    # Check for logged in user
    if 'username' not in login_session or \
       creator.id != login_session['user_id']:
            return render_template('publicitems.html', items=items,
                                   category=category, creator=creator)
    else:
        return render_template('items.html', items=items, category=category,
                               creator=creator)


# ------------------------------------------------------
# CREATE A NEW ITEM
# ------------------------------------------------------
@app.route('/category/<int:category_id>/new/', methods=['GET', 'POST'])
def newItem(category_id):
    category = session.query(Category).filter_by(id=category_id).one()

    # Check for logged in user
    if 'username' not in login_session:
        return redirect('/login')

    # Make sure the user is the creator of the category
    if category.user_id != login_session['user_id']:
        flash('You are not authorized to create an item. \
            You must be the owner of %s.' % category.name)
        return redirect(url_for('showCategoryItems', category_id=category_id))

    # If request is a post, prepare the db add + commit
    if request.method == 'POST':
        newItem = Item(name=request.form['name'], description=request.form[
                       'description'], category_id=category_id,
                       user_id=category.user_id)
        session.add(newItem)
        session.commit()
        flash('New %s Item Successfully Created' % newItem.name)
        return redirect(url_for('showCategoryItems', category_id=category_id))
    else:
        return render_template('newitem.html', category_id=category_id,
                               category=category)


# ------------------------------------------------------
# EDIT AN ITEM
# ------------------------------------------------------
@app.route('/category/<int:category_id>/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    editedItem = session.query(Item).filter_by(id=item_id).one()
    category = session.query(Category).filter_by(id=category_id).one()

    # Check for logged in user
    if 'username' not in login_session:
        return redirect('/login')

    # Make sure the user is the creator of the menu item
    if editedItem.user_id != login_session['user_id']:
        flash('You are not authorized to edit %s.' % editedItem.name)
        flash('You must be the owner of %s.' % category.name)
        return redirect(url_for('showCategoryItems', category_id=category_id))

    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']

        session.add(editedItem)
        session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for('showCategoryItems', category_id=category_id))
    else:
        return render_template('edititem.html', category_id=category_id,
                               item_id=item_id, item=editedItem)


# ------------------------------------------------------
# DELETE AN ITEM
# ------------------------------------------------------
@app.route('/category/<int:category_id>/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    category = session.query(Category).filter_by(id=category_id).one()
    itemToDelete = session.query(Item).filter_by(id=item_id).one()

    # Check for logged in user
    if 'username' not in login_session:
        return redirect('/login')

    # Make sure the user is the creator of the food item
    if category.user_id != login_session['user_id']:
        flash('You are not authorized to delete %s.' % itemToDelete.name)
        flash('You must be the owner of %s.' % category.name)
        return redirect(url_for('showCategoryItems', category_id=category_id))

    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('showCategoryItems', category_id=category.id))
    else:
        return render_template('deleteitem.html', item=itemToDelete,
                               category_id=category_id, item_id=item_id)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
