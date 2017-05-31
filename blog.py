import os
import re

import jinja2
import webapp2
import seq

from google.appengine.ext import db
from datetime import timedelta


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


#
#
# DATABASES
#
#

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


#
#
# HANDLERS
#
#


def login_required(f):
    """Decorator to see if user is logged in"""
    def login(self, *a, **kw):
        if self.user:
            f(self, *a, **kw)
        else:
            self.redirect("/login")
    return login


class Handler(webapp2.RequestHandler):
    """Main Requesthandler"""
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_cookie(self, name, value, plain=False):
        cookie_val = seq.hash_cookie(value) if not plain else value
        self.response.headers.add_header(
            "Set-Cookie",
            str("%s=%s; Path=/" % (name, cookie_val)))

    def get_cookie(self, name):
        cookie = self.request.cookies.get(name)
        return seq.valid_cookie(cookie)

    def del_cookie(self, name):
        self.response.headers.add_header(
            "Set-Cookie",
            str("%s=; Path=/; Expires=Wed, 21 Oct 2015 07:28:00 GMT" % name))

    def login(self, user):
        self.set_cookie('user_id', str(user.key().id()))
        self.set_cookie('user', user.username, True)

    def logout(self):
        self.del_cookie('user_id')
        self.del_cookie('user')

    def uid(self):
        if self.user:
            return self.user.key().id()

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.get_cookie('user_id')
        self.user = uid and Users.by_id(int(uid))


class Main(Handler):
    """Handler for front page"""
    def get(self):
        posts = db.GqlQuery("""SELECT * FROM Posts
                               ORDER BY created DESC
                               LIMIT 10""")
        self.render("index.html", posts=posts)


class Signup(Handler):
    """Handler for signup page"""
    def verify(self, input, type):
        USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        PASS_RE = re.compile(r"^.{3,20}$")
        MAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")

        if type == "username":
            return USER_RE.match(input)
        elif type == "password":
            return PASS_RE.match(input)
        elif type == "email":
            return MAIL_RE.match(input)
        else:
            return False

    def get(self):
        self.render("signup.html")

    def post(self):
        user = self.request.get("username")
        pass1 = self.request.get("password")
        pass2 = self.request.get("verify")
        email = self.request.get("email")

        err = dict()
        if not self.verify(user, "username"):
            err['err_user'] = "Username not valid"
        if not self.verify(pass1, "password"):
            err['err_pw1'] = "Password not valid"
        if email and not self.verify(email, "email"):
            err['err_mail'] = "Email not valid"
        if pass1 != pass2:
            err['err_pw2'] = "Passwords don't match"
        u1 = Users.by_name(user)
        if u1:
            err['err_user'] = "Username already exists"

        if len(err) == 0:
            u = Users.register(user, pass1, email)
            u.put()

            self.login(u)
            self.redirect("/welcome")

        else:
            self.render("signup.html",
                        username=user,
                        email=email,
                        **err)


class Login(Handler):
    """Handler for login page"""
    def get(self):
        if self.user:
            self.redirect("/welcome")
        else:
            self.render("login.html")

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")

        u = Users.valid_login(username, password)
        if u:
            self.login(u)
            self.redirect("/welcome")
        else:
            self.render("login.html",
                        username=username,
                        error="Login not valid")


class Logout(Handler):
    """Handler for logging out"""
    def get(self):
        self.logout()
        self.redirect("/")


class Welcome(Handler):
    """Handler for welcome page"""
    def count(self):
        # Collecting statistics for user
        # Count blog posts by user
        p = db.GqlQuery("""SELECT * FROM Posts
                        WHERE author = KEY('Users', %s)""" % self.uid())
        posts = p.count()
        # Count comments by user
        c = db.GqlQuery("""SELECT * FROM Comments
                        WHERE author = KEY('Users', %s)""" % self.uid())
        comments = c.count()
        # Count number of votes by user
        ups = self.user.ups.split(",")
        downs = self.user.downs.split(",")
        ups = 0 if len(ups) == 0 else len(ups)-1
        downs = 0 if len(downs) == 0 else len(downs)-1
        votes = ups+downs
        # Count average score of posts by user
        scores = []
        for post in p:
            scores.append(post.score)
        avg_score = sum(scores) / len(scores) if len(scores) else 0
        # Count score of votes
        tot_votes = ups-downs

        return [posts, comments, votes, avg_score, tot_votes]

    @login_required
    def get(self):
        p = db.GqlQuery("""SELECT * FROM Posts
                        WHERE author = KEY('Users', %s)
                        ORDER BY created DESC
                        LIMIT 5""" % self.uid())
        c = db.GqlQuery("""SELECT * FROM Comments
                        WHERE author = KEY('Users', %s)
                        ORDER BY time DESC
                        LIMIT 5""" % self.uid())
        self.render("welcome.html",
                    posts=p, comms=c,
                    u=self.user.username,
                    count=self.count())


class ViewPost(Handler):
    """Handler for post pages"""
    def get_post_comments(self, post_id):
        p = Posts.by_id(post_id)
        c = Comments.get_comments(post_id)
        return p, c

    def render_post(self, post_id, *a, **kw):
        p, c = self.get_post_comments(post_id)
        edit = True if p.author.key().id() == self.uid() else False

        self.render("viewpost.html", p=p, comments=c,
                    uid=self.uid(), edit=edit)

    def get(self, post_id):
        if Posts.by_id(post_id):
            self.render_post(post_id)
        else:
            # Send to front if post doesn't exist
            self.redirect("/")

    @login_required
    def post(self, post_id):
        # Posting comments
        if Posts.by_id(post_id):
            comment = self.request.get("comment")
            if comment:
                c = Comments(author=self.user,
                             post=Posts.by_id(post_id),
                             comment=comment)
                c.put()
                self.redirect("/post/%s#%s" % (str(post_id), str(c.key().id()))) # NOQA
            else:
                self.render_post(post_id, err="Comment must have content")
        else:
            self.redirect("/")


class NewPost(Handler):
    """Handler for new post page"""
    @login_required
    def get(self):
        self.render("newpost.html")

    @login_required
    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            p = Posts(subject=subject, content=content, author=self.user)
            p.put()
            self.redirect("/post/"+str(p.key().id()))

        else:
            error = "Subject and content is required"
            self.render("newpost.html",
                        subject=subject,
                        content=content,
                        error=error)


class EditPost(Handler):
    """Handler for edit post page"""
    @login_required
    def get(self, post_id):
        p = Posts.by_id(post_id)
        if p:
            if self.uid() == p.author.key().id():
                self.render("edit_post.html", p=p)
            else:
                self.redirect("/post/"+str(post_id))
        else:
            self.redirect("/")

    @login_required
    def post(self, post_id):
        p = Posts.by_id(post_id)
        if p:
            subject = self.request.get("subject")
            content = self.request.get("content")

            if subject and content:
                if self.uid() == p.author.key().id():
                    p.subject = subject
                    p.content = content
                    p.put()
                self.redirect("/post/"+str(post_id))
            else:
                err = """If you want to delete this post,
                         press the delete button"""
                self.render("edit_post.html", p=p, err=err)
        else:
            self.redirect("/")


class DelPost(Handler):
    """Handler for deleting posts"""
    @login_required
    def get(self, post_id):
        p = Posts.by_id(post_id)
        if p and self.uid() == p.author.key().id():
            p.delete()
        self.redirect("/")


class EditComment(Handler):
    """Handler for edit comment post page"""
    @login_required
    def get(self, comm_id):
        c = Comments.by_id(comm_id)
        if c:
            if self.uid() == c.author.key().id():
                self.render("edit_comment.html", c=c)
            else:
                self.redirect("/post/"+str(c.post.key().id()))
        else:
            self.redirect("/")

    @login_required
    def post(self, comm_id):
        c = Comments.by_id(comm_id)
        if c:
            comment = self.request.get("comment")
            if comment:
                if self.uid() == c.author.key().id():
                    c.comment = comment
                    c.put()
                self.redirect("/post/%s#%s" % (str(c.post.key().id()), str(c.key().id()))) # NOQA
            else:
                err = """If you want to delete the comment,
                         press the delete button"""
                self.render("edit_comment.html", c=c, err=err)
        else:
            self.redirect("/")


class DelComment(Handler):
    """Handler for deleting comments"""
    @login_required
    def get(self, comm_id):
        c = Comments.by_id(comm_id)
        if c:
            if self.uid() == c.author.key().id():
                c.delete()
            self.redirect("/post/"+str(c.post.key().id()))
        else:
            self.redirect("/")


class VoteUp(Handler):
    """Handler for votimg up posts"""
    @login_required
    def get(self, post_id):
        p = Posts.by_id(post_id)
        if p:
            if p.can_vote(self.uid()):
                p.score += 1
                self.user.ups += str(post_id)+","
                # Don't update the modified field
                p._properties['modified'].auto_now = False
                p.put()
                self.user.put()
                p._properties['modified'].auto_now = True
            self.redirect("/post/"+str(post_id))
        else:
            self.redirect("/")


class VoteDn(Handler):
    """Handler for voting down posts"""
    @login_required
    def get(self, post_id):
        p = Posts.by_id(post_id)
        if p:
            if p.can_vote(self.uid()):
                p.score -= 1
                self.user.downs += str(post_id)+","
                # Don't update the modified field
                p._properties['modified'].auto_now = False
                p.put()
                self.user.put()
                p._properties['modified'].auto_now = True
            self.redirect("/post/"+str(post_id))
        else:
            self.redirect("/")


app = webapp2.WSGIApplication([
    ('/', Main),
    ('/signup', Signup),
    ('/login', Login),
    ('/logout', Logout),
    ('/welcome', Welcome),
    ('/newpost', NewPost),
    ('/post/(\d+)', ViewPost),
    ('/post/edit/(\d+)', EditPost),
    ('/post/del/(\d+)', DelPost),
    ('/comment/edit/(\d+)', EditComment),
    ('/comment/del/(\d+)', DelComment),
    ('/post/up/(\d+)', VoteUp),
    ('/post/dn/(\d+)', VoteDn)
], debug=True)
