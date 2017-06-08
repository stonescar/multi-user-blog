from google.appengine.ext import db
from database import Database
from users import Users
from posts import Posts


class Votes(Database):
    post = db.ReferenceProperty(Posts)
    user = db.ReferenceProperty(Users)
    vote = db.IntegerProperty(required=True)
