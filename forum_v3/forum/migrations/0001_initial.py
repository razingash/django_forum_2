# Generated by Django 4.2.11 on 2024-03-11 19:30

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import forum.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to=forum.models.user_avatar_upload, validators=[forum.models.validate_file_size, forum.models.validate_image_size, django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png'])])),
                ('role', models.CharField(choices=[('superadmin', 'Superadmin'), ('admin', 'Admin'), ('moderator', 'Moderator'), ('user', 'User')], default='user', max_length=30)),
                ('level', models.PositiveSmallIntegerField(default=0)),
                ('status', models.CharField(choices=[('free', 'Free'), ('muted', 'Muted'), ('silenced', 'Silenced'), ('banned', 'Banned')], default='free', max_length=30, verbose_name='User Status')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'custom_user',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
                ('comment', models.CharField(max_length=400, validators=[django.core.validators.MinLengthValidator(3)])),
                ('rating', models.SmallIntegerField(default=0, null=True)),
                ('is_replied', models.BooleanField(blank=True, default=False, null=True)),
                ('dda_id', models.PositiveIntegerField(null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('parent_comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='forum.comments')),
            ],
            options={
                'db_table': 'dt_comments',
            },
        ),
        migrations.CreateModel(
            name='Discussion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visibility', models.CharField(choices=[('everyone', 'everyone'), ('adults', 'adults'), ('illuminated', 'illuminated'), ('illuminated adults', 'illuminated adults')], default='adults', max_length=30)),
                ('aviability_lvl', models.PositiveSmallIntegerField(default=1)),
                ('rating', models.SmallIntegerField(blank=True, default=0, null=True)),
                ('status', models.CharField(choices=[('opened', 'открыта'), ('closed', 'закрыта'), ('banned', 'забанена')], default='opened', max_length=30, null=True)),
                ('theme', models.CharField(max_length=90, validators=[django.core.validators.MinLengthValidator(4)])),
                ('creation_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('content', models.CharField(max_length=700, validators=[django.core.validators.MinLengthValidator(4)])),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'dt_discussion',
            },
        ),
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connector', to=settings.AUTH_USER_MODEL)),
                ('user2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connected', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'dt_user_friend',
            },
        ),
        migrations.CreateModel(
            name='Specializations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'dt_specializations',
            },
        ),
        migrations.CreateModel(
            name='UserSpecializations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level_of_awareness', models.PositiveSmallIntegerField(default=1, verbose_name='level of awareness')),
                ('experience', models.PositiveSmallIntegerField(default=0, null=True)),
                ('specialization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum.specializations')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'dt_user_specializations',
            },
        ),
        migrations.CreateModel(
            name='UserEvents',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(choices=[('friendship', 'friendship'), ('reply', 'reply'), ('notification', 'notification'), ('admin notification', 'admin notification')], max_length=30)),
                ('event_start', models.DateField(auto_now_add=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_receiver', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='event_sender', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'dt_user_events',
            },
        ),
        migrations.CreateModel(
            name='UserDescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sex', models.CharField(choices=[('undefinded', 'Undefined'), ('man', 'Man'), ('woman', 'Woman')], default='undefinded', max_length=10)),
                ('birth_date', models.DateField(blank=True, null=True, validators=[forum.models.validator_birth_date])),
                ('political_orientation', models.CharField(choices=[('0', 'Undefined'), ('1', 'Left-centerists'), ('2', 'Right-centerists'), ('3', 'Left'), ('4', 'Right'), ('5', 'Libertarians'), ('6', 'Authoritarian'), ('7', 'Left libertarians')], default='0', max_length=20, verbose_name='Political orientation')),
                ('art_style', models.CharField(choices=[('0', 'Undefined'), ('1', 'Gothic'), ('2', 'Renaissance'), ('3', 'Baroque'), ('4', 'Rococo'), ('5', 'Classicism'), ('6', 'Impressionism'), ('7', 'Expressionism'), ('8', 'Abstractionism'), ('9', 'Cubism')], default='0', max_length=20, verbose_name='Art style')),
                ('ideology', models.CharField(blank=True, max_length=50, null=True)),
                ('credo', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'dt_user_description',
            },
        ),
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(blank=True, max_length=300, null=True, validators=[django.core.validators.MinLengthValidator(4)])),
                ('sent_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('friendship', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum.friendship')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_receiver', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_sender', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'dt_messages',
            },
        ),
        migrations.CreateModel(
            name='InterlocutionTags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum.specializations')),
            ],
            options={
                'db_table': 'dt_interlocution_tags',
            },
        ),
        migrations.CreateModel(
            name='DiscussionTags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('DDA', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum.discussion')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='forum.interlocutiontags')),
            ],
            options={
                'db_table': 'dt_discussion_tags',
            },
        ),
        migrations.CreateModel(
            name='DiscussionGrades',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_grade', models.CharField(choices=[('1', '1'), ('0', '0')], max_length=1, null=True)),
                ('discussion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum.discussion')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'dt_discussion_grades',
            },
        ),
        migrations.CreateModel(
            name='DiscussionComments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('DDA', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum.discussion')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum.comments')),
            ],
            options={
                'db_table': 'dt_discussion_comments',
            },
        ),
        migrations.CreateModel(
            name='Culprits',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(choices=[('reason_1', 'reason_1'), ('reason_2', 'reason_2'), ('reason_3', 'reason_3')], max_length=10)),
                ('durability_from', models.DateField(auto_now_add=True)),
                ('durability_to', models.DateField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'dt_culprits',
            },
        ),
        migrations.CreateModel(
            name='CommentsRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_grade', models.CharField(choices=[('1', '1'), ('0', '0')], max_length=1, null=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum.comments')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'dt_comments_rating',
            },
        ),
        migrations.AddConstraint(
            model_name='friendship',
            constraint=models.UniqueConstraint(fields=('user1', 'user2'), name='unique_friendship_users'),
        ),
        migrations.AddConstraint(
            model_name='commentsrating',
            constraint=models.UniqueConstraint(fields=('comment', 'user'), name='unique_comments_rating'),
        ),
        migrations.AddConstraint(
            model_name='customuser',
            constraint=models.UniqueConstraint(fields=('username',), name='unique_customuser_username'),
        ),
        migrations.AddConstraint(
            model_name='customuser',
            constraint=models.UniqueConstraint(fields=('email',), name='unique_customuser_email'),
        ),
    ]
