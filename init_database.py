# initializes db with items

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, CatalogItem, User
from flask import jsonify
import json


engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def loadData(fname, key):
    '''loads data from json file into python array'''
    return json.load(open(fname, 'r'))[key]

# Initializes and Loads all user data


def initAll():
    # clean up by deleting old resources

    session.query(Category).delete()
    session.query(CatalogItem).delete()
    session.query(User).delete()

    # load users

    for user in loadData('usersInit.json', 'Users'):
        session.add(User(
            name=user['name'],
            email=user['email'],
            picture=user['picture']
        ))
        session.commit()

    # load categories

    for category in loadData('categoriesInit.json', 'Categories'):

        user_id = category['user_id']
        user = session.query(User).filter_by(id=user_id).one()

        session.add(Category(
            name=category['name'],
            user=user,
        ))
        session.commit()

    # load catalog items

    for catalogItem in loadData('itemsInit.json', 'CatalogItems'):

        category_id = catalogItem['category_id']
        user_id = catalogItem['user_id']

        category = session.query(Category).filter_by(id=category_id).one()
        user = session.query(User).filter_by(id=user_id).one()

        session.add(
            CatalogItem(
                name=catalogItem['name'],
                title=catalogItem['title'],
                description=catalogItem['description'],
                price=catalogItem['price'],
                category=category,
                img=catalogItem['img'],
                user=user,
            )
        )
        session.commit()

if __name__ == '__main__':
    initAll()
    items = session.query(CatalogItem).all()
    print "added %s items to the catalog!" % len(items)
