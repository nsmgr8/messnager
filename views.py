import logging

# appengine import
from google.appengine.api import users
from google.appengine.ext import webapp

# my imports
from utils import render, paginate
from models import roles
from models import Member, Meal
from forms import MemberForm, MealForm

class Members(webapp.RequestHandler):
    def get(self):
        members = Member.all().order('nick')
        params = paginate(members, self, name="members")#, cache_key="main_page")
        render(self, "member_list.html", params)

class CreateMember(webapp.RequestHandler):
    @Member.role('admin')
    def get(self):
        form = MemberForm()
        render(self, "member_add.html", {'form':form})

    @Member.role('admin')
    def post(self):
        form = MemberForm(data=self.request.POST)
        if form.is_valid():
            entity = form.save(commit=False)
            entity.put()
        self.redirect('/member/')

class EditMember(webapp.RequestHandler):
    @Member.role('admin')
    def get(self, key):
        member = Member.get(key)
        if not member:
            self.redirect('/member/')
            return
        form = MemberForm(instance=member)
        render(self, "member_edit.html", {'form':form})

    @Member.role('admin')
    def post(self, key):
        member = Member.get(key)
        if not member:
            self.redirect('/member/')
            return
        form = MemberForm(data=self.request.POST, instance=member)
        if form.is_valid():
            entity = form.save(commit=False)
            entity.put()
        self.redirect('/member/')

class DeleteMember(webapp.RequestHandler):
    @Member.role('admin')
    def get(self, key):
        member = Member.get(key)
        if member:
            if not member.user == users.get_current_user():
                logging.info("deleting member %s" % member.nick)
                member.delete()
        self.redirect('/member/')

class Register(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            self.redirect('/')
            return

        user = users.User()
        if users.is_current_user_admin():
            key_name = "site_admin_%s" % user
            Member.get_or_insert(key_name,
                                 user=user,
                                 email=user.email(),
                                 nick=user.nickname(),
                                 role_id=roles['Admin'])
            self.redirect('/member/')
            return

        member = Member.all().filter('user', user).get()
        if not member:
            member = Member.all().filter('email', user.email()).get()
            if member:
                member.user = user
                member.put()
            else:
                logging.info('User %s not allowed' % users.get_current_user())
                self.redirect(users.create_logout_url("/member/"))
                return

        self.redirect('/member/')
        return

class ManageMeal(webapp.RequestHandler):
    def get(self):
        members = Member.all().order('nick')
        forms = []
        for member in members:
            form = MealForm(data={'member':member.key()})
            data = {
                'member': member,
                'meal': form,
            }
            forms.append(data)
        params = {
            'forms': forms,
        }
        render(self, "manage_meal.html", params)

    def post(self):
        print self.request.POST
