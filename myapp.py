

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
from blog import *

from google.appengine.ext import ndb


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))


class Handler(webapp2.RequestHandler):
    """Defines common functions to Handle Template

    Also deals with setting Cookie values and readign them
    """
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_cookie(self, name, val):
        cookie_val = make_secure_val(str(val))
        self.response.headers.add_header('Set-Cookie',
                                         '%s=%s; Path=/' % (name, cookie_val))

    def read_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def correct_login(self, user):
        self.set_cookie('user_id', str(user.key.id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_cookie('user_id')
        self.user = uid and User._get_user(int(uid))


class MainPage(Handler):
    def get(self):
        self.redirect("/blog")


class SignupPage(Handler):
    """Signup for a new user"""
    def get(self):
        self.render("signup.html", user_name="",
                    pwd="", verifypwd="", email="")

    def post(self):

        # Taking values from the form by post method
        user_name = self.request.get("username")
        pwd = self.request.get("password")
        verifypwd = self.request.get("verify")
        email = self.request.get("email")

        # Checking if the Username, Password and Email are valid

        if not (valid_username(user_name)):
            if not (valid_password(pwd)):
                self.render("signup.html", username=user_name, email=email,
                            username_error="This is not a valid username",
                            password_error="This is not a valid password")
            elif not (verify_password(verifypwd, pwd)):
                self.render("signup.html", username=user_name, email=email,
                            username_error="This is not a valid username",
                            no_match_pwd_error="Your passwords did not match")
        else:
            if not (valid_password(pwd)):
                self.render("signup.html", username=user_name, email=email,
                            password_error="This is not a valid password")
            elif not (verify_password(verifypwd, pwd)):
                self.render("signup.html", username=user_name, email=email,
                            no_match_pwd_error="Your passwords did not match")
            elif (email and not valid_email(email)):
                self.render("signup.html", username=user_name, email=email,
                            email_error="This is not a valid email ID")
            else:
                # Check if user doesn't already exist
                u = User._check_name(user_name)
                if u:
                    self.render("signup.html",
                                name_error="This user already exists")
                else:
                    u = User._register(user_name, pwd, email)
                    u.put()
                    self.correct_login(u)
                    self.redirect("/blog")


class LoginPage(Handler):
    """Asks for Username and Password to login for existing users"""
    def get(self):
        self.render("login.html", error="", username="")

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        u = User._check_name(username)
        if u and valid_pw(username, password, u.pw_hash):
            self.correct_login(u)
            self.redirect("/blog")
        else:
            self.render("login.html", username=username,
                        error="Login Credentials Invalid")


class LogoutPage(Handler):
    """Clear cookies and logs out a user"""
    def get(self):
        self.logout()
        self.redirect("/login")


class BlogPage(Handler):
    """Class for showing all the blog posts on a single page"""
    def get(self):
        q = Post.query().order(-Post.created)
        post = q.fetch(10)
        if self.user:
            uid = self.read_cookie('user_id')
            key = ndb.Key('User', int(uid), parent=users_key())
            curr_user = key.get()
            self.render("blog.html", post=post, user=curr_user)
        else:
            self.render("blog.html", post=post)


class PostPage(Handler):
    """Display page for each blog post"""
    def get(self, post_id):
        key = ndb.Key('Post', int(post_id), parent=blog_key())
        post = key.get()
        comments = Comment.gql("WHERE post_id = %s"
                               " ORDER BY created DESC" % int(post_id))
        liked = None
        if self.user and post:
            uid = self.read_cookie('user_id')
            key = ndb.Key('User', int(uid), parent=users_key())
            curr_user = key.get()
            liked = Like.gql("WHERE post_id = :1 AND author.name = :2",
                             int(post_id), curr_user.name).get()
            self.render("blog_post.html", post=post, comments=comments,
                    liked=liked, user=curr_user)
        elif self.user and not post:
            self.render("error.html")
        else:
            self.render("blog_post.html", post=post, comments=comments,
                    liked=liked, user="")

    def post(self, post_id):
        key = ndb.Key('Post', int(post_id), parent=blog_key())
        post = key.get()
        uid = self.read_cookie('user_id')
        if uid:
            key = ndb.Key('User', int(uid), parent=users_key())
            curr_user = key.get()
        if self.request.get("like"):
            # User liked post
            if post and self.user:
                post.likes += 1
                like = Like(post_id=int(post_id), author=curr_user)
                like.put()
                post.put()
                time.sleep(0.2)
            self.redirect("/blog/%s" % post_id)
        elif self.request.get("unlike"):
            # User unliked post
            if post and self.user:
                post.likes -= 1
                like = Like.gql("WHERE post_id = :1 AND author.name = :2",
                                int(post_id), curr_user.name).get()
                key = like.key
                key.delete()
                post.put()
                time.sleep(0.2)
            self.redirect("/blog/%s" % post_id)
        else:
            # User commented on post
            content = self.request.get("content")
            if self.user:
                if content:
                    comment = Comment(post_id=int(post_id), author=curr_user,
                                  content=str(content))
                    comment.put()
                    time.sleep(0.2)
                    self.redirect("/blog/%s" % post_id)
                else:
                    self.render("blog_post.html", post=post, user=curr_user,
                            content=content, error="Content is required")
            else:
                self.redirect('/login')


class EditPost(Handler):
    """ Renders edit_post page and contains function to update the post """
    def get(self):
        if self.user:
            uid = self.read_cookie('user_id')
            key = ndb.Key('User', int(uid), parent=users_key())
            curr_user = key.get()
            post_id = self.request.get("post")
            key = ndb.Key('Post', int(post_id), parent=blog_key())
            post = key.get()
            if post and post.author.name == curr_user.name:
                self.render("edit_post.html", subject=post.subject,
                            content=post.content, post=post, user=curr_user)
            else:
                self.render("error.html")
        else:
            self.redirect("/login")

    def post(self):
        post_id = self.request.get("post")
        key = ndb.Key('Post', int(post_id), parent=blog_key())
        post = key.get()
        uid = self.read_cookie('user_id')
        if uid:
            key = ndb.Key('User', int(uid), parent=users_key())
            curr_user = key.get()
            if post and post.author.name == curr_user.name:
                self.subject = self.request.get("subject")
                self.content = self.request.get("content")
                if self.subject and self.content:
                    post.subject = self.subject
                    post.content = self.content
                    post.put()
                    time.sleep(0.2)
                    self.redirect("/")
                else:
                    error = "you need both a subject and content"
                    self.render("edit_post.html", subject=subject,
                            content=content, error=error)
            else:
                self.redirect("/")
        else:
            self.redirect("/blog/%s" % post_id)


class DeletePost(Handler):
    """Renders delete_post page and contains function to delete page"""
    def get(self):
        if self.user:
            uid = self.read_cookie('user_id')
            key = ndb.Key('User', int(uid), parent=users_key())
            curr_user = key.get()
            post_id = self.request.get("post")
            key = ndb.Key('Post', int(post_id), parent=blog_key())
            post = key.get()
            if post and post.author.name == curr_user.name:
                self.render("delete_post.html", post=post, user=curr_user)
            else:
                self.render("error.html")
        else:
            self.redirect("/login")

    def post(self):
        uid = self.read_cookie('user_id')
        if uid:
            key = ndb.Key('User', int(uid), parent=users_key())
            curr_user = key.get()
            post_id = self.request.get("post")
            key = ndb.Key('Post', int(post_id), parent=blog_key())
            post = key.get()
            if self.user:
                if post and post.author.name == curr_user.name:
                    key.delete()
                    time.sleep(0.2)
                self.redirect("/blog")
            else:
                self.redirect("/blog")
        else:
            self.render("/blog")


class EditComment(Handler):
    """ Renders edit_comment page and function to update comment """
    def get(self):
        comment_id = self.request.get("comment")
        key = ndb.Key('Comment', int(comment_id))
        comment = key.get()
        uid = self.read_cookie('user_id')
        if uid:
            key = ndb.Key('User', int(uid), parent=users_key())
            curr_user = key.get()
            if comment and comment.author.name == curr_user.name:
                self.render("edit_comment.html", content=comment.content,
                        post_id=comment.post_id, user=curr_user)
            else:
                self.render("error.html")
        else:
            self.redirect("/blog/%s" % comment_id)

    def post(self):
        comment_id = self.request.get("comment")
        key = ndb.Key('Comment', int(comment_id))
        comment = key.get()
        uid = self.read_cookie('user_id')
        if uid:
            key = ndb.Key('User', int(uid), parent=users_key())
            curr_user = key.get()
            if comment and comment.author.name == curr_user.name:
                content = self.request.get("content")
                if content:
                    comment.content = content
                    comment.put()
                    time.sleep(0.2)
                    self.redirect("/blog/%s" % comment.post_id)
                else:
                    error = "you need both a subject and content"
                    self.render("edit_comment.html", content=content,
                                post_id=comment.post_id, error=error,
                                user=curr_user)
        else:
            self.redirect("/blog/%s" % comment.post_id)


class DeleteComment(Handler):
    """Renders delete_comment page and deltes the comment"""
    def get(self):
        if self.user:
            comment_id = self.request.get("comment")
            key = ndb.Key('Comment', int(comment_id))
            comment = key.get()
            uid = self.read_cookie('user_id')
            key = ndb.Key('User', int(uid), parent=users_key())
            curr_user = key.get()
            if comment and comment.author.name == curr_user.name:
                self.render("delete_comment.html", comment=comment, user=curr_user)
            else:
                self.render("error.html")
        else:
            self.redirect("/login")

    def post(self):
        uid = self.read_cookie('user_id')
        if uid:
            userkey = ndb.Key('User', int(uid), parent=users_key())
            curr_user = userkey.get()
            comment_id = self.request.get("comment")
            key = ndb.Key('Comment', int(comment_id))
            comment = key.get()
            if comment and comment.author.name == curr_user.name:
                post_id = comment.post_id
                key.delete()
                time.sleep(0.2)
            self.redirect("/blog/%s" % post_id)
        else:
            self.redirect("/blog/%s" % post_id)


class NewPostForm(Handler):
    """ For creating a new blog post """
    def get(self):
        if self.user:
            uid = self.read_cookie('user_id')
            key = ndb.Key('User', int(uid), parent=users_key())
            curr_user = key.get()
            self.render("newpost.html", subject="", content="",
                        error="", user=curr_user)
        else:
            self.redirect('/login')

    def post(self):
        if not self.user:
            self.redirect('/login')

        subject = self.request.get("subject")
        content = self.request.get("content")
        uid = self.read_cookie('user_id')
        key = ndb.Key('User', int(uid), parent=users_key())
        curr_user = key.get()
        if (subject and content):
            a = Post(parent=blog_key(), subject=subject,
                     content=content, author=curr_user)
            a.put()
            self.redirect('/blog/%s' % str(a.key.id()))
        else:
            error = "Subject and Content fields are required"
            self.render("newpost.html", subject=subject, content=content,
                        error=error, user=curr_user)

# Mapping of Handlers

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/signup', SignupPage),
                               ('/login', LoginPage),
                               ('/logout', LogoutPage),
                               ('/blog', BlogPage),
                               ('/blog/([0-9]+)', PostPage),
                               ('/comment/edit', EditComment),
                               ('/comment/delete', DeleteComment),
                               ('/edit', EditPost),
                               ('/delete', DeletePost),
                               ('/newpost', NewPostForm),
                               ('/blog_post', PostPage)], debug=True)
