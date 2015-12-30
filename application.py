# TODO

# route to category list

# main catalog

# route to new item
# route to edit item
# route to delete item

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CatalogItem
app = Flask(__name__)

# error
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/category/<cat_name>')
@app.route('/category/<cat_name>/')
def categoryMenu(cat_name="Soccer"):
    category = session.query(Category).filter_by(name = cat_name).one()
    categories = session.query(Category).all()
    items = session.query(CatalogItem).filter_by(category_id=category.id)
    return render_template('catalog.html', category=category, items = items, categories=categories)

@app.route('/category/<cat_name>/new/', methods=['GET', 'POST'])
def newCatalogItem(cat_name):
    if request.method == 'POST':
    	category = session.query(Category).filter_by(name = cat_name).one()
        newItem = CatalogItem(name = request.form['name'], 
            title = request.form['title'],
            description = request.form['description'],
            price = request.form['price'],
            img = request.form['img'],
            category_id = category.id)
        session.add(newItem)
        session.commit()
        flash("new catalog item created!")
        return redirect(url_for('categoryMenu', cat_name = cat_name))
    else:
        return render_template('newcatalogitem.html', cat_name = cat_name)
    # return "page to create a new catalog item. Task 1 complete!"

# TODO: Make route for displayOnly
@app.route('/category/<cat_name>/<catalogItem>/')
def showCatalogItem(cat_name, catalogItem):
    publicItem = session.query(CatalogItem).filter_by(name = catalogItem).one()
    categories = session.query(Category).all()
    return render_template('publiccatalogitem.html', 
        cat_name = cat_name, catalogItem = catalogItem, 
        i = publicItem)

@app.route('/category/<cat_name>/<catalogItem>/edit/', methods = ['GET', 'POST'])
def editCatalogItem(cat_name, catalogItem):
    editedItem = session.query(CatalogItem).filter_by(name = catalogItem).one()
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

# Task 3: Create a route for deleteCatalogItem function here

@app.route('/category/<cat_name>/<catalogItem>/delete/', methods = ['GET', 'POST'])
def deleteCatalogItem(cat_name, catalogItem):
    print catalogItem
    item = session.query(CatalogItem).filter_by(name = catalogItem).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("%s catalog item was deleted" % item.name)
        return redirect(url_for('categoryMenu', cat_name = cat_name))
    else:
        return render_template('deletecatalogitem.html', cat_name = cat_name, catalogItem = catalogItem, item = item)

# Making an API Endpoint (GET Request)
@app.route('/category/<cat_name>/catalog/JSON')
def categoryMenuJSON(cat_name):
    category = session.query(Category).filter_by(name = cat_name).one()
    items = session.query(CatalogItem).all()
    return jsonify(CatalogItems = [i.serialize for i in items] )

# Get one Menu Item JSON
@app.route('/category/<cat_name>/<catalogItem>/JSON')
def categoryCatalogItemJSON(cat_name, catalogItem):
    item = session.query(CatalogItem).filter_by(name = catalogItem).one()
    return jsonify(CatalogItems = item.serialize )


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
