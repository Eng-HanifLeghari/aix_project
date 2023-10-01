from django.contrib import admin
from .models import User, UserProfile, UserRoles
from ..data_source.models import AIServices

# Register your models here.
#
# from django.contrib import admin
# from django.customutils.translation import gettext_lazy as _
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
#
# from .models import User, UserProfile
#
#
# class UserProfileInline(admin.StackedInline):
#     model = UserProfile
#     can_delete = False
#     verbose_name_plural = 'UserProfile'
#
#     fields = ('username', 'email', 'first_name', 'last_name', 'age', 'city', 'state')
#
#
# @admin.register(User)
# class UserAdmin(BaseUserAdmin):
#     inlines = [
#         UserProfileInline
#     ]
#     fieldsets = (
#         (None, {'fields': ('email', 'password')}),
#         (_('Personal info'), {'fields': ('first_name', 'last_name')}),
#         (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
#                                        'groups', 'user_permissions')}),
#         (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
#     )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'password1', 'password2'),
#         }),
#     )
#     # list_display = ('email', 'first_name', 'last_name', 'is_staff')
#     search_fields = ('email', 'first_name', 'last_name')
#     ordering = ('email',)
#
#
admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(UserRoles)
admin.site.register(AIServices)
# admin.site.register(User, UserAdmin)
