# Generated by Django 3.0.8 on 2020-08-12 10:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_auto_20200812_1546'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comments',
            name='comment_on',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_by_users', to='auctions.active_list'),
        ),
    ]