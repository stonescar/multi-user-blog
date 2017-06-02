import webapp2
from .. import utils
from .. import seq
from ..models import Users


class Handler(webapp2.RequestHandler):
    """Main Requesthandler"""
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = utils.jinja_env.get_template(template)
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
