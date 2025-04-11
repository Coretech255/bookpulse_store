from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from django.utils.translation import gettext_lazy as _ 
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget


class CustomUserResource(resources.ModelResource):
    class Meta:
        model = CustomUser
        use_bulk = True  # Use bulk for non-ManyToMany fields
        batch_size = 500 



class CustomUserAdmin(ImportExportModelAdmin, UserAdmin):
    resource_class = CustomUserResource  # Use the custom resource class for bulk operations
    # Customize how the user model is displayed on the admin dashboard
    list_display = ('id', 'email', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name')
    filter_horizontal = ()
    list_filter = ()
        # Remove 'username' and add 'email' to the fieldsets
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'date_of_birth', 'phone_number', )}),
        (_('Permissions'), {'fields': ('is_staff', 'is_active')}),
    )

        # Add email and password to the add_fieldsets (when creating new users)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'date_of_birth', 'phone_number', 'is_staff', 'is_active')}
        ),
    )
    ordering = ('email',)  # Specify a valid field for ordering, such as 'email'

# Register the CustomUser model with the custom admin class
admin.site.register(CustomUser, CustomUserAdmin)
