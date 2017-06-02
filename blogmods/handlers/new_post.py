from main_handler import Handler
from ..models import Posts
from .. import utils


class NewPost(Handler):
    """Handler for new post page"""
    @utils.login_required
    def get(self):
        self.render("newpost.html")

    @utils.login_required
    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            p = Posts(subject=subject, content=content, author=self.user)
            p.put()
            self.redirect("/post/"+str(p.key().id()))

        else:
            error = "Subject and content is required"
            self.render("newpost.html",
                        subject=subject,
                        content=content,
                        error=error)
