from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shelflife_models import Category, User, Base, Item

engine = create_engine('sqlite:///shelflife.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='http://tinyurl.com/ycxn2jb4')
session.add(User1)
session.commit()

print "added user!"


# Create initial categories
category1 = Category(user_id=1, name="Fruits")

session.add(category1)
session.commit()

category2 = Category(user_id=1, name="Vegetables")

session.add(category2)
session.commit()

category3 = Category(user_id=1, name="Dairy & Eggs")

session.add(category3)
session.commit()

category4 = Category(user_id=1, name="Meat & Poultry")

session.add(category4)
session.commit()

category5 = Category(user_id=1, name="Fish & Shellfish")

session.add(category5)
session.commit()

category6 = Category(user_id=1, name="Nuts, Grains, & Pasta")

session.add(category6)
session.commit()

category7 = Category(user_id=1, name="Condiments & Oils")

session.add(category7)
session.commit()

category8 = Category(user_id=1, name="Snacks & Baked Goods")

session.add(category8)
session.commit()

category9 = Category(user_id=1, name="Herbs & Spices")

session.add(category9)
session.commit()

category10 = Category(user_id=1, name="Beverages")

session.add(category10)
session.commit()

print "added categories!"


# Create dummy items
item1 = Item(name="Apples", description="Apples must be kept in a cool place.",
             category_id=1, user_id=1)

session.add(item1)
session.commit()

item2 = Item(name="Milk", description="Milk lasts for 7 days after its best-by \
             date.", category_id=3, user_id=1)

session.add(item2)
session.commit()

print "added items!"
