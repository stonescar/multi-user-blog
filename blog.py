import webapp2
from blogmods import handlers


app = webapp2.WSGIApplication([
    ('/', handlers.Front),
    ('/signup', handlers.Signup),
    ('/login', handlers.Login),
    ('/logout', handlers.Logout),
    ('/welcome', handlers.Welcome),
    ('/newpost', handlers.NewPost),
    ('/post/(\d+)', handlers.ViewPost),
    ('/post/edit/(\d+)', handlers.EditPost),
    ('/post/del/(\d+)', handlers.DelPost),
    ('/comment/edit/(\d+)', handlers.EditComment),
    ('/comment/del/(\d+)', handlers.DelComment),
    ('/post/up/(\d+)', handlers.VoteUp),
    ('/post/dn/(\d+)', handlers.VoteDn)
], debug=True)
