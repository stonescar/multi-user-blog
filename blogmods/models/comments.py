from google.appengine.ext import db
from database import Database
from users import Users
from posts import Posts


class Comments(Database):
    """ DB for comments """
    author = db.ReferenceProperty(Users)
    post = db.ReferenceProperty(Posts)
    comment = db.TextProperty(required=True)
    time = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def get_comments(cls, post_id):
        c = db.GqlQuery("""SELECT * FROM Comments
                           WHERE post = KEY('Posts', %s)
                           ORDER BY time""" % post_id)
        return c
