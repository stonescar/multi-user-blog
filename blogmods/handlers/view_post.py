from main_handler import Handler
from ..models import Posts, Comments
from .. import utils


class ViewPost(Handler):
    """Handler for post pages"""
    def get_post_comments(self, post_id):
        p = Posts.by_id(post_id)
        c = Comments.get_comments(post_id)
        return p, c

    def render_post(self, post_id, *a, **kw):
        p, c = self.get_post_comments(post_id)
        edit = True if p.author.key().id() == self.uid() else False

        self.render("viewpost.html", p=p, comments=c,
                    uid=self.uid(), edit=edit)

    def get(self, post_id):
        if Posts.by_id(post_id):
            self.render_post(post_id)
        else:
            # Send to front if post doesn't exist
            self.redirect("/")

    @utils.login_required
    def post(self, post_id):
        # Posting comments
        if Posts.by_id(post_id):
            comment = self.request.get("comment")
            if comment:
                c = Comments(author=self.user,
                             post=Posts.by_id(post_id),
                             comment=comment)
                c.put()
                self.redirect("/post/%s#%s" % (str(post_id), str(c.key().id()))) # NOQA
            else:
                self.render_post(post_id, err="Comment must have content")
        else:
            self.redirect("/")
