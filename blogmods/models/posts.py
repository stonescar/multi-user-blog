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

    def can_vote(self, uid):
        # See if user is allowed to vote
        if uid:
            post_id = self.key().id()
            v = db.GqlQuery("""SELECT vote FROM Votes
                               WHERE post = KEY('Posts', %s)
                               AND user = KEY('Users', %s)
                               """ % (post_id, uid))
            if v.count() == 0 and uid != self.author.key().id():
                return True

    def get_score(self):
        s = db.GqlQuery("""SELECT * FROM Votes
                               WHERE post = KEY('Posts', %s)
                               """ % self.key().id())
        score = sum(v.vote for v in s) if s.count() > 0 else 0
        return score

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
