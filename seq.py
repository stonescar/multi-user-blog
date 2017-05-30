import random
import string
import hashlib
import s


def make_salt():
    return "".join(random.choice(string.letters) for i in range(5))


def hash_pw(user, pw, salt=""):
    salt = make_salt() if salt == "" else salt
    h = hashlib.sha256(s.secret + user + pw + salt).hexdigest()
    return "%s|%s" % (h, salt)


def valid_pw(user, pw, h):
    salt = h.split("|")[1]
    if hash_pw(user, pw, salt) == h:
        return True


def hash_cookie(cookie, salt=""):
    salt = make_salt() if salt == "" else salt
    h = hashlib.md5(s.secret + cookie + salt).hexdigest()
    return "%s|%s|%s" % (cookie, h, salt)


def valid_cookie(i):
    if i:
        c, h, salt = i.split("|")
        if hash_cookie(c, salt) == i:
            return c
