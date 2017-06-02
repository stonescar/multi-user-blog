from main_handler import Handler
from ..models import Posts, Comments
from .. import utils


class ViewPost(Handler):
    """Handler for post pages"""
    def render_post(self, p, *a, **kw):
        self.render("viewpost.html", p=p, uid=self.uid())

    @utils.post_exists
    def get(self, post_id, post):
        self.render_post(post)

    @utils.login_required
    @utils.post_exists
    def post(self, post_id, post):
        # Posting comments
        comment = self.request.get("comment")
        if comment:
            c = Comments(author=self.user,
                         post=Posts.by_id(post_id),
                         comment=comment)
            c.put()
            self.redirect("/post/%s#%s" % (str(post_id), str(c.key().id())))
        else:
            self.render_post(post_id, err="Comment must have content")
