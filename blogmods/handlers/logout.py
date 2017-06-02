from main_handler import Handler


class Logout(Handler):
    """Handler for logging out"""
    def get(self):
        self.logout()
        self.redirect("/")
