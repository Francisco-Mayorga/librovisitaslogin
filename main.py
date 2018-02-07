#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import jinja2
import webapp2
from models import Message
from google.appengine.api import users



template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if params is None:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            logged_in = True
            logout_url = users.create_logout_url('/')

            params = {"logged_in": logged_in, "logout_url": logout_url, "user": user}
        else:
            logged_in = False
            login_url = users.create_login_url('/')

            params = {"logged_in": logged_in, "login_url": login_url, "user": user}

        return self.render_template("hello.html", params=params)

class AdminHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            if users.is_current_user_admin():
                self.response.write('You are an administrator.')
            else:
                self.response.write('You are not an administrator.')
        else:
            self.response.write('You are not logged in.')

class ResultHandler(BaseHandler):
    def post(self):
        user = users.get_current_user()
        nombre = self.request.get("nombre")
        email = user.email()
        texto = self.request.get("texto")

        if not nombre:
            nombre = u"anónimo"

        msg = Message(nombre=nombre, email=email, texto=texto)
        msg.put()

        params = {"nombre": nombre, "email": email, "texto": texto}
        return self.render_template("result.html", params=params)

class MessageListHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            logged_in = True
            logout_url = users.create_logout_url('/')

            params = {"logged_in": logged_in, "logout_url": logout_url, "user": user}
        else:
            return self.redirect_to("index")

        messages = Message.query(Message.deleted == False).fetch()
        params["messages"]= messages
        return self.render_template("message_list.html", params=params)

class MessageDetailsHandler(BaseHandler):
    def get(self, message_id):
        user = users.get_current_user()

        if user:
            logged_in = True
            logout_url = users.create_logout_url('/')

            params = {"logged_in": logged_in, "logout_url": logout_url, "user": user}
        else:
            return self.redirect_to("index")
        message = Message.get_by_id(int(message_id))
        params["message"] = message
        return self.render_template("message_details.html", params=params)

class EditMessageHandler(BaseHandler):
    def get(self, message_id):
        if not users.is_current_user_admin():
            return self.write("You are not admin")

        message = Message.get_by_id(int(message_id))
        context = {
            "message": message,
        }
        return self.render_template("message_edit.html", params=context)

    def post(self, message_id):
        nombre = self.request.get("nombre")
        email = self.request.get("email")
        texto = self.request.get("texto")
        message = Message.get_by_id(int(message_id))
        message.nombre = nombre
        message.email = email
        message.texto = texto
        message.put()
        return self.redirect_to("msg-list")

class DeleteMessageHandler(BaseHandler):
    def get(self, message_id):
        if not users.is_current_user_admin():
            return self.write("You are not admin")

        message = Message.get_by_id(int(message_id))
        context = {
            "message": message,
        }
        return self.render_template("message_delete.html", params=context)

    def post(self, message_id):
        message = Message.get_by_id(int(message_id))
        message.deleted = True
        message.put()
        return self.redirect_to("msg-list")

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name="index"),
    webapp2.Route('/admin', AdminHandler),
    webapp2.Route('/result', ResultHandler),
    webapp2.Route('/message_list', MessageListHandler, name="msg-list"),
    webapp2.Route('/message/<message_id:\d+>/details', MessageDetailsHandler),
    webapp2.Route('/message/<message_id:\d+>/edit', EditMessageHandler),
    webapp2.Route('/message/<message_id:\d+>/delete', DeleteMessageHandler),

], debug=True)
