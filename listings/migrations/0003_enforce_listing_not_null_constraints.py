# Generated manually to enforce NOT NULL constraints on Listing table
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0002_fix_photo_display_order_typo'),
    ]

    operations = [
        # First, ensure all existing listings have valid values (they should already)
        # Then alter the fields to be NOT NULL
        migrations.AlterField(
            model_name='listing',
            name='created_by',
            field=models.ForeignKey(
                db_column='Created_by',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='listings',
                to='listings.user'
            ),
        ),
        migrations.AlterField(
            model_name='listing',
            name='property_type',
            field=models.ForeignKey(
                db_column='Property_Type_ID',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='listings',
                to='listings.propertytype'
            ),
        ),
        migrations.AlterField(
            model_name='listing',
            name='neighborhood',
            field=models.ForeignKey(
                db_column='Neighborhood_ID',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='listings',
                to='listings.neighborhood'
            ),
        ),
    ]

