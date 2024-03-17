# Generated by Django 4.2.9 on 2024-03-12 15:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('converse', '0007_product_color'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.CharField(default='', max_length=255, primary_key=True, serialize=False)),
                ('user', models.CharField(default='', max_length=255)),
                ('email', models.EmailField(blank=True, default='', max_length=254)),
                ('phone', models.CharField(default='', max_length=255)),
                ('shipping_address', models.CharField(default='', max_length=255)),
                ('total_price', models.IntegerField(default=0)),
                ('status', models.CharField(default='', max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='OderDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
                ('price', models.IntegerField(default=0)),
                ('order_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='converse.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='converse.product')),
            ],
        ),
    ]
