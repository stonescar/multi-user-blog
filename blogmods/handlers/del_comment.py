from main_handler import Handler
from ..models import Comments
from .. import utils


class DelComment(Handler):
    """Handler for deleting comments"""
    @utils.login_required
    def get(self, comm_id):
        c = Comments.by_id(comm_id)
        if c:
            if self.uid() == c.author.key().id():
                c.delete()
            self.redirect("/post/"+str(c.post.key().id()))
        else:
            self.redirect("/")
