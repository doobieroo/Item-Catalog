from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import string

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    # Return object data in easily serializeable format
    @property
    def serialize(self):

        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture
            }


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # Return object data in easily serializeable format
    @property
    def serialize(self):

        return {
            'id': self.id,
            'name': self.name
            }


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # Return object data in easily serializeable format
    @property
    def serialize(self):

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
            }

engine = create_engine('sqlite:///shelflife.db')


Base.metadata.create_all(engine)
