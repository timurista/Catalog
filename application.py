from flask import Flask, render_template, request
from flask import redirect, url_for, flash, jsonify, abort
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CatalogItem, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# To prevent XSFR
from flask.ext.seasurf import SeaSurf

app = Flask(__name__)
csrf = SeaSurf(app)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Web App"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# TODO EXTRA: include cart item to track user additions
# TODO EXTRA: implement sign in with facebook
# TODO EXTRA: have sign in redirect locally, not login-page

# OAUTH

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
# TODO: implement facebook signin.. current not set up
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly
    # logout, let's strip out the information before the equals sign in our
    # token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
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
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

@csrf.exempt
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
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

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
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Authorization and Authentication helpers

def checkLogin():
    return (login_session and 'username' in login_session)

def checkLoginAndRedirect(url="/login"):
    if not checkLogin():
        abort(405)

def checkUserIsCorrectUser(editedItem):
    ''' check that the user who edited the item is the current user'''
    if 'user_id' in login_session:
        return editedItem.user_id != login_session['user_id']
    else:
        abort(405)


def check_duplicate(cat_name):
    ''' if name is found in categories already, return true '''
    return (session.query(Category).filter_by(name=cat_name).all())


def checkAndAbort(cat_name="", func=check_duplicate, error_code=441):
    ''' Raises forbidden error if user is trying to make duplicates'''
    if func(cat_name) or not len(cat_name):
        print "duplicate names should not be entered!"
        abort(403)

# decorator to handle security
import functools

# function tools to properly wrap decorator for flask
def checkAuthorization(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        checkLoginAndRedirect()
        return f(*args, **kwargs)
    return wrapped

# custom error handler pages

@app.errorhandler(405)
def must_be_logged_in(e):
    return redirect('/login')

@app.errorhandler(403)
def page_not_found(e):
    return render_template('unauthorized_access.html'), 403


# DISCONNECT - Revoke a current user's token and reset their login_session

@csrf.exempt
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    print 'access_token ',access_token

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    print result['status']

    if result['status'] == '200':
        # reset user's session
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        # response = make_response(json.dumps('disconnected.'), 200)
        # response.headers['Content-Type'] = 'application/json'
        flash('User successfully logged out!')
        return redirect('/latest')

    elif result['status'] != '200':
        # For whatever reason, the given token was invalid.
        print result['status']
        response = make_response(
            json.dumps('Failed to revoke token for given user. %s' 
                % result, 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# END OAUTH

# Making an API Endpoint (GET Request)
@app.route('/category/<cat_name>/JSON')
def categoryMenuJSON(cat_name):
    """
    categoryMenuJSON returns a json file with all objects in their categories
        args: String cat_name as name of category
    """
    category = session.query(Category).filter_by(name=cat_name).one()
    items = session.query(CatalogItem).filter_by(category=category).all()
    return jsonify(CategoryItems=[i.serialize for i in items])

# get all items in the catalog
@app.route('/catalog/JSON')
def catalogJSON():
    """ catalogJSON returns json file with all catalog items"""    
    items = session.query(CatalogItem).all()
    print "catalog"
    print jsonify(CatalogItems=[i.serialize for i in items])
    return jsonify(CatalogItems=[i.serialize for i in items])

# get all categories in the catalog
@app.route('/catalog/categories/JSON')
def categoriesJSON():
    """ categoriesJSON returns json file with all categories"""
    items = session.query(Category).all()
    print [i.serialize for i in items]
    print jsonify(Categories=[i.serialize for i in items])
    return jsonify(Categories=[i.serialize for i in items])

# get all users registered on this site
@app.route('/catalog/users/JSON')
def usersJSON():
    """ usersJSON returns json object with all users if admin user is logged in """
    #  check that user has admin property, else abort
    
    amdin_email = "timothy.urista@gmail.com"

    if amdin_email != login_session['email']:        
        abort(403)

    return jsonify(Users=[i.serialize for i in items])

# Get one Menu Item JSON

@app.route('/category/<cat_name>/<catalogItem>/<int:item_id>/JSON')
def categoryCatalogItemJSON(cat_name, catalogItem, item_id):
    """ categoryCatalogItemJSON returns json file for specific catalogItem """
    item = session.query(CatalogItem).filter_by(id=item_id).one()
    return jsonify(CatalogItem=item.serialize)


# Render RSS feed

@app.route('/catalog/RSS')
@app.route('/rss')
@app.route('/RSS')
def catalogRSS():
    """ catalogRSS renders rss feed of latest items in the catalog """
    items = session.query(CatalogItem).order_by(
        CatalogItem.timestamp.desc()).all()
    return render_template('rss.xml', items=items)


@app.route('/')
@app.route('/latest')
@app.route('/catalog')
def showCatalog():
    """
    showCatalog displays current items in the catalog for the user
    args:
        None
    """
    categories = session.query(Category).all()
    items = session.query(CatalogItem).order_by(
        CatalogItem.timestamp.desc()).all()
    return render_template('latest.html', 
        items=items, 
        category="Latest", 
        categories=categories, 
        cat_name="Latest", 
        login_session=login_session)


@app.route('/category/new/', methods=['POST', 'GET'])
@checkAuthorization
def newCategory(cat_name=""):
    """
    newCategory creates a new category
    args:
        takes post method and category name
    """
    

    if request.method == 'POST':

        checkAndAbort(request.form['name'])

        category = Category(
            name=request.form['name'],
            # store reference to user when created
            user=getUserInfo(login_session['user_id']))
        session.add(category)
        session.commit()
        flash("new category created!")
        return redirect(url_for('showCatalog', 
            cat_name=category.name, 
            login_session=login_session))
    else:
        return render_template('newcategory.html', 
            login_session=login_session, 
            categories=session.query(Category).all())


@app.route('/category/<cat_name>/edit/', methods=['POST', 'GET'])
@checkAuthorization
def editCategory(cat_name):
    """
    editCategory edits an existing category
    args:
        takes post method and category name
    """

    editedCategory = session.query(Category).filter_by(name=cat_name).one()
    categories = session.query(Category).filter(
        Category.name != cat_name).all()

    

    if checkUserIsCorrectUser(editedCategory):
        abort(401)

    if request.method == 'POST' and editedCategory:

        editedCategory.name = request.form['name']
        editedCategory.user = getUserInfo(login_session['user_id'])
        session.add(editedCategory)
        session.commit()
        flash("category updated!")
        return redirect(url_for('showCatalog', 
            cat_name=editedCategory.name,
            login_session=login_session, 
            categories=categories))
    else:
        return render_template('editcategory.html',
                               cat_name=cat_name, 
                               category=editedCategory, 
                               login_session=login_session, 
                               categories=categories)


@app.route('/category/<cat_name>/delete/', methods=['POST', 'GET'])
@checkAuthorization
def deleteCategory(cat_name):
    """
    deleteCategory deletes a category
    args:
        takes post method and category name
    """

    

    item = session.query(Category).filter_by(name=cat_name).one()

    if checkUserIsCorrectUser(item):
        return render_template('unauthorized_access.html')

    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("%s catalog item was deleted" % item.name)
        return redirect(url_for('showCatalog', 
            cat_name=cat_name, 
            login_session=login_session))
    else:
        return render_template('deletecategory.html', 
            cat_name=cat_name, 
            category=item, 
            login_session=login_session)


@app.route('/category/<cat_name>')
@app.route('/category/<cat_name>/')
def categoryMenu(cat_name="Soccer"):
    """
    categoryMenu displays items in the current category
    will direct to either public or regular catalog if user is signed in
    args:
        takes category name
    """

    category = session.query(Category).filter_by(name=cat_name).one()
    categories = session.query(Category).all()
    items = session.query(CatalogItem).filter_by(category_id=category.id)

    if not checkLogin():
        return render_template('publiccatalog.html', 
            category=category, 
            items=items, 
            categories=categories, 
            cat_name=cat_name, 
            login_session=login_session)
    else:
        return render_template('catalog.html', 
            category=category, 
            items=items, 
            categories=categories, 
            cat_name=cat_name, 
            login_session=login_session)


@app.route('/category/<cat_name>/new/', methods=['GET', 'POST'])
@checkAuthorization
def newCatalogItem(cat_name):
    """
    newCatalogItem creates a new catalogItem
    args:
        takes post method and category name
    """
    

    if request.method == 'POST':
        category = session.query(Category).filter_by(name=cat_name).one()
        newItem = CatalogItem(
            name=request.form['name'],
            title=request.form['title'],
            description=request.form['description'],
            price=request.form['price'],
            img=request.form['img'],
            category_id=category.id,
            user=getUserInfo(login_session['user_id']))

        session.add(newItem)
        session.commit()
        flash("new catalog item created!")

        return redirect(url_for('categoryMenu', 
            cat_name=cat_name, 
            login_session=login_session))
    else:
        return render_template('newcatalogitem.html', 
            cat_name=cat_name, 
            login_session=login_session)


@app.route('/category/<cat_name>/<catalogItem>/<int:item_id>')
def showCatalogItem(cat_name, catalogItem, item_id):
    """
    showCatalogItem displays current item to the user
    args:
        takes category name, catalog item and the id of the catalog item
    """
    publicItem = session.query(CatalogItem).filter_by(id=item_id).one()
    categories = session.query(Category).all()
    return render_template('publiccatalogitem.html',
                           cat_name=cat_name, 
                           catalogItem=catalogItem,
                           i=publicItem, 
                           login_session=login_session)


@app.route('/category/<cat_name>/<catalogItem>/<int:item_id>/edit/', 
    methods=['GET', 'POST'])
@checkAuthorization
def editCatalogItem(cat_name, catalogItem, item_id):
    """
    editCatalogItem edits the current catalog item
    args:
        takes category name, catalog item and the id of the catalog item
    """
    editedItem = session.query(CatalogItem).filter_by(id=item_id).one()
    categories = session.query(Category).all()

    

    # handles if an incorrect user attempts to access
    if checkUserIsCorrectUser(editedItem):
        abort(403)

    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['title']:
            editedItem.title = request.form['title']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['img']:
            editedItem.img = request.form['img']
        if request.form['category_id']:
            editedItem.category_id = request.form['category_id']

        session.add(editedItem)
        session.commit()
        flash("%s catalog item updated!" % editedItem.name)
        return redirect(url_for('categoryMenu', 
            cat_name=cat_name, 
            login_session=login_session))
    else:
        return render_template('editcatalogitem.html', 
            cat_name=cat_name, 
            catalogItem=catalogItem,
            i=editedItem, 
            categories=categories, 
            login_session=login_session)


@app.route('/category/<cat_name>/<catalogItem>/<int:item_id>/delete/', methods=['GET', 'POST'])
@checkAuthorization
def deleteCatalogItem(cat_name, catalogItem, item_id):
    """
    deleteCatalogItem deletes the current catalog item
    args:
        takes category name, catalog item and the id of the catalog item
    """
    item = session.query(CatalogItem).filter_by(id=item_id).one()

    

    if checkUserIsCorrectUser(item):
        abort(403)

    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("%s catalog item was deleted" % item.name)
        return redirect(url_for('categoryMenu', 
            cat_name=cat_name, 
            login_session=login_session))
    else:
        return render_template('deletecatalogitem.html', 
            cat_name=cat_name, catalogItem=catalogItem, 
            item=item, login_session=login_session)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
