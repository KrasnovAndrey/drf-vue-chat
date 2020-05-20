# Generated by Django 3.0.5 on 2020-05-13 08:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0007_auto_20200510_1123'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatsessionmessage',
            name='isRead',
        ),
        migrations.CreateModel(
            name='Reader',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isRead', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='readers', to='chat.ChatSessionMessage')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
