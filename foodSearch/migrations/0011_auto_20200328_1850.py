# Generated by Django 3.0.3 on 2020-03-28 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodSearch', '0010_auto_20200303_1049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=200, unique=True, verbose_name='Nom'),
        ),
    ]
