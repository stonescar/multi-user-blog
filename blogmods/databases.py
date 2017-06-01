from google.appengine.ext import db
from datetime import timedelta
import seq


class Database(db.Model):
    def time_convert(self, t):
        # Convert to Norwegian time zone
        return t + timedelta(seconds=7200)

    @classmethod
    def by_id(cls, uid):
        return cls.get_by_id(int(uid))


class Users(Database):
    """ DB for users """
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty(required=False)
    ups = db.TextProperty(default="")
    downs = db.TextProperty(default="")

    @classmethod
    def by_name(cls, name):
        u = cls.all().filter('username =', name).get()
        return u

    @classmethod
    def name_by_id(cls, id):
        u = cls.by_id()
        return u.username

    @classmethod
    def register(cls, name, pw, email=None):
        pw_hash = seq.hash_pw(name, pw)
        return cls(username=name,
                   password=pw_hash,
                   email=email)

    @classmethod
    def valid_login(cls, name, pw):
        u = cls.by_name(name)
        if u and seq.valid_pw(name, pw, u.password):
            return u


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
