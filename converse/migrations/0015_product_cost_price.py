# Generated by Django 4.2.9 on 2024-03-17 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('converse', '0014_alter_user_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='cost_price',
            field=models.IntegerField(default=0),
        ),
    ]