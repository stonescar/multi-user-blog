from main_handler import Handler
from .. import utils


class EditPost(Handler):
    """Handler for edit post page"""
    @utils.login_required
    @utils.post_exists
    @utils.user_owns_post
    def get(self, post_id, p):
        self.render("edit_post.html", p=p)

    @utils.login_required
    @utils.post_exists
    @utils.user_owns_post
    def post(self, post_id, p):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            p.subject = subject
            p.content = content
            p.put()
            self.redirect("/post/"+str(post_id))
        else:
            err = """If you want to delete this post,
                     press the delete button"""
            self.render("edit_post.html", p=p, err=err)
