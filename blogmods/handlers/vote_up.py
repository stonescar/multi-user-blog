from main_handler import Handler
from ..models import Posts
from .. import utils


class VoteUp(Handler):
    """Handler for voting up posts"""
    @utils.login_required
    def get(self, post_id):
        p = Posts.by_id(post_id)
        if p:
            if p.can_vote(self.uid()):
                p.score += 1
                self.user.ups += str(post_id)+","
                # Don't update the modified field
                p._properties['modified'].auto_now = False
                p.put()
                self.user.put()
                p._properties['modified'].auto_now = True
            self.redirect("/post/"+str(post_id))
        else:
            self.redirect("/")
