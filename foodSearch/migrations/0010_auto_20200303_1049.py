# Generated by Django 3.0.2 on 2020-03-03 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodSearch', '0009_auto_20200303_1046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image_small_url',
            field=models.URLField(),
        ),
        migrations.AlterField(
            model_name='product',
            name='image_url',
            field=models.URLField(),
        ),
        migrations.AlterField(
            model_name='product',
            name='url',
            field=models.URLField(),
        ),
    ]
