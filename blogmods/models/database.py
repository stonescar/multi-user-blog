from google.appengine.ext import db
from datetime import timedelta


class Database(db.Model):
    def time_convert(self, t):
        # Convert to Norwegian time zone
        return t + timedelta(seconds=7200)

    @classmethod
    def by_id(cls, uid):
        return cls.get_by_id(int(uid))
