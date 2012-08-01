import re
import os
import random
import hashlib
import logging
from string import letters

import jinja2
import webapp2

#from file import class
from jinja_utilities import *
from user_utilities import *
from models import Post
from models import User

from google.appengine.ext import db


class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
    
    def render_json(self, d):
        json_txt = json.dumps(d)
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.write(json_txt)

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))
        
        if self.request.url.endswith('.json'):
            self.format = 'json'
        else:
            self.format = 'html'         
        
class Signup(BlogHandler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username,
                      email = self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError
    
        
class Register(Signup):
    def done(self):
        #make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username = msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/')

class Login(BlogHandler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)

class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/')
        
def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

      
class MainPage(BlogHandler):
    def get(self):
        self.render('index.html')
    
    def post(self):
        email = self.request.get('email')
        product = self.request.get('product')

        if email and product:
            p = Post(parent = blog_key(), email = email, product = product)
            p.put()
            self.redirect('/profile?email=' + email + '&product=' + product)
        else:
            error = "product and email, please!"
            self.render("index.html", email = email, product = product, error=error)
            
class Profile(BlogHandler):
    def get(self):
        email = self.request.get('email')
        product = self.request.get('product')
        product_list = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 10")
        self.render('profile.html', email = email, product = product, product_list = product_list)
        
        
        


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/profile', Profile)
                               ],
                              debug=True)

#compare the results to current "Post" entrys in the db and return matches


#questions for henry
#how to seperate out login/register stuff into a seperate module?
#how to use gaesessions to authenticate users and display content based on the user
#essentially private profiles
#this also means i need to tag each Post entity in the db by the user so i know which to display
#compare the results to current "Post" entrys in the db and return matches
#iterate over a bunch of groupon deals and build a dictionary or GQL entity
#set up cron jobs to update this every so often
#compare the results to current "Post" entrys in the db and return matches