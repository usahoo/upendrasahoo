#!/usr/bin/env python3

# This program connects to a database called catalog.
# It allows all users to view categories and authorized users
# can create, edit and delete items.
# Google oAuth is used to for authorization.
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    jsonify,
    url_for,
    flash
)

# from sqlalchemy import create_engine, asc, desc
from sqlalchemy import asc, desc
# from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
from flask_sqlalchemy import SQLAlchemy
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# load client_secret json data
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catalog.db'
db = SQLAlchemy(app)


@app.context_processor
def inject_dict_for_all_templates():
    """
    Injects username and user_id into all templates
    """
    if 'username' in login_session and 'user_id' in login_session:
        return dict(username=login_session['username'],
                    user_id=login_session['user_id'])
    else:
        return dict()


# handle login request
@app.route('/login')
def showLogin():
    """
    Shows login page with Google login button and provides an
    anti-forgery state token for added security
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# handle Google Connect request
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(str(h.request(url, 'GET')[1], encoding='utf-8'))

    print("gconnect response received")

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
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
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                                'Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Check if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; '
    output += 'height: 300px;border-radius:'
    output += '150px;-webkit-border-radius: '
    output += '150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s." % login_session['username'])
    print("done!")
    return output


# disconnect - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    """
    Used for logging out- revokes access token and removes user data
    from session
    """
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Show Home page
@app.route('/')
@app.route('/catalog')
def showCatalogHome():
    """
    Shows catalog home page with all categories and 10 most recent
    items
    """
    categories = db.session.query(Category).order_by(asc(Category.name))
    items = db.session.query(Item).order_by(desc(Item.id)).limit(10)
    return render_template('home.html',
                           categories=categories, items=items)


# Get catalog data as json
@app.route('/JSON/')
@app.route('/catalog/JSON/')
def showCatalogJson():
    """
    Returns JSON of all categories and their items
    """
    categoryList = []
    categories = db.session.query(Category).order_by(asc(Category.name))
    for category in categories:
        items = db.session.query(Item).\
                filter_by(category_id=category.id)

        itemList = []
        for item in items:
            itemList.append(item.serialize)

        categoryDict = {'id': category.id, 'name': category.name,
                        'items': itemList}
        categoryList.append(categoryDict)

    return jsonify(categoryList)


# Get catagory data
@app.route('/catalog/<string:category_name>/items/')
def showCategory(category_name):
    """
    Shows a chosen category page and its items
    """
    categories = db.session.query(Category).order_by(asc(Category.name))
    selectedCategory = db.session.query(Category).\
        filter_by(name=category_name).one()
    items = db.session.query(Item).\
        filter_by(category_id=selectedCategory.id).\
        order_by(desc(Item.id))
    return render_template('category.html', categories=categories,
                           selectedCategory=selectedCategory, items=items)


# Get catagory data as json
@app.route('/catalog/<string:category_name>/items/JSON/')
def showCategoryJson(category_name):
    """
    Shows JSON for a chosen category and its items
    """
    selectedCategory = db.session.query(Category).\
        filter_by(name=category_name).one()
    items = db.session.query(Item).\
        filter_by(category_id=selectedCategory.id)

    itemList = []
    for item in items:
        itemList.append(item.serialize)

    categoryDict = {'id': selectedCategory.id,
                    'name': selectedCategory.name, 'items': itemList}

    return jsonify(category=categoryDict)


# Get items for a category
@app.route('/catalog/<string:category_name>/<string:item_name>/')
def showItem(category_name, item_name):
    """
    Shows an item page with option to edit and delete if it was
    created by the logged in user
    """
    item, category = db.session.query(Item, Category).\
        filter(Item.category_id == Category.id).\
        filter(Category.name == category_name, Item.name == item_name).one()
    return render_template('item.html', item=item)


# Get item data as json for a category
@app.route('/catalog/<string:category_name>/<string:item_name>/JSON/')
def showItemJson(category_name, item_name):
    """
    Returns JSON for a chosen item
    """
    item, category = db.session.query(Item, Category).\
        filter(Item.category_id == Category.id).\
        filter(Category.name == category_name, Item.name == item_name).one()
    return jsonify(item=item.serialize)


# create a new catalog
@app.route('/catalog/item/new/', methods=['GET', 'POST'])
def addItem():
    """
    For GET request, shows form to add a new item. On POST
    request, will add a new item and then redirect to catalog
    home page. Requires user to be logged in or will redirect
    to login page.
    """
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        newItem = Item(name=request.form['itemName'],
                       description=request.form['description'],
                       category_id=request.form['category'],
                       user_id=login_session['user_id'])
        db.session.add(newItem)
        db.session.commit()
        flash('%s item created' % newItem.name)
        return redirect(url_for('showCatalogHome'))

    else:
        categories = db.session.query(Category).order_by(asc(Category.name))
        return render_template('newItem.html', categories=categories)


# edit an existing item
@app.route('/catalog/<string:category_name>/<string:item_name>/edit/',
           methods=['GET', 'POST'])
def editItem(category_name, item_name):
    """
    For GET request, shows form to edit an item. On POST
    request, will save edited item and then redirect to catalog
    home page. If user not logged in, will redirect to login
    page. If user is not creator of item, will send alert message
    that they are not authorized to edit item.
    """
    if 'username' not in login_session:
        return redirect('/login')
    editedItem, _ = db.session.query(Item, Category).\
        filter(Item.category_id == Category.id).\
        filter(Category.name == category_name, Item.name == item_name).one()
    if login_session['user_id'] != editedItem.user_id:
        return ("<script>function myFunction() " +
                "{alert('You are not authorized" +
                " to edit items you did not create.');}</script>" +
                "<body onload='myFunction()''>")
    if request.method == 'POST':
        if request.form['itemName']:
            editedItem.name = request.form['itemName']
        if request.form['description']:
            editedItem.description = request.form['description']
        db.session.add(editedItem)
        db.session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for('showCatalogHome'))
    else:
        return render_template('editItem.html', item=editedItem)


# delete an item
@app.route('/catalog/<string:category_name>/<string:item_name>/delete/',
           methods=['GET', 'POST'])
def deleteItem(category_name, item_name):
    """
    For GET request, shows button to confirm delete of an item. On
    POST request, will delete item and then redirect to catalog
    home page. If user not logged in, will redirect to login
    page. If user is not creator of item, will send alert message
    that they are not authorized to delete item.
    """
    if 'username' not in login_session:
        return redirect('/login')
    itemToDelete, _ = db.session.\
        query(Item, Category).\
        filter(Item.category_id == Category.id).\
        filter(Category.name == category_name, Item.name == item_name).one()
    if login_session['user_id'] != itemToDelete.user_id:
        return ("<script>function myFunction() {alert('You are not" +
                " authorized to delete items you did not create.');}" +
                "</script>" +
                "<body onload='myFunction()''>")
    if request.method == 'POST':
        db.session.delete(itemToDelete)
        db.session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('showCatalogHome'))
    else:
        return render_template('deleteItem.html', item=itemToDelete)


# Add a new user to database
def createUser(login_session):
    """
    Adds new user to database
    """
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    db.session.add(newUser)
    db.session.commit()
    user = db.session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Get user's info
def getUserInfo(user_id):
    """
    Gets user from database by id
    """
    user = db.session.query(User).filter_by(id=user_id).one()
    return user


# Get user's ID
def getUserID(email):
    """
    Gets user from database by email
    """
    try:
        user = db.session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        print('get user info from db failed')
        return None


# start the app
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
