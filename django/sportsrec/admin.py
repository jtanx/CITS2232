from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.admin import User
from sportsrec.models import Contact, SiteUser, Member, Club, Membership

class SiteUserInline(admin.StackedInline):
    model = SiteUser
    can_delete = False
    verbose_name_plural = 'siteuser'

class UserAdmin(UserAdmin):
    inlines = (SiteUserInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Contact)
admin.site.register(Member)
admin.site.register(Club)
admin.site.register(Membership)
