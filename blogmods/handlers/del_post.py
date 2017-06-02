from main_handler import Handler
from ..models import Posts
from .. import utils


class DelPost(Handler):
    """Handler for deleting posts"""
    @utils.login_required
    def get(self, post_id):
        p = Posts.by_id(post_id)
        if p and self.uid() == p.author.key().id():
            p.delete()
        self.redirect("/")
