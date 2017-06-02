from .. import utils
from main_handler import Handler
from ..models import Users


class Login(Handler):
    """Handler for login page"""
    @utils.not_logged_in
    def get(self):
        self.render("login.html")

    @utils.not_logged_in
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
