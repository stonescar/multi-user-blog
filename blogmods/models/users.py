from google.appengine.ext import db
from database import Database
from .. import seq


class Users(Database):
    """ DB for users """
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty(required=False)

    def get_votes(self, uid):
        v = db.GqlQuery("""SELECT * FROM Votes
                           WHERE user = KEY('Users', %s)
                           """ % uid)
        return v.count()

    def get_vote_score(self, uid):
        s = db.GqlQuery("""SELECT * FROM Votes
                           WHERE user = KEY('Users', %s)
                           """ % uid)
        return sum(v.vote for v in s)

    def get_post_scores(self, uid):
        p = db.GqlQuery("""SELECT * FROM Posts
                           WHERE author = KEY('Users', %s)
                           """ % uid)
        if p.count() > 0:
            posts = [post.key().id() for post in p]
            score = 0
            for post in posts:
                s = db.GqlQuery("""SELECT * FROM Votes
                                   WHERE post = KEY('Posts', %s)
                                   """ % post)
                if s.count() > 0:
                    score += sum(score.vote for score in s)
            return score/p.count()
        else:
            return 0

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
