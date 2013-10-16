from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.admin import User
from django.contrib.auth.models import Group
from sportsrec.models import *

#class SiteUserInline(admin.StackedInline):
#    model = SiteUser
#    can_delete = False
#    verbose_name_plural = 'siteuser'

#class UserAdmin(UserAdmin):
#    inlines = (SiteUserInline, )

#admin.site.unregister(User)
#admin.site.register(User, UserAdmin)
#admin.site.register(Contact)

admin.site.register(Member)
admin.site.register(Club)
admin.site.register(Membership)
admin.site.register(ClubType)
admin.site.register(ClubTag)
#admin.site.register(UserMeta)


def is_admin(user):
    group = Group.objects.get(name="End Admin")

    if group in user.groups.all():
        return True
    return False
