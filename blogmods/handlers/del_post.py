from main_handler import Handler
from .. import utils


class DelPost(Handler):
    """Handler for deleting posts"""
    @utils.login_required
    @utils.post_exists
    @utils.user_owns_post
    def get(self, post_id, post):
        post.delete()
        self.redirect("/")
