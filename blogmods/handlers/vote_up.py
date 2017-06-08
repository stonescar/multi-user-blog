from main_handler import Handler
from .. import utils


class VoteUp(Handler):
    """Handler for voting up posts"""
    @utils.login_required
    @utils.post_exists
    def get(self, post_id, p):
        utils.vote_up(p, self.user)
        self.redirect("/post/"+str(post_id))
