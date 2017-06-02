import re
from ..models import Users
from .. import utils
from main_handler import Handler


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

    @utils.not_logged_in
    def get(self):
        self.render("signup.html")

    @utils.not_logged_in
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
