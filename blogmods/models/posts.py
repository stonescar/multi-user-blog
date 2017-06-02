from google.appengine.ext import db
from database import Database
from users import Users


class Posts(Database):
    """ DB for blogposts """
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)
    author = db.ReferenceProperty(Users)
    score = db.IntegerProperty(default=0)

    def can_vote(self, uid):
        # See if user is allowed to vote
        if uid:
            u = Users.by_id(uid)
            post_id = self.key().id()
            if uid != self.author.key().id() and str(post_id) not in u.ups and str(post_id) not in u.downs: # NOQA
                return True

    def is_modified(self):
        # See if post has been edited
        created = str(self.created)[:21]
        modified = str(self.modified)[:21]
        return True if created != modified else False

    @property
    def comments(self):
        # Get all comments for post
        c = db.GqlQuery("""SELECT * FROM Comments
                           WHERE post = KEY('Posts', %s)
                           ORDER BY time""" % self.key().id())
        return c
