# Generated by Django 3.0.5 on 2022-12-07 02:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blood', '0004_bloodrequest_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
