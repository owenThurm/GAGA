from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from api.models import User

# Register your models here.

class UserAdminModel(UserAdmin):
  list_display = ('email', 'username', 'brand_name', 'date_joined',
                  'last_login', 'is_admin', 'is_staff')
  search_fields = ('email', 'username', 'brand_name')
  read_only = ('date_joined', 'last_login')

  filter_horizontal = ()
  list_filter = ()
  fieldsets = ()

admin.site.register(User, UserAdminModel)

