from itertools import chain
from django import template
from forum.models import *
from django.db.models import Count, Q, F

register = template.Library()


@register.simple_tag()
def discussion_tags(discussion):
    category_map = {1: 'Nature', 2: 'Policy', 3: 'Science', 4: 'History', 5: 'Morality', 6: 'Philosophy'}
    tags_num = {category: 0 for category in category_map.values()}
    for tag in discussion:
        category_id = tag.tag.category_id
        key = category_map.get(category_id)
        if key:
            tags_num[key] += 1
    return tags_num


@register.simple_tag()
def is_my_friend_tag(profile, current_user):
    if profile == '' or current_user == '':
        return False
    friendship_exists = Friendship.objects.filter(
        Q(user1_id=profile, user2_id=current_user) | Q(user1_id=current_user, user2_id=profile)
    ).exists()
    return friendship_exists


@register.simple_tag()
def is_my_friend_got_request_tag(profile, current_user):
    if profile == '' or current_user == '':
        return False
    event = UserEvents.Requests.INVITE_FRIENDSHIP
    friendship_request_exists = UserEvents.objects.filter(
        Q(event=event, receiver_id=profile, sender_id=current_user) | Q(event=event, receiver_id=current_user, sender_id=profile)
    ).exists()
    return friendship_request_exists


discussion_tags = register.simple_tag(discussion_tags)
is_my_friend_tag = register.simple_tag(is_my_friend_tag)
