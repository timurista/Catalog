import sys
from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

# classes are special classes
Base = declarative_base()

# create class code
class Category(Base):
	__tablename__ = "category"
	name = Column(
		String(80), nullable = False)
	
	id = Column(
		Integer, primary_key = True)

# create rest class
class CatalogItem(Base):
	__tablename__ = "catalog_item"
	name = Column(String(80), nullable=False)
	title = Column(String(200), nullable=False)
	id = Column(Integer, primary_key=True)
	description = Column(String(250))
	price = Column(String(8))
	category_id = Column(
		Integer, ForeignKey('category.id'))
	category = relationship(Category)
	img = Column(String(250))

	@property
	def serialize(self):
		#returns object data in easily serializeable format
		return {
			'name' : self.name,
			'title' : self.title,
			'description' : self.description,
			'id' : self.id,
			'price' : self.price,
			'img' : self.img,
		}

#### insert at end of file ###
engine = create_engine(
	'sqlite:///catalog.db')
Base.metadata.create_all(engine)

