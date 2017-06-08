import os
import jinja2
from functools import wraps
from .models import Posts, Comments, Votes


template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


def login_required(f):
    """
    Decorator to see if user is logged in
    Redirect to login page if not logged in
    """
    @wraps(f)
    def login(self, *a, **kw):
        if self.user:
            f(self, *a, **kw)
        else:
            self.redirect("/login")
    return login


def not_logged_in(f):
    """
    Decorator to see if user is NOT logged in.
    Redirect to welcome page if logged in
    """
    @wraps(f)
    def logged_in(self, *a, **kw):
        if self.user:
            self.redirect("/welcome")
        else:
            f(self, *a, **kw)
    return logged_in


def post_exists(f):
    """
    Decorator to see if post exists
    """
    @wraps(f)
    def wrapper(self, post_id):
        post = Posts.by_id(post_id)
        if post:
            return f(self, post_id, post)
        else:
            self.redirect("/")
    return wrapper


def comment_exists(f):
    """
    Decorator to see if comment exists
    """
    @wraps(f)
    def wrapper(self, comm_id):
        comment = Comments.by_id(comm_id)
        if comment:
            return f(self, comm_id, comment)
        else:
            self.redirect("/")
    return wrapper


def user_owns_post(f):
    """
    Decorator to see if user is post author
    """
    @wraps(f)
    def wrapper(self, post_id, *a, **kw):
        post = Posts.by_id(post_id)
        if post.author.key().id() != self.uid():
            self.redirect("/post/"+post_id)
        else:
            f(self, post_id, *a, **kw)
    return wrapper


def user_owns_comment(f):
    """
    Decorator to see if user is comment author
    """
    @wraps(f)
    def wrapper(self, comm_id, *a, **kw):
        comment = Comments.by_id(comm_id)
        if comment.author.key().id() != self.uid():
            self.redirect("/post/"+str(comment.post.key().id()))
        else:
            f(self, comm_id, *a, **kw)
    return wrapper


def vote_up(p, u):
    if p.can_vote(u.key().id()):
        v = Votes(post=p, user=u, vote=1)
        v.put()


def vote_dn(p, u):
    if p.can_vote(u.key().id()):
        v = Votes(post=p, user=u, vote=-1)
        v.put()
