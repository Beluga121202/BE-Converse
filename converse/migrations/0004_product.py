# Generated by Django 4.2.9 on 2024-01-25 02:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('converse', '0003_user_birthday_user_birthday_dayofyear_internal_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_type', models.CharField(default='', max_length=255)),
                ('product_id', models.CharField(default='', max_length=255)),
                ('product_name', models.CharField(default='', max_length=255)),
                ('img', models.ImageField(blank=True, null=True, upload_to='images/')),
                ('quantity', models.IntegerField(default=0)),
                ('price', models.IntegerField(default=0)),
                ('discount', models.IntegerField(default=0)),
                ('place', models.CharField(default='', max_length=255)),
                ('product_line', models.CharField(default='', max_length=255)),
            ],
        ),
    ]
