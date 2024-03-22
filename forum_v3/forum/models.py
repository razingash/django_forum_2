from datetime import date, timedelta
from PIL import Image
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator, MinLengthValidator
from django.db import models
from django.db.models import UniqueConstraint, Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
import re


def user_avatar_upload(instance, filename):
    filename = 'avatar' + re.search(r'\.(.*)', filename)[0]
    return f'user/{instance.pk}/avatar/{filename}'

def validate_file_size(value):
    max_size = 2 * 512 * 512
    if value.size > max_size:
        raise ValidationError(f'''Maximum file size mustn\'t exceed {max_size} bytes.''')

def validate_image_size(image):
    required_width = 512
    required_height = 512
    img = Image.open(image)
    (width, height) = img.size
    if width > required_width or height > required_height:
        raise ValidationError(f'''Image mustn\'t be more {required_width}x{required_height} pixels.''')
    if width != height:
        raise ValidationError('Image must be square')


def validator_birth_date():
    min_date = date.today() - timedelta(days=90 * 365.25)
    max_date = date.today() - timedelta(days=13 * 365.25)
    return [MinValueValidator(limit_value=min_date), MaxValueValidator(limit_value=max_date)]


def validator_aviability():
    return [MinValueValidator(limit_value=0), MaxValueValidator(limit_value=99)]


def validator_user_vote():
    return [MinValueValidator(limit_value=-1), MaxValueValidator(limit_value=1)]


def default_sent_time():
    return timezone.now().replace(second=0, microsecond=0)


class CustomUser(AbstractUser):
    class UserMainRole(models.TextChoices):
        SUPERADMIN = 'superadmin', 'Superadmin'
        ADMIN = 'admin', 'Admin'
        MODERATOR = 'moderator', 'Moderator'
        USER = 'user', 'User'

    class UserStatusChoices(models.TextChoices):
        FREE = 'free', 'Free'
        MUTED = 'muted', 'Muted'
        SILENCED = 'silenced', 'Silenced'
        BANNED = 'banned', 'Banned'

    avatar = models.ImageField(upload_to=user_avatar_upload, null=True, blank=True,
                               validators=[validate_file_size, validate_image_size,
                                           FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    role = models.CharField(max_length=30, choices=UserMainRole.choices, default=UserMainRole.USER)
    level = models.PositiveSmallIntegerField(default=0, null=False)
    status = models.CharField(max_length=30, choices=UserStatusChoices.choices,
                              default=UserStatusChoices.FREE, verbose_name='User Status')

    def get_absolute_url(self):
        return reverse('profile', kwargs={'profile_id': self.pk})

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'custom_user'
        constraints = [
            UniqueConstraint(fields=['username'], name='unique_customuser_username'),
            UniqueConstraint(fields=['email'], name='unique_customuser_email')
        ]


class UserDescription(models.Model):
    class UserSex(models.TextChoices):
        UNDEFINED = 'undefinded', 'Undefined'
        MAN = 'man', 'Man'
        WOMAN = 'woman', 'Woman'

    class UserPoliticalOrientation(models.TextChoices):
        UNDEFINED = '0', 'Undefined'
        LEFT_CENTERISTS = '1', 'Left-centerists'
        RIGHT_CENTERISTS = '2', 'Right-centerists'
        LEFT = '3', 'Left'
        RIGHT = '4', 'Right'
        LIBERTARIANS = '5', 'Libertarians'
        AUTHORITARIAN = '6', 'Authoritarian'
        LEFT_LIBERTARIANS = '7', 'Left libertarians'

    class UserFavouriteArtStyle(models.TextChoices):
        UNDEFINED = '0', 'Undefined'
        GOTHIC = '1', 'Gothic'
        RENAISSANCE = '2', 'Renaissance'
        BAROQUE = '3', 'Baroque'
        ROCOCO = '4', 'Rococo'
        CLASSICISM = '5', 'Classicism'
        IMPRESSIONISM = '6', 'Impressionism'
        EXPRESSIONISM = '7', 'Expressionism'
        ABSTRACTIONISM = '8', 'Abstractionism'
        CUBISM = '9', 'Cubism'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sex = models.CharField(choices=UserSex.choices, default=UserSex.UNDEFINED, max_length=10)
    birth_date = models.DateField(null=True, blank=True, validators=[validator_birth_date])
    political_orientation = models.CharField(choices=UserPoliticalOrientation.choices,
                                             default=UserPoliticalOrientation.UNDEFINED,
                                             max_length=20, verbose_name='Political orientation')
    art_style = models.CharField(choices=UserFavouriteArtStyle.choices, default=UserFavouriteArtStyle.UNDEFINED,
                                 max_length=20, verbose_name='Art style')
    ideology = models.CharField(max_length=50, null=True, blank=True)
    credo = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_user_description(sender, instance, created, **kwargs):
        if created:
            UserDescription.objects.create(user=instance)

    class Meta:
        db_table = 'dt_user_description'


class Specializations(models.Model):
    name = models.CharField(max_length=30, blank=False, null=False)

    class Meta:
        db_table = 'dt_specializations'



class UserSpecializations(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    specialization = models.ForeignKey(Specializations, on_delete=models.CASCADE)
    level_of_awareness = models.PositiveSmallIntegerField(default=1, verbose_name='level of awareness')
    experience = models.PositiveSmallIntegerField(default=0, null=True)

    @receiver(post_save, sender=CustomUser)
    def create_user_specializations(sender, instance, created, **kwargs):
        if created:
            specializations = Specializations.objects.all()
            user_specializations = [UserSpecializations(user=instance, specialization=spec) for spec in specializations]
            UserSpecializations.objects.bulk_create(user_specializations)

    class Meta:
        db_table = 'dt_user_specializations'


class Friendship(models.Model):
    user1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='connector')
    user2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='connected')

    class Meta:
        db_table = 'dt_user_friend'
        constraints = [
            models.UniqueConstraint(fields=['user1', 'user2'], name='unique_friendship_users')
        ]

    def clean(self):
        if Friendship.objects.filter(Q(user1=self.user2, user2=self.user1) | Q(user1=self.user1, user2=self.user2)).exists():
            raise ValidationError('This friendship already exists in reverse direction.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Messages(models.Model):
    friendship = models.ForeignKey(Friendship, on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='message_sender')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='message_receiver')
    message = models.CharField(max_length=300, validators=[MinLengthValidator(4)], blank=True, null=True)
    sent_time = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'dt_messages'


class UserEvents(models.Model):
    class Requests(models.TextChoices):
        INVITE_FRIENDSHIP = 'friendship', 'friendship'
        REPLY = 'reply', 'reply'
        NOTIFICATION = 'notification', 'notification'
        ADMIN_NOTIFICATION = 'admin notification', 'admin notification'

    event = models.CharField(choices=Requests.choices, max_length=30)
    event_start = models.DateField(auto_now_add=True)
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='event_receiver')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='event_sender', null=True)

    class Meta:
        db_table = 'dt_user_events'

class Culprits(models.Model):
    class ExecutionReason(models.TextChoices):
        REASON_1 = 'reason_1', 'reason_1'
        REASON_2 = 'reason_2', 'reason_2'
        REASON_3 = 'reason_3', 'reason_3'

    user = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    reason = models.CharField(choices=ExecutionReason.choices, max_length=10)
    durability_from = models.DateField(auto_now_add=True)
    durability_to = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'dt_culprits'


class Discussion(models.Model):
    class Visibility(models.TextChoices):
        EVERYONE = 'everyone', 'everyone'
        ADULTS = 'adults', 'adults'
        ILLUMINATED = 'illuminated', 'illuminated'
        ILLUMINATED_ADULTS = 'illuminated adults', 'illuminated adults'

    class Status(models.TextChoices):
        OPENED = 'opened', 'открыта'
        CLOSED = 'closed', 'закрыта'
        BANNED = 'banned', 'забанена'

    creator = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    visibility = models.CharField(choices=Visibility.choices, default=Visibility.ADULTS, max_length=30, blank=False)
    aviability_lvl = models.PositiveSmallIntegerField(default=1)
    rating = models.SmallIntegerField(default=0, null=True, blank=True)
    status = models.CharField(choices=Status.choices, default=Status.OPENED, max_length=30, blank=False, null=True)
    theme = models.CharField(max_length=90, validators=[MinLengthValidator(4)], blank=False, null=False)
    creation_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    content = models.CharField(max_length=700, validators=[MinLengthValidator(4)], blank=False, null=False)

    def get_absolute_url(self):
        return reverse('discussion', kwargs={'discussion_id': self.pk})

    class Meta:
        db_table = 'dt_discussion'


class DiscussionGrades(models.Model):
    class Rating(models.TextChoices):
        P = '1', '1'
        N = '0', '0'

    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    user_grade = models.CharField(choices=Rating.choices, max_length=1, blank=False, null=True)

    class Meta:
        db_table = 'dt_discussion_grades'


class InterlocutionTags(models.Model):
    name = models.CharField(max_length=30, blank=False, null=True)
    category = models.ForeignKey(Specializations, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'dt_interlocution_tags'


class DiscussionTags(models.Model):
    DDA = models.ForeignKey(Discussion, on_delete=models.CASCADE)
    tag = models.ForeignKey(InterlocutionTags, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'dt_discussion_tags'


class Comments(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    upload_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    comment = models.CharField(max_length=400, validators=[MinLengthValidator(3)], blank=False, null=False)
    rating = models.SmallIntegerField(default=0, blank=False, null=True)
    is_replied = models.BooleanField(default=False, blank=True, null=True)
    dda_id = models.PositiveIntegerField(blank=False, null=True)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies')

    class Meta:
        db_table = 'dt_comments'


class CommentsRating(models.Model):
    class Rating(models.TextChoices):
        P = '1', '1'
        N = '0', '0'

    comment = models.ForeignKey(Comments, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    user_grade = models.CharField(choices=Rating.choices, max_length=1, blank=False, null=True)

    class Meta:
        db_table = 'dt_comments_rating'
        constraints = [
            models.UniqueConstraint(fields=['comment', 'user'], name='unique_comments_rating')]#эту хуйню проверить

class DiscussionComments(models.Model):
    DDA = models.ForeignKey(Discussion, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comments, on_delete=models.CASCADE)

    class Meta:
        db_table = 'dt_discussion_comments'

