

import os
import webapp2
import jinja2
import re
import hashlib
import hmac
import random
import string
import time

from users import *

from google.appengine.ext import ndb


def blog_key(name='default'):
    """assigns a key to the blogpost"""
    return ndb.Key('blogs', name)


class Post(ndb.Model):
    """Store details about a blog post"""
    subject = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    last_modified = ndb.DateTimeProperty(auto_now=True)
    author = ndb.StructuredProperty(User)
    likes = ndb.IntegerProperty(default=0)


class Comment(ndb.Model):
    """For adding comments to a post"""
    post_id = ndb.IntegerProperty(required=True)
    author = ndb.StructuredProperty(User)
    content = ndb.StringProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)


class Like(ndb.Model):
    """For likes and dislikes on a post"""
    post_id = ndb.IntegerProperty(required=True)
    author = ndb.StructuredProperty(User)
