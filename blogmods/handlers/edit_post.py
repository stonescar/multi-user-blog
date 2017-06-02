from main_handler import Handler
from ..models import Posts
from .. import utils


class EditPost(Handler):
    """Handler for edit post page"""
    @utils.login_required
    def get(self, post_id):
        p = Posts.by_id(post_id)
        if p:
            if self.uid() == p.author.key().id():
                self.render("edit_post.html", p=p)
            else:
                self.redirect("/post/"+str(post_id))
        else:
            self.redirect("/")

    @utils.login_required
    def post(self, post_id):
        p = Posts.by_id(post_id)
        if p:
            subject = self.request.get("subject")
            content = self.request.get("content")

            if subject and content:
                if self.uid() == p.author.key().id():
                    p.subject = subject
                    p.content = content
                    p.put()
                self.redirect("/post/"+str(post_id))
            else:
                err = """If you want to delete this post,
                         press the delete button"""
                self.render("edit_post.html", p=p, err=err)
        else:
            self.redirect("/")
