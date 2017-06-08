from google.appengine.ext import db
from .. import utils
from main_handler import Handler


class Welcome(Handler):
    """Handler for welcome page"""
    def count(self):
        # Collecting statistics for user
        # Count blog posts by user
        p = db.GqlQuery("""SELECT * FROM Posts
                        WHERE author = KEY('Users', %s)""" % self.uid())
        uid = self.uid()
        posts = p.count()

        # Count comments by user
        c = db.GqlQuery("""SELECT * FROM Comments
                        WHERE author = KEY('Users', %s)""" % self.uid())
        comments = c.count()

        # Count number of votes by user
        votes = self.user.get_votes(uid)

        # Count average score of posts by user
        avg_score = self.user.get_post_scores(uid)

        # Count score of votes
        tot_votes = self.user.get_vote_score(uid)

        return [posts, comments, votes, avg_score, tot_votes]

    @utils.login_required
    def get(self):
        p = db.GqlQuery("""SELECT * FROM Posts
                        WHERE author = KEY('Users', %s)
                        ORDER BY created DESC
                        LIMIT 5""" % self.uid())
        c = db.GqlQuery("""SELECT * FROM Comments
                        WHERE author = KEY('Users', %s)
                        ORDER BY time DESC
                        LIMIT 5""" % self.uid())
        self.render("welcome.html",
                    posts=p, comms=c,
                    u=self.user.username,
                    count=self.count())
