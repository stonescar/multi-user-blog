from main_handler import Handler
from .. import utils


class EditComment(Handler):
    """Handler for edit comment post page"""
    @utils.login_required
    @utils.comment_exists
    @utils.user_owns_comment
    def get(self, comm_id, c):
        self.render("edit_comment.html", c=c)

    @utils.login_required
    @utils.comment_exists
    @utils.user_owns_comment
    def post(self, comm_id, c):
        comment = self.request.get("comment")
        if comment:
            c.comment = comment
            c.put()
            self.redirect("/post/%s#%s" % (str(c.post.key().id()), str(c.key().id()))) # NOQA
        else:
            err = """If you want to delete the comment,
                     press the delete button"""
            self.render("edit_comment.html", c=c, err=err)
