from main_handler import Handler
from .. import utils


class DelComment(Handler):
    """Handler for deleting comments"""
    @utils.login_required
    @utils.comment_exists
    @utils.user_owns_comment
    def get(self, comm_id, comment):
        comment.delete()
        self.redirect("/post/"+str(comment.post.key().id()))
