# Generated by Django 4.2.9 on 2024-03-13 09:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('converse', '0011_rename_order_id_oderdetails_order_alter_order_status'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='OderDetails',
            new_name='OrderDetails',
        ),
    ]