import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func

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
	title = Column(String(200))
	id = Column(Integer, primary_key=True)
	description = Column(String(250))
	price = Column(String(8))
	category_id = Column(
		Integer, ForeignKey('category.id'))
	category = relationship(Category)
	img = Column(String(250))
	# timestamp is set to autopopulate when item is created, and autoupdate
	timestamp = Column(DateTime, default=func.now(), onupdate=func.current_timestamp())



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
			'category_id' : self.category_id,
			'timestamp' : self.timestamp,
		}

#### insert at end of file ###
engine = create_engine(
	'sqlite:///catalog.db')
Base.metadata.create_all(engine)

