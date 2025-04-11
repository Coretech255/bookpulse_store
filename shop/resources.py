from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Rating, Product, CustomUser
import logging


logger = logging.getLogger(__name__)

class RatingResource(resources.ModelResource):
    # Define the field for ForeignKey to Product
    #print('entered Rating Resource')
    product = fields.Field(
        column_name='isbn',  # CSV column name for the foreign key to Product
        attribute='product',  # Model attribute
        widget=ForeignKeyWidget(Product, 'isbn')  # Use ForeignKeyWidget with 'isbn' field
    )
    
    # Define the field for ForeignKey to CustomUser
    user = fields.Field(
        column_name='user_id',  # CSV column name for the foreign key to CustomUser
        attribute='user',  # Model attribute
        widget=ForeignKeyWidget(CustomUser, 'id')  # Use ForeignKeyWidget with 'email' field
    )

    def before_import_row(self, row, **kwargs):
        #print(f"Processing row with Product ISBN: {row['isbn']}")
        logger.info("done processing row with Product ISBN")
        #if not Product.objects.filter(isbn=row['isbn']).exists():
        #    print(f"Product with ISBN {row['isbn']} does not exist.")
        #    logger.error(f"Product with ISBN {row['isbn']} does not exist.")

    class Meta:
        model = Rating
        fields = ('user', 'product', 'rating', 'review',)
        export_order = ('user', 'product', 'rating', 'review',)
        import_id_fields = ['user', 'product']
        use_bulk = True  # Use bulk for non-ManyToMany fields
        batch_size = 500 

    #def get_import_id_fields(self):
    #    return ['user', 'product'] 
