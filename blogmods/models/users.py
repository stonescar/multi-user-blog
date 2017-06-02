from google.appengine.ext import db
from database import Database
from .. import seq


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
