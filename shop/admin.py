import logging
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
#from import_export.instance_loaders import CachedInstanceLoader
from users.models import CustomUser
from .models import Product, Category, Rating, Interaction
from .resources import RatingResource
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget

logger = logging.getLogger(__name__)

# In resources.py
class ProductResource(resources.ModelResource):
    categories = fields.Field(
        column_name='categories',
        attribute='categories',
        widget=ManyToManyWidget(Category, field='name', separator='|')
    )

    class Meta:
        model = Product
        import_id_fields = ('isbn',)  # Use ISBN as the unique identifier
        fields = ('isbn', 'title', 'author', 'description', 'categories', 'price', 'cover_photo_url', 'publication_date')

    def before_import_row(self, row, **kwargs):
        # Handle ManyToManyField assignment
        category_name = row["categories"]
        Category.objects.get_or_create(name=category_name, defaults={"name": category_name})

class ProductAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    # Customize how the user model is displayed on the admin dashboard
    resource_class = ProductResource
    list_display = ('title', 'isbn', 'price', 'publication_date')
    search_fields = ('title', 'author', 'isbn', 'publication_date')
    filter_horizontal = ()
    list_filter = ('author', 'publication_date',)
    fieldsets = ()
    ordering = ('title',)  # Specify a valid field for ordering, such as 'email'

# Register the Product model with the custom admin class
admin.site.register(Product, ProductAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description',)
admin.site.register(Category, CategoryAdmin)


class RatingAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_classes = [RatingResource] 
    list_display = ('id', 'get_user_full_name', 'get_product_isbn', 'rating', 'timestamp')
    list_filter = ('timestamp',)

    def get_user_full_name(self, obj):
        if obj.user:
            if obj.user.first_name and obj.user.last_name:
                return f"{obj.user.first_name} {obj.user.last_name}"
            return obj.user.email  # Fallback to username if names are missing
        return "No user"
    get_user_full_name.short_description = 'User'

    def get_product_isbn(self, obj):
        return obj.product.isbn
    get_product_isbn.short_description = 'Product ISBN'
    #list_display = ('user', 'product', 'rating', 'timestamp')
    #list_filter = ('timestamp',)



admin.site.register(Rating, RatingAdmin)

class InteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'liked', 'clicks',  'added_to_cart', 'timestamp')
    list_filter = ('timestamp',)

admin.site.register(Interaction, InteractionAdmin)
