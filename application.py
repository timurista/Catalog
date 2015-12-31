from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
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

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# TODO: extra credit, include cart item to track user additions




'''
TODO:
1. make sure other users cannot enter information
2. make edit,new, delete for category
2. RSS feed
3. add cart option
4. sign in with facebook
4. vagrant up
5. instructions for init.py file to populate db
6. update readme file
7. restyle app
-- cleanup
8. remove legacy code
9. update function names
10. submit project
'''





###################### OAUTH

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Web App"

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

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
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
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


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

def checkLogin():
    if 'username' not in login_session:
        return True
    else:
        return False

def checkLoginAndRedirect(url="/login"):
    # TODO: check user name is correct username
    if not checkLogin() or login_session['username']:
        return redirect(url)

def checkUserIsCorrectUser(editedItem):
  if editedItem.user_id != login_session['user_id']:
    return "<script>function myAlert() {alert('You are not authorized to delete this restaurant or edit this item. Please create your own restaurant in order to delte or add.');}</script><body onload=myAlert()''>"

# DISCONNECT - Revoke a current user's token and reset their login_session


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
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        #reset user's session
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        # response = make_response(json.dumps('disconnected.'), 200)
        # response.headers['Content-Type'] = 'application/json'
        flash('User successfully logged out!')
        return redirect('/latest')
 
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response
    # else:
    #     # login_session = []
    #     redirect('/catalog')
    #     return "<p>logging out..</p>" + result['status']


## END OAUTH

# Making an API Endpoint (GET Request)
@app.route('/category/<cat_name>/catalog/JSON')
def categoryMenuJSON(cat_name):    
    category = session.query(Category).filter_by(name = cat_name).one()
    items = session.query(CatalogItem).all()
    return jsonify(CatalogItems = [i.serialize for i in items] )

# Get one Menu Item JSON
@app.route('/category/<cat_name>/<catalogItem>/<int:item_id>/JSON')
def categoryCatalogItemJSON(cat_name, catalogItem, item_id):
    item = session.query(CatalogItem).filter_by(id = item_id).one()
    return jsonify(CatalogItems = item.serialize )


# TODO: Additional API Endpoints RSS, Atom, XML


@app.route('/')
@app.route('/latest') 
@app.route('/catalog') 
def showCatalog():    
    categories = session.query(Category).all()
    items = session.query(CatalogItem).order_by(CatalogItem.timestamp.desc()).all()
    return render_template('latest.html', items = items, category="Latest", categories=categories, cat_name="Latest", login_session=login_session)

# For managing categories
@app.route('/category/new/')
def newCategory():
    checkLoginAndRedirect()
    return render_template('newcategory.html')

@app.route('/category/<cat_name>/edit/')
def editCategory(cat_name):
    checkLoginAndRedirect()
    return render_template('editcategory.html')

@app.route('/category/<cat_name>/delete/')
def deleteCategory(cat_name):
    checkLoginAndRedirect()
    return render_template('deletecategory.html')


@app.route('/category/<cat_name>')
@app.route('/category/<cat_name>/')
def categoryMenu(cat_name="Soccer"):
    category = session.query(Category).filter_by(name = cat_name).one()
    categories = session.query(Category).all()
    items = session.query(CatalogItem).filter_by(category_id=category.id)
    if checkLogin():
        return render_template('publiccatalog.html', category=category, items = items, categories=categories, cat_name=cat_name, login_session=login_session)
    else:
        return render_template('catalog.html', category=category, items = items, categories=categories, cat_name=cat_name, login_session=login_session)

@app.route('/category/<cat_name>/new/', methods=['GET', 'POST'])
def newCatalogItem(cat_name):
    checkLoginAndRedirect()
    if request.method == 'POST':
    	category = session.query(Category).filter_by(name = cat_name).one()
        newItem = CatalogItem(name = request.form['name'], 
            title = request.form['title'],
            description = request.form['description'],
            price = request.form['price'],
            img = request.form['img'],
            category_id = category.id,
            # store reference to user when created
            user = getUserInfo())
        session.add(newItem)
        session.commit()
        flash("new catalog item created!")
        return redirect(url_for('categoryMenu', cat_name = cat_name))
    else:
        return render_template('newcatalogitem.html', cat_name = cat_name)

# TODO: Make route for displayOnly
@app.route('/category/<cat_name>/<catalogItem>/<int:item_id>')
def showCatalogItem(cat_name, catalogItem, item_id):
    publicItem = session.query(CatalogItem).filter_by(id = item_id).one()
    categories = session.query(Category).all()
    return render_template('publiccatalogitem.html', 
        cat_name = cat_name, catalogItem = catalogItem, 
        i = publicItem)

@app.route('/category/<cat_name>/<catalogItem>/<int:item_id>/edit/', methods = ['GET', 'POST'])
def editCatalogItem(cat_name, catalogItem, item_id):
    checkLoginAndRedirect()
    editedItem = session.query(CatalogItem).filter_by(id = item_id).one()
    categories = session.query(Category).all()
    
    print request.method
    print editedItem
    if request.method == 'POST':
        print request.form['name']
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
        return redirect(url_for('categoryMenu', cat_name = cat_name))
    else:
        return render_template('editcatalogitem.html', cat_name = cat_name, catalogItem = catalogItem, 
            i = editedItem, categories = categories)

# A route for deleteCatalogItem function here
# TODO: handle CSRF using oauth tokens

@app.route('/category/<cat_name>/<catalogItem>/<int:item_id>/delete/', methods = ['GET', 'POST'])
def deleteCatalogItem(cat_name, catalogItem, item_id):
    checkLoginAndRedirect()
    item = session.query(CatalogItem).filter_by(id = item_id).one()
    checkUserIsCorrectUser(item)

    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("%s catalog item was deleted" % item.name)
        return redirect(url_for('categoryMenu', cat_name = cat_name))
    else:
        return render_template('deletecatalogitem.html', cat_name = cat_name, catalogItem = catalogItem, item = item)



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
