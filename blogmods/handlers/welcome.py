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
        posts = p.count()

        # Count comments by user
        c = db.GqlQuery("""SELECT * FROM Comments
                        WHERE author = KEY('Users', %s)""" % self.uid())
        comments = c.count()

        # Count number of votes by user
        ups = self.user.ups.split(",")
        downs = self.user.downs.split(",")
        ups = 0 if len(ups) == 0 else len(ups)-1
        downs = 0 if len(downs) == 0 else len(downs)-1
        votes = ups+downs

        # Count average score of posts by user
        scores = []
        for post in p:
            scores.append(post.score)
        avg_score = sum(scores) / len(scores) if len(scores) else 0

        # Count score of votes
        tot_votes = ups-downs

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
