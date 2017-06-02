from main_handler import Handler
from ..models import Comments
from .. import utils


class EditComment(Handler):
    """Handler for edit comment post page"""
    @utils.login_required
    def get(self, comm_id):
        c = Comments.by_id(comm_id)
        if c:
            if self.uid() == c.author.key().id():
                self.render("edit_comment.html", c=c)
            else:
                self.redirect("/post/"+str(c.post.key().id()))
        else:
            self.redirect("/")

    @utils.login_required
    def post(self, comm_id):
        c = Comments.by_id(comm_id)
        if c:
            comment = self.request.get("comment")
            if comment:
                if self.uid() == c.author.key().id():
                    c.comment = comment
                    c.put()
                self.redirect("/post/%s#%s" % (str(c.post.key().id()), str(c.key().id()))) # NOQA
            else:
                err = """If you want to delete the comment,
                         press the delete button"""
                self.render("edit_comment.html", c=c, err=err)
        else:
            self.redirect("/")
