from main_handler import Handler
from .. import utils


class VoteDn(Handler):
    """Handler for voting down posts"""
    @utils.login_required
    @utils.post_exists
    def get(self, post_id, p):
        if p.can_vote(self.uid()):
            p.score -= 1
            self.user.downs += str(post_id)+","
            # Don't update the modified field
            p._properties['modified'].auto_now = False
            p.put()
            self.user.put()
            p._properties['modified'].auto_now = True
        self.redirect("/post/"+str(post_id))
