

import os
import webapp2
import jinja2
import re
import hashlib
import hmac
import random
import string
import time

from google.appengine.ext import ndb

SECRET = "iamasecret"


# Making Cookies Secure

def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()


def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))


def check_secure_val(h):
    str = h[:h.find('|')]
    HASH = h[h.find('|')+1:]
    if hash_str(str) == HASH:
        return str
    else:
        return None


# Making Hash of Passwords


def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))


def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (h, salt)


def valid_pw(name, pw, h):
    salt = h[h.find(',')+1:]
    if h == make_pw_hash(name, pw, salt):
        return True


# Checking Validity of Username, Passwords and Email

def valid_username(username):
    return bool(re.compile(r'^[a-zA-Z0-9_-]{3,20}$').match(username))


def valid_password(password):
    return bool(re.compile(r'^.{3,20}$').match(password))


def valid_email(email):
    return bool(re.compile(r'^[\S]+@[\S]+.[\S]+$').match(email))


def verify_password(verifypwd, password):
    if (verifypwd == password):
        return True


# Key to identify a user uniquely

def users_key(group='default'):
    return ndb.Key('users', group)


# Making User Class that defines the database entry format

class User(ndb.Model):
    """ Storing name email and hashed password of user """
    name = ndb.StringProperty(required=True)
    pw_hash = ndb.StringProperty(required=True)
    email = ndb.StringProperty()

    @classmethod
    def _get_user(cls, uid):
        return User.get_by_id(uid, parent=users_key())

    @classmethod
    def _register(cls, name, pw, email=None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent=users_key(),
                    name=name,
                    pw_hash=pw_hash,
                    email=email)

    @classmethod
    def _check_name(cls, name):
        user = User.gql("WHERE name = '%s'" % name).get()
        return user
