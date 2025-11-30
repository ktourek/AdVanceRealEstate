# Generated migration for adding thumbnail_data field to Photo model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0004_omahalocation'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='thumbnail_data',
            field=models.BinaryField(blank=True, db_column='Thumbnail_Data', null=True),
        ),
    ]
