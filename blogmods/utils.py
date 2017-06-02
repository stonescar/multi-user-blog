import os
import jinja2


template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


def login_required(f):
    """
    Decorator to see if user is logged in
    Redirect to login page if not logged in
    """
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
    def logged_in(self, *a, **kw):
        if self.user:
            self.redirect("/welcome")
        else:
            f(self, *a, **kw)
    return logged_in
