from main_handler import Handler
from .. import utils


class VoteDn(Handler):
    """Handler for voting down posts"""
    @utils.login_required
    @utils.post_exists
    def get(self, post_id, p):
        utils.vote_dn(p, self.user)
        self.redirect("/post/"+str(post_id))
