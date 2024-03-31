from django.db.models import Prefetch, Manager, Q, Count

from forum.models import Discussion, CustomUser, Comments, Specializations, UserDescription, UserEvents, Friendship, \
    Culprits, InterlocutionTags, DiscussionTags, DiscussionGrades, DiscussionComments, CommentsRating


def only_objects_decorator(func: callable):  # decorator for only
    def only_return_wrapper(objects, only=(), *args, **kwargs):
        return func(objects, *args, **kwargs).only(*only)
    return only_return_wrapper


def order_objects_decorator(func: callable):  # decorator for order_by
    def only_return_wrapper(objects, ordered_by=(), *args, **kwargs):
        return func(objects, *args, **kwargs).order_by(*ordered_by)
    return only_return_wrapper


def filter_objects_decorator(func: callable):  # decorator for filter
    def only_return_wrapper(objects, filters={}, *args, **kwargs):
        return func(objects, *args, **kwargs).filter(**filters)
    return only_return_wrapper


def exclude_objects_decorator(func: callable):  # decorator for exclude
    def only_return_wrapper(objects, excludes={}, *args, **kwargs):
        return func(objects, *args, **kwargs).filter(**excludes)
    return only_return_wrapper


def select_related_decorator(func: callable):  # decorator for select_related
    def only_return_wrapper(objects, related_selects=(), *args, **kwargs):
        return func(objects, *args, **kwargs).select_related(*related_selects)
    return only_return_wrapper


def prefetch_related_decorator(func: callable):  # decorator for prefetch_related
    def only_return_wrapper(objects, related_prefetch=(), *args, **kwargs):
        return func(objects, *args, **kwargs).prefetch_related(*related_prefetch)
    return only_return_wrapper


@only_objects_decorator
@order_objects_decorator
@filter_objects_decorator
@exclude_objects_decorator
@select_related_decorator
@prefetch_related_decorator
def main_layout(objects: Manager, **kwargs):  # main layout for different cases
    return objects


def get_several_filtered_ordered_discussions(search_request):  # getting first ten discussions in short search
    return main_layout(objects=Discussion.objects, only=('id', 'theme',), ordered_by=('theme',),
                       filters={'theme__icontains': search_request})[:10]


def get_several_filtered_ordered_users(search_request):  # getting first ten users in short search
    return main_layout(objects=CustomUser.objects, only=('id', 'username',), ordered_by=('username',),
                       filters={'username__icontains': search_request})[:10]


def get_comments_filtered_ordered(user_id):
    return main_layout(objects=Comments.objects, only=('id', 'upload_date', 'comment', 'rating', 'dda_id'),
                       ordered_by=('-id',), filters={'author_id': user_id})


def get_profile_info(profile_id):
    user_des = Prefetch('userdescription', queryset=main_layout(objects=UserDescription.objects, only=(
        'id', 'sex', 'birth_date', 'political_orientation', 'art_style', 'ideology', 'credo', 'description',
        'user_id')))
    user_spec = Prefetch('userspecializations_set__specialization', queryset=Specializations.objects.all())
    queryset = CustomUser.objects.filter(id=profile_id).prefetch_related(user_des, 'userspecializations_set',
                                                                         user_spec).only('id', 'username', 'avatar',
                                                                                         'level', 'date_joined')
    return queryset


def get_friendship_event_check(receiver_id, sender_id):  # checking for friendship request
    event = UserEvents.Requests.INVITE_FRIENDSHIP
    return UserEvents.objects.filter(Q(event=event, receiver_id=receiver_id, sender_id=sender_id)
                                     | Q(event=event, receiver_id=sender_id, sender_id=receiver_id)).exists()


def get_friendship_check(receiver_id, sender_id):  # checking for friendship link
    return Friendship.objects.filter(Q(user1=receiver_id, user2=sender_id) |
                                     Q(user1=sender_id, user2=receiver_id)).exists()


def get_event_check(event, profile_id, sender_id):
    return UserEvents.objects.filter(event=event, receiver_id=profile_id, sender_id=sender_id).exists()


def get_event(event, profile_id, sender_id):
    return UserEvents.objects.get(event=event, receiver_id=profile_id, sender_id=sender_id)


def get_friendship(user_id, friend_id):  # getting specific friend
    return Friendship.objects.get(Q(user1_id=user_id, user2_id=friend_id) | Q(user1_id=friend_id, user2_id=user_id))


def create_friendship_event(receiver_id, sender_id):  # creating friendship request
    return UserEvents.objects.create(event=UserEvents.Requests.INVITE_FRIENDSHIP, sender_id=sender_id,
                                     receiver_id=receiver_id)


def get_friendship_link(user_id):  # checking for friendship connection
    return Friendship.objects.filter(Q(user1_id=user_id) | Q(user2_id=user_id))


def get_user_friends(related_user_ids):  # getting user friends (connection may vary)
    return main_layout(objects=CustomUser.objects, only=('id', 'username', 'avatar'), ordered_by=('-username',),
                       filters={'id__in': related_user_ids})


def get_user_bans(user_id):
    return main_layout(objects=Culprits.objects, ordered_by=('-id',), filters={'user_id': user_id})


def get_user_events(user_id):
    return UserEvents.objects.filter(receiver_id=user_id).order_by('-id').select_related('sender').prefetch_related(
        Prefetch('sender__userdescription', queryset=UserDescription.objects.only('sex'))
    ).only('id', 'event', 'sender__id', 'sender__username', 'sender__avatar', 'sender__userdescription__sex')


def get_user_discussions(author_id):
    return main_layout(objects=Discussion.objects, only=('id', 'rating', 'creation_date', 'theme'), ordered_by=('-id',),
                       filters={'creator_id': author_id})


def get_specializations_and_tags():
    return Specializations.objects.prefetch_related('interlocutiontags_set')


"""DiscussionsPage p_inc == 0 and p_exc == 0"""


def get_custom_discussion(queryset):  # getting discussions when tags_inc == 0 and tags_exc == 0
    return queryset.prefetch_related('discussiontags_set__tag')


def get_custom_discussion_inc_exc(queryset, tags_included,
                                  tags_excluded):  # getting discussions when tags_inc != 0 and tags_exc != 0
    queryset = queryset.filter(discussiontags__tag__in=tags_included).annotate(
        num_tags=Count('discussiontags')).filter(num_tags=len(tags_included)).distinct()
    return queryset.exclude(discussiontags__tag__in=tags_excluded)


def get_custom_discussion_inc(queryset, tags_included):  # getting discussions when tags_inc != 0 and tags_exc == 0
    return queryset.filter(discussiontags__tag__in=tags_included).distinct().annotate(
        num_tags=Count('discussiontags')).filter(num_tags=len(tags_included))


def get_custom_discussion_exc(queryset, tags_excluded):  # getting discussions when tags_inc == 0 and tags_exc != 0
    return queryset.exclude(discussiontags__tag__in=tags_excluded)


"""DiscussionsPage p_inc != 0 and p_exc != 0"""


def get_custom_discussion_p_inc_p_exc(queryset, p_orient_included,
                                      p_orient_excluded):  # getting discussions when p_inc != 0 and p_inc != 0
    return queryset.prefetch_related(
        Prefetch('creator__userdescription', queryset=UserDescription.objects.only('political_orientation')),
        Prefetch('discussiontags_set__tag', queryset=InterlocutionTags.objects.all())
    ).filter(creator__userdescription__political_orientation__in=p_orient_included).distinct().exclude(
        creator__userdescription__political_orientation__in=p_orient_excluded)


def get_custom_discussion_p_inc_p_exc_inc_exc(queryset, tags_included,
                                              tags_excluded):  # getting discussions when tags_inc != 0 and tags_exc != 0
    return queryset.filter(discussiontags__tag__in=tags_included).annotate(
        num_tags=Count('discussiontags')).filter(num_tags=len(tags_included)).distinct().exclude(
        discussiontags__tag__in=tags_excluded)


def get_custom_discussion_p_inc_p_exc_inc(queryset,
                                          tags_included):  # getting discussions when tags_inc != 0 and tags_exc == 0
    return queryset.filter(discussiontags__tag__in=tags_included).annotate(
        num_tags=Count('discussiontags')).filter(num_tags=len(tags_included)).distinct()


def get_custom_discussion_p_inc_p_exc_exc(queryset,
                                          tags_excluded):  # getting discussions when tags_inc == 0 and tags_exc != 0
    return queryset.exclude(discussiontags__tag__in=tags_excluded).annotate(
        num_tags=Count('discussiontags')).exclude(num_tags=len(tags_excluded)).distinct()


"""DiscussionsPage p_inc == 0"""


def get_custom_discussion_p_inc(queryset, p_orient_excluded):  # getting discussions when p_inc != 0 and p_inc != 0
    return queryset.prefetch_related(
        Prefetch('creator__userdescription', queryset=UserDescription.objects.only('political_orientation')),
        Prefetch('discussiontags_set__tag', queryset=InterlocutionTags.objects.all())
    ).exclude(creator__userdescription__political_orientation__in=p_orient_excluded)


def get_custom_discussion_p_inc_inc_exc(queryset, tags_included,
                                        tags_excluded):  # getting discussions when tags_inc != 0 and tags_exc != 0
    return queryset.filter(discussiontags__tag__in=tags_included).annotate(
        num_tags=Count('discussiontags')).filter(num_tags=len(tags_included)).distinct().exclude(
        discussiontags__tag__in=tags_excluded)


def get_custom_discussion_p_inc_inc(queryset,
                                    tags_included):  # getting discussions when tags_inc != 0 and tags_exc == 0
    return queryset.filter(discussiontags__tag__in=tags_included).annotate(
        num_tags=Count('discussiontags')).filter(num_tags=len(tags_included)).distinct()


def get_custom_discussion_p_inc_exc(queryset,
                                    tags_excluded):  # getting discussions when tags_inc == 0 and tags_exc != 0
    return queryset.exclude(discussiontags__tag__in=tags_excluded).annotate(
        num_tags=Count('discussiontags')).exclude(num_tags=len(tags_excluded)).distinct()


"""DiscussionsPage p_exc == 0"""


def get_custom_discussion_p_exc(queryset, p_orient_included):  # getting discussions when p_inc != 0 and p_inc != 0
    return queryset.prefetch_related(
        Prefetch('creator__userdescription', queryset=UserDescription.objects.only('political_orientation')),
        Prefetch('discussiontags_set__tag', queryset=InterlocutionTags.objects.all())
    ).filter(creator__userdescription__political_orientation__in=p_orient_included).distinct()


def get_custom_discussion_p_exc_inc_exc(queryset, tags_included,
                                        tags_excluded):  # getting discussions when tags_inc != 0 and tags_exc != 0
    return queryset.filter(discussiontags__tag__in=tags_included).annotate(
        num_tags=Count('discussiontags')).filter(num_tags=len(tags_included)).distinct().exclude(
        discussiontags__tag__in=tags_excluded)


def get_custom_discussion_p_exc_inc(queryset,
                                    tags_included):  # getting discussions when tags_inc != 0 and tags_exc == 0
    return queryset.filter(discussiontags__tag__in=tags_included).annotate(
        num_tags=Count('discussiontags')).filter(num_tags=len(tags_included)).distinct()


def get_custom_discussion_p_exc_exc(queryset,
                                    tags_excluded):  # getting discussions when tags_inc == 0 and tags_exc != 0
    return queryset.exclude(discussiontags__tag__in=tags_excluded).annotate(
        num_tags=Count('discussiontags')).exclude(num_tags=len(tags_excluded)).distinct()


"""###"""


def get_discussion_by_user(discussion_id, grader_id):  # authorship checkicng
    return main_layout(objects=Discussion.objects, filters={'id': discussion_id}, excludes={'creator_id': grader_id})


def get_discussion_objects_by_id(discussion_id):
    return Discussion.objects.get(id=discussion_id)


def get_discussion_grade_check(discussion_id, grader_id):
    return main_layout(objects=DiscussionGrades.objects, filters={'discussion_id': discussion_id,
                                                                  'user_id': grader_id}).exists()


def get_comments_grade_check(comment_id, grader_id):
    return main_layout(objects=Comments.objects, filters={'id': comment_id}, excludes={'author_id': grader_id}).exists()


def get_user_comment(comment_id):
    return Comments.objects.get(id=comment_id)


def get_comment_by_user(comment_id, grader_id):  # authorship checking
    return main_layout(objects=CommentsRating.objects,
                       filters={'comment_id': comment_id, 'user_id': grader_id}).exists()


def get_comments_for_discussion(dda_id):
    comments = DiscussionComments.objects.select_related('comment', 'comment__author', 'comment__parent_comment',
                                                         'comment__parent_comment__author')
    comments = comments.only('id', 'comment__id', 'comment__upload_date', 'comment__comment', 'comment__rating',
                             'comment__author__avatar',
                             'comment__author__username', 'comment__parent_comment__author__username').filter(
        DDA_id=dda_id).order_by('id')
    return comments


def get_discussion_data(discussion_id):
    return Discussion.objects.select_related('creator').only('id', 'theme', 'content', 'creation_date',
                                                             'creator__username').filter(id=discussion_id)


# DiscussionCreatePage
def get_values_list_tags():
    return InterlocutionTags.objects.values_list('id', flat=True)


def get_all_tags():
    return InterlocutionTags.objects.only('id', 'name').all()


def get_p_orient_choices():
    return UserDescription.UserPoliticalOrientation.choices


def get_discussion_grade(discussion_id, grader_id):
    return DiscussionGrades.objects.get(discussion_id=discussion_id, user_id=grader_id)


def get_comment_grade(comment_id, grader_id):
    return CommentsRating.objects.get(comment_id=comment_id, user_id=grader_id)


def get_comment_check(comment_id, dda_id, request_id):
    return Comments.objects.filter(id=comment_id, dda_id=dda_id, author_id=request_id).exists()


def get_discussion_comment(comment_id, dda_id, request_id):
    return Comments.objects.get(id=comment_id, dda_id=dda_id, author_id=request_id)


def get_comment_by_id_dda_id(comment_id, dda_id):
    return Comments.objects.filter(id=comment_id, dda_id=dda_id).exists()


def get_comment_advanced(replied_text, dda_id, request_id, comment_id):
    return Comments(comment=replied_text, dda_id=dda_id, author_id=request_id, parent_comment_id=comment_id)


def get_discussion_comments_by_id(dda_id, comment_id):
    return DiscussionComments(DDA_id=dda_id, comment_id=comment_id)


def object_create_comment(comment_text, dda_id, request_id):
    return Comments(comment=comment_text, dda_id=dda_id, author_id=request_id)


def create_friendship(sender_id, profile_id):
    Friendship(user1_id=sender_id, user2_id=profile_id).save()


def create_grade_for_discussion(user_grade: str, discussion_id, grader_id):
    DiscussionGrades.objects.create(user_grade=user_grade, discussion_id=discussion_id, user_id=grader_id)


def create_grade_for_comment(user_grade: str, comment_id, grader_id):
    CommentsRating.objects.create(user_grade=user_grade, comment_id=comment_id, user_id=grader_id)


def create_bulk_discussion_tags(dda_id, valid_tags):
    DiscussionTags.objects.bulk_create([DiscussionTags(DDA_id=dda_id, tag_id=tag_id) for tag_id in valid_tags])
