# Generated by Django 4.0.2 on 2022-02-09 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0004_alter_hzuserinfo_foto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hzuserinfo',
            name='foto',
            field=models.FileField(blank=True, null=True, upload_to='crm/media/foto/users/%Y/%m/%d/', verbose_name='Фотография'),
        ),
    ]
