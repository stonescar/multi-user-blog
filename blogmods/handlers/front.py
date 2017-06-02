from google.appengine.ext import db
from main_handler import Handler


class Front(Handler):
    """Handler for front page"""
    def get(self):
        posts = db.GqlQuery("""SELECT * FROM Posts
                               ORDER BY created DESC
                               LIMIT 10""")
        self.render("index.html", posts=posts)
