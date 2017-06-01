import re

import webapp2
from google.appengine.ext import db

from blogmods.databases import Users, Posts, Comments
from blogmods import env


class Main(env.Handler):
    """Handler for front page"""
    def get(self):
        posts = db.GqlQuery("""SELECT * FROM Posts
                               ORDER BY created DESC
                               LIMIT 10""")
        self.render("index.html", posts=posts)


class Signup(env.Handler):
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

    @env.not_logged_in
    def get(self):
        self.render("signup.html")

    @env.not_logged_in
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


class Login(env.Handler):
    """Handler for login page"""
    @env.not_logged_in
    def get(self):
        if self.user:
            self.redirect("/welcome")
        else:
            self.render("login.html")

    @env.not_logged_in
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


class Logout(env.Handler):
    """Handler for logging out"""
    def get(self):
        self.logout()
        self.redirect("/")


class Welcome(env.Handler):
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

    @env.login_required
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


class ViewPost(env.Handler):
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

    @env.login_required
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


class NewPost(env.Handler):
    """Handler for new post page"""
    @env.login_required
    def get(self):
        self.render("newpost.html")

    @env.login_required
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


class EditPost(env.Handler):
    """Handler for edit post page"""
    @env.login_required
    def get(self, post_id):
        p = Posts.by_id(post_id)
        if p:
            if self.uid() == p.author.key().id():
                self.render("edit_post.html", p=p)
            else:
                self.redirect("/post/"+str(post_id))
        else:
            self.redirect("/")

    @env.login_required
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


class DelPost(env.Handler):
    """Handler for deleting posts"""
    @env.login_required
    def get(self, post_id):
        p = Posts.by_id(post_id)
        if p and self.uid() == p.author.key().id():
            p.delete()
        self.redirect("/")


class EditComment(env.Handler):
    """Handler for edit comment post page"""
    @env.login_required
    def get(self, comm_id):
        c = Comments.by_id(comm_id)
        if c:
            if self.uid() == c.author.key().id():
                self.render("edit_comment.html", c=c)
            else:
                self.redirect("/post/"+str(c.post.key().id()))
        else:
            self.redirect("/")

    @env.login_required
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


class DelComment(env.Handler):
    """Handler for deleting comments"""
    @env.login_required
    def get(self, comm_id):
        c = Comments.by_id(comm_id)
        if c:
            if self.uid() == c.author.key().id():
                c.delete()
            self.redirect("/post/"+str(c.post.key().id()))
        else:
            self.redirect("/")


class VoteUp(env.Handler):
    """Handler for votimg up posts"""
    @env.login_required
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


class VoteDn(env.Handler):
    """Handler for voting down posts"""
    @env.login_required
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
