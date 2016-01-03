import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

# classes are special classes
Base = declarative_base()

# create user class

class User(Base):
    __tablename__ = "user"
    name = Column(String(80), nullable=False)
    email = Column(String(120), nullable=False)
    picture = Column(String(250))
    id = Column(
        Integer, primary_key=True)

    @property
    def serialize(self):
        ''' returns user data in easily serializeable format '''
        return {
            'name': self.name,
            'id': self.id,
            'picture': self.picture,
            'email': self.email,
        }


# create category code

class Category(Base):
    __tablename__ = "category"
    name = Column(
        String(80), nullable=False)

    id = Column(
        Integer, primary_key=True)

    user = relationship(User)
    user_id = Column(Integer, ForeignKey('user.id'))

    @property
    def serialize(self):
        ''' returns category data in easily serializeable format '''
        return {
            'name': self.name,
            'id': self.id,
            'user_id': self.user_id,
        }

# create catalog item class

class CatalogItem(Base):
    __tablename__ = "catalog_item"
    name = Column(String(80), nullable=False)
    title = Column(String(200))
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    category_id = Column(
        Integer, ForeignKey('category.id'))
    category_name = Column(
        String(70))
    category = relationship(Category)
    img = Column(String(250))
    # timestamp is set to autopopulate when item is created, and autoupdate
    timestamp = Column(DateTime, default=func.now(),
                       onupdate=func.current_timestamp())

    user = relationship(User)
    user_id = Column(Integer, ForeignKey('user.id'))

    @property
    def serialize(self):
        ''' returns catalog item data in easily serializeable format '''
        return {
            'name': self.name,
            'title': self.title,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'img': self.img,
            'category_id': self.category_id,
            'category_name': self.category.name,
            'timestamp': str(self.timestamp),
            'user_id': self.user_id,
            'user': self.user,
        }

# insert at end of file #
engine = create_engine(
    'sqlite:///catalog.db')
Base.metadata.create_all(engine)
