from itertools import chain
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.core.paginator import Paginator
from django.db.models import Prefetch, Q, Count
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView
from forum.forms import LoginCustomUserForm, RegisterCustomUserForm, ChangeCustomUserForm, \
    ChangeCustomUserDescriptionForm, ChangeCustomUserPasswordForm, CreateDiscussionForm
from forum.models import CustomUser, Specializations, UserDescription, Discussion, InterlocutionTags, \
    DiscussionComments, DiscussionTags, Friendship, Comments, Culprits, UserEvents, CommentsRating, DiscussionGrades
from forum.utils import DataMixin


class RulesPage(ListView, DataMixin):
    template_name = 'forum/rules.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            mix = self.get_user_context(title='Main Page', user_id=self.request.user.id)
        else:
            mix = self.get_user_context(title='Main Page')
        return context | mix

    def post(self, request, *args, **kwargs):
        print('POST request in header')
        print(request.POST)
        if request.POST.get('request_type') == 'discussions_search':
            print('discussion_search')
            search_request = request.POST.get('search_request')
            discussions = Discussion.objects.only('id', 'theme').order_by('theme').filter(
                theme__icontains=search_request)[:10]
            print(discussions)
            result = 'nothing founded'
            if len(discussions) > 0:
                result = [{'id': discussion.id, 'theme': discussion.theme, 'get_absolute_url': discussion.get_absolute_url()} for discussion in discussions]
            return JsonResponse({'message': result, 'type': 'result_discussions'})
        elif request.POST.get('request_type') == 'users_search':
            print('users_search')
            search_request = request.POST.get('search_request')
            users = CustomUser.objects.only('id', 'username').order_by('username').filter(
                username__icontains=search_request)[:10]
            result = 'nothing founded'
            if len(users) > 0:
                result = [{'id': user.id, 'username': user.username, 'get_absolute_url': user.get_absolute_url()} for user in users]
            return JsonResponse({'message': result, 'type': 'result_users'})
        else:
            return JsonResponse({'message': 'mistake'})

    def get_queryset(self):
        pass



class RegistrationPage(CreateView, DataMixin):
    form_class = RegisterCustomUserForm
    template_name = 'forum/register_page.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        mix = self.get_user_context(title='Registration')
        return context | mix

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')


class LoginPage(LoginView, DataMixin):
    template_name = 'forum/login_page.html'
    form_class = LoginCustomUserForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        mix = self.get_user_context(title='Login')
        return context | mix

    def get_success_url(self):
        return reverse_lazy('home')


class SettingsBasePage(LoginRequiredMixin, DataMixin, FormView):
    template_name = 'forum/settings.html'
    success_url = reverse_lazy('home')
    form_class = ChangeCustomUserForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            description_form = ChangeCustomUserDescriptionForm(instance=self.request.user.userdescription)
            mix = self.get_user_context(title='settings', user_id=self.request.user.id, description_form=description_form)
            context.update(mix)
            return context | mix

    def form_valid(self, form):
        form.save()
        description_instance = self.request.user.userdescription
        description_form = ChangeCustomUserDescriptionForm(self.request.POST, instance=description_instance)
        if description_form.is_valid():
            description_form.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    def get_object(self, queryset=None):
        return self.request.user


class SettingsPasswordPage(LoginRequiredMixin, PasswordChangeView, DataMixin):
    template_name = 'forum/settings_password.html'
    success_url = reverse_lazy('home')
    form_class = ChangeCustomUserPasswordForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            mix = self.get_user_context(title='password updating', user_id=self.request.user.id)
            return context | mix

    def get_object(self, queryset=None):
        return self.request.user


class ProfilePage(DetailView, DataMixin):
    model = CustomUser
    template_name = 'forum/profile_comments.html'
    context_object_name = 'user'
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('profile_id')
        comments = Comments.objects.only('id', 'upload_date', 'comment', 'rating', 'dda_id').filter(author_id=user_id)
        comments = comments.order_by('-id')

        paginator = Paginator(comments, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        if self.request.user.is_authenticated:
            mix = self.get_user_context(title='Profile', user_id=self.request.user.id, comments=page_obj)
        else:
            mix = self.get_user_context(title='Profile', comments=page_obj)
        return context | mix

    def get_object(self, queryset=None):
        profile_id = self.kwargs.get('profile_id')
        user_des = Prefetch('userdescription',
                            queryset=UserDescription.objects.only('id', 'sex', 'birth_date', 'political_orientation',
                                                                  'art_style', 'ideology', 'credo', 'description', 'user_id'))
        user_spec = Prefetch('userspecializations_set__specialization', queryset=Specializations.objects.all())
        queryset = CustomUser.objects.filter(id=profile_id).prefetch_related(user_des, 'userspecializations_set', user_spec).only('id', 'username', 'avatar', 'level', 'date_joined')
        return get_object_or_404(queryset)

    def post(self, request, *args, **kwargs):
        print('POST')
        if request.POST.get('event') == 'friendship':
            receiver_id = self.kwargs.get('profile_id')
            sender_id = request.POST.get('sender_id')
            print(sender_id, receiver_id)
            event = UserEvents.Requests.INVITE_FRIENDSHIP
            if not UserEvents.objects.filter(Q(event=event, receiver_id=receiver_id, sender_id=sender_id)
                                             | Q(event=event, receiver_id=sender_id, sender_id=receiver_id)).exists():
                if not Friendship.objects.filter(Q(user1=receiver_id, user2=sender_id) | Q(user1=sender_id, user2=receiver_id)).exists():
                    new = UserEvents.objects.create(event=event, sender_id=sender_id, receiver_id=receiver_id)
                    self.object = self.get_object()
                    context = self.get_context_data(object=self.object)
                    return self.render_to_response(context)
            return JsonResponse({'message': 'mistake 1'})
        return JsonResponse({'message': 'mistake 2 '})


class ProfileFriendsPage(DetailView, DataMixin):
    template_name = 'forum/profile_friends.html'
    context_object_name = 'user'
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('profile_id')
        friendship_records = Friendship.objects.filter(Q(user1_id=user_id) | Q(user2_id=user_id))
        related_user_ids = set(chain(friendship_records.values_list('user1_id', flat=True),
                                     friendship_records.values_list('user2_id', flat=True)))
        related_user_ids.discard(user_id)
        friends = CustomUser.objects.order_by('-username').only('id', 'username', 'avatar').filter(id__in=related_user_ids)

        paginator = Paginator(friends, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        if self.request.user.is_authenticated:
            mix = self.get_user_context(title='profile', user_id=self.request.user.id, friends=page_obj)
        else:
            mix = self.get_user_context(title='profile', friends=page_obj)
        return context | mix

    def get_object(self, queryset=None):
        profile = self.kwargs.get('profile_id')
        user_des = Prefetch('userdescription',
                            queryset=UserDescription.objects.only('id', 'sex', 'birth_date', 'political_orientation',
                                                                  'art_style', 'ideology', 'credo', 'description', 'user_id'))
        user_spec = Prefetch('userspecializations_set__specialization', queryset=Specializations.objects.all())
        queryset = CustomUser.objects.filter(id=profile).prefetch_related(user_des, 'userspecializations_set',
                                                                          user_spec).only('id', 'username', 'avatar',
                                                                                          'level', 'date_joined')
        queryset = get_object_or_404(queryset)
        queryset.userspecializations_set.filter(user_id=profile)
        return queryset

    def post(self, request, *args, **kwargs):
        print('POST friends view')
        if request.POST.get('event') == 'broken friendship':
            user_id = self.request.user.id
            friend_id = request.POST.get('friend_id')
            friendship = Friendship.objects.filter(Q(user1_id=user_id, user2_id=friend_id) | Q(user1_id=friend_id, user2_id=user_id)).exists()
            if friendship:
                friendship = Friendship.objects.get(Q(user1_id=user_id, user2_id=friend_id) | Q(user1_id=friend_id, user2_id=user_id))
                friendship.delete()
            else:
                raise ValueError('Error due to incorrect friendship in friends view')
            self.object = self.get_object()
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)


class ProfileBansPage(DetailView, DataMixin):
    template_name = 'forum/profile_bans.html'
    context_object_name = 'user'
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('profile_id')
        bans = Culprits.objects.filter(user_id=user_id).order_by('-id')

        paginator = Paginator(bans, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        if self.request.user.is_authenticated:
            mix = self.get_user_context(title='Profile', user_id=self.request.user.id, bans=page_obj)
        else:
            mix = self.get_user_context(title='Profile', bans=page_obj)
        return context | mix

    def get_object(self, queryset=None):
        profile_id = self.kwargs.get('profile_id')
        user_des = Prefetch('userdescription',
                            queryset=UserDescription.objects.only('id', 'sex', 'birth_date', 'political_orientation',
                                                                  'art_style', 'ideology', 'credo', 'description', 'user_id'))
        user_spec = Prefetch('userspecializations_set__specialization', queryset=Specializations.objects.all())
        queryset = CustomUser.objects.filter(id=profile_id).prefetch_related(user_des, 'userspecializations_set', user_spec).only('id', 'username', 'avatar', 'level', 'date_joined')
        return get_object_or_404(queryset)

    def dispatch(self=None, request=None, *args, **kwargs):
        user_id = self.kwargs.get('profile_id')
        if request.user.id != user_id:
            return HttpResponseForbidden('try more')
        else:
            return super().dispatch(request, *args, **kwargs)


class ProfileEventsPage(DetailView, DataMixin):
    template_name = 'forum/profile_events.html'
    context_object_name = 'user'
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('profile_id')

        events = UserEvents.objects.filter(receiver_id=user_id).order_by('-id').select_related('sender').prefetch_related(
            Prefetch('sender__userdescription', queryset=UserDescription.objects.only('sex'))
        ).only('id', 'event', 'sender__id', 'sender__username', 'sender__avatar', 'sender__userdescription__sex')

        paginator = Paginator(events, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        if self.request.user.is_authenticated:
            mix = self.get_user_context(title='profile', user_id=self.request.user.id, events=page_obj)
        else:
            mix = self.get_user_context(title='profile', events=page_obj)
        return context | mix

    def get_object(self, queryset=None):
        profile_id = self.kwargs.get('profile_id')
        user_des = Prefetch('userdescription',
                            queryset=UserDescription.objects.only('id', 'sex', 'birth_date', 'political_orientation',
                                                                  'art_style', 'ideology', 'credo', 'description', 'user_id'))
        user_spec = Prefetch('userspecializations_set__specialization', queryset=Specializations.objects.all())
        queryset = CustomUser.objects.filter(id=profile_id).prefetch_related(user_des, 'userspecializations_set', user_spec).only('id', 'username', 'avatar', 'level', 'date_joined')
        return get_object_or_404(queryset)

    def post(self, request, *args, **kwargs):
        print(request.POST)
        profile_id = self.kwargs.get('profile_id')
        if request.POST.get('event') == 'event__friendship' and UserEvents.objects.filter(event='friendship', receiver_id=profile_id, sender_id=request.POST.get('sender_id')).exists():
            sender_id = request.POST.get('sender_id')
            print('friendship')
            event = UserEvents.objects.get(event='friendship', receiver_id=profile_id, sender_id=sender_id)
            if request.POST.get('event_type') == 'accept':
                friends_link = Friendship(user1_id=request.POST.get('sender_id'), user2_id=self.kwargs.get('profile_id'))
                friends_link.save()
                event.delete()
            elif request.POST.get('event_type') == 'reject':
                event.delete()
                print('reject')
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def dispatch(self=None, request=None, *args, **kwargs):
        user_id = self.kwargs.get('profile_id')
        if request.user.id != user_id:
            return HttpResponseForbidden('bad try')
        else:
            return super().dispatch(request, *args, **kwargs)


class ProfileContributionPage(DetailView, DataMixin):
    template_name = 'forum/profile_contribution.html'
    context_object_name = 'user'
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        author_id = self.kwargs.get('profile_id')
        discussions = Discussion.objects.only('id', 'rating', 'creation_date', 'theme').filter(creator_id=author_id).order_by('-id')

        paginator = Paginator(discussions, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        if self.request.user.is_authenticated:
            mix = self.get_user_context(title='Profile', user_id=self.request.user.id, discussions=page_obj)
        else:
            mix = self.get_user_context(title='Profile', discussions=page_obj)
        return context | mix


    def get_object(self, queryset=None):
        profile_id = self.kwargs.get('profile_id')
        user_des = Prefetch('userdescription',
                            queryset=UserDescription.objects.only('id', 'sex', 'birth_date', 'political_orientation',
                                                                  'art_style', 'ideology', 'credo', 'description', 'user_id'))
        user_spec = Prefetch('userspecializations_set__specialization', queryset=Specializations.objects.all())
        queryset = CustomUser.objects.filter(id=profile_id).prefetch_related(user_des, 'userspecializations_set', user_spec).only('id', 'username', 'avatar', 'level', 'date_joined')
        return get_object_or_404(queryset)


class DiscussionCreatePage(LoginRequiredMixin, CreateView, DataMixin):
    form_class = CreateDiscussionForm
    template_name = 'forum/new_discussion.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            specs = Specializations.objects.prefetch_related('interlocutiontags_set')
            mix = self.get_user_context(title='new page', user_id=self.request.user.id, specs=specs)
        else:
            mix = self.get_user_context(title='Add title')
        return context | mix

    def form_valid(self, form):
        form.instance.creator = self.request.user
        self.object = form.save()
        print(self.request.POST)
        selected_tags = self.request.POST.getlist('tag')

        tags_ids = InterlocutionTags.objects.values_list('id', flat=True)

        valid_tags = [int(tag_id) for tag_id in selected_tags if int(tag_id) in tags_ids]

        DiscussionTags.objects.bulk_create([
            DiscussionTags(DDA_id=self.object.pk, tag_id=tag_id) for tag_id in valid_tags
        ])
        success_url = self.object.get_absolute_url()
        return HttpResponseRedirect(success_url)


class DiscussionsPage(DataMixin, ListView):
    model = Discussion
    paginate_by = 10
    ordering = ['-id']
    template_name = 'forum/discussions.html'
    context_object_name = 'discussions'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        tags = InterlocutionTags.objects.only('id', 'name').all()
        author_or = UserDescription.UserPoliticalOrientation.choices
        if self.request.user.is_authenticated:
            mix = self.get_user_context(title='discussions', user_id=self.request.user.id, tags=tags,
                                        p_orients=author_or)
        else:
            mix = self.get_user_context(title='discussion', tags=tags, p_orients=author_or)
        return context | mix

    def get_queryset(self):  # p_orient работает не так как теги()
        queryset = super().get_queryset()
        tags_included = self.request.GET.getlist('tag[include]')
        tags_excluded = self.request.GET.getlist('tag[exclude]')
        p_orient_included = self.request.GET.getlist('orientation[include]')
        p_orient_excluded = self.request.GET.getlist('orientation[exclude]')
        print(f'p_orient_excluded:{p_orient_excluded}, p_orient_included: {p_orient_included}')
        print(f'tags_excluded:{tags_excluded}, tags_included: {tags_included}')
        if len(p_orient_included) == 0 and len(p_orient_excluded) == 0:
            queryset = queryset.prefetch_related('discussiontags_set__tag')
            if len(tags_included) == 0 and len(tags_excluded) == 0:
                queryset = queryset
            elif len(tags_included) != 0 and len(tags_excluded) != 0:
                queryset = queryset.filter(discussiontags__tag__in=tags_included).annotate(
                    num_tags=Count('discussiontags')).filter(num_tags=len(tags_included)).distinct()
                queryset = queryset.exclude(discussiontags__tag__in=tags_excluded)
            elif len(tags_included) != 0:
                queryset = queryset.filter(discussiontags__tag__in=tags_included).distinct().annotate(
                    num_tags=Count('discussiontags')).filter(num_tags=len(tags_included))
            elif len(tags_excluded) != 0:
                queryset = queryset.exclude(discussiontags__tag__in=tags_excluded)
        elif len(p_orient_included) != 0 and len(p_orient_excluded) != 0:
            queryset = queryset.prefetch_related(
                Prefetch('creator__userdescription', queryset=UserDescription.objects.only('political_orientation')),
                Prefetch('discussiontags_set__tag', queryset=InterlocutionTags.objects.all())
            ).filter(creator__userdescription__political_orientation__in=p_orient_included).distinct().exclude(
                creator__userdescription__political_orientation__in=p_orient_excluded)
            if len(tags_included) == 0 and len(tags_excluded) == 0:
                queryset = queryset
            elif len(tags_included) != 0 and len(tags_excluded) != 0:
                queryset = queryset.filter(discussiontags__tag__in=tags_included).annotate(
                    num_tags=Count('discussiontags')).filter(num_tags=len(tags_included)).distinct()
                queryset = queryset.exclude(discussiontags__tag__in=tags_excluded)
            elif len(tags_excluded) == 0:
                queryset = queryset.filter(discussiontags__tag__in=tags_included).annotate(
                    num_tags=Count('discussiontags')).filter(num_tags=len(tags_included)).distinct()
            elif len(tags_included) == 0:
                queryset = queryset.exclude(discussiontags__tag__in=tags_excluded).annotate(
                    num_tags=Count('discussiontags')).exclude(num_tags=len(tags_excluded)).distinct()
        elif len(p_orient_included) == 0:
            queryset = queryset.prefetch_related(
                Prefetch('creator__userdescription', queryset=UserDescription.objects.only('political_orientation')),
                Prefetch('discussiontags_set__tag', queryset=InterlocutionTags.objects.all())
            ).exclude(creator__userdescription__political_orientation__in=p_orient_excluded)
            if len(tags_included) == 0 and len(tags_excluded) == 0:
                queryset = queryset
            elif len(tags_included) != 0 and len(tags_excluded) != 0:
                queryset = queryset.filter(discussiontags__tag__in=tags_included).annotate(
                    num_tags=Count('discussiontags')).filter(num_tags=len(tags_included)).distinct()
                queryset = queryset.exclude(discussiontags__tag__in=tags_excluded)
            elif len(tags_excluded) == 0:
                queryset = queryset.filter(discussiontags__tag__in=tags_included).annotate(
                    num_tags=Count('discussiontags')).filter(num_tags=len(tags_included)).distinct()
            elif len(tags_included) == 0:
                queryset = queryset.exclude(discussiontags__tag__in=tags_excluded).annotate(
                    num_tags=Count('discussiontags')).exclude(num_tags=len(tags_excluded)).distinct()
        elif len(p_orient_excluded) == 0:
            queryset = queryset.prefetch_related(
                Prefetch('creator__userdescription', queryset=UserDescription.objects.only('political_orientation')),
                Prefetch('discussiontags_set__tag', queryset=InterlocutionTags.objects.all())
            ).filter(creator__userdescription__political_orientation__in=p_orient_included).distinct()
            if len(tags_included) == 0 and len(tags_excluded) == 0:
                queryset = queryset
            elif len(tags_included) != 0 and len(tags_excluded) != 0:
                queryset = queryset.filter(discussiontags__tag__in=tags_included).annotate(
                    num_tags=Count('discussiontags')).filter(num_tags=len(tags_included)).distinct()
                queryset = queryset.exclude(discussiontags__tag__in=tags_excluded)
            elif len(tags_excluded) == 0:
                queryset = queryset.filter(discussiontags__tag__in=tags_included).annotate(
                    num_tags=Count('discussiontags')).filter(num_tags=len(tags_included)).distinct()
            elif len(tags_included) == 0:
                queryset = queryset.exclude(discussiontags__tag__in=tags_excluded).annotate(
                    num_tags=Count('discussiontags')).exclude(num_tags=len(tags_excluded)).distinct()
        return queryset

    def post(self, request, *args, **kwargs):
        # print(request.POST)
        if request.POST.get('request_type') == 'discussion_grade':
            action = request.POST.get('action')
            discussion_id = request.POST.get('discussion_id')
            grader_id = request.POST.get('user_id')
            if grader_id is None:
                return JsonResponse({'message': 'mistake'})
            if Discussion.objects.filter(id=discussion_id).exclude(creator_id=grader_id):
                discussion = Discussion.objects.get(id=discussion_id)
                if not DiscussionGrades.objects.filter(discussion_id=discussion_id, user_id=grader_id).exists():
                    if action == 'up':
                        discussion.rating += 1
                        discussion.save()
                        DiscussionGrades.objects.create(user_grade='1', discussion_id=discussion_id, user_id=grader_id)
                    elif action == 'down':
                        discussion.rating -= 1
                        discussion.save()
                        DiscussionGrades.objects.create(user_grade='0', discussion_id=discussion_id, user_id=grader_id)
                else:
                    grade = DiscussionGrades.objects.get(discussion_id=discussion_id, user_id=grader_id)
                    if action == 'up' and grade.user_grade == '0':
                        discussion.rating += 2
                        grade.user_grade = '1'
                        discussion.save()
                        grade.save()
                    elif action == 'down' and grade.user_grade == '1':
                        discussion.rating -= 2
                        grade.user_grade = '0'
                        discussion.save()
                        grade.save()
                return JsonResponse({'new_rating': discussion.rating})
            return JsonResponse({'message': 'mistake'})
        else:
            return JsonResponse({'message': 'mistake'})


class DiscussionPage(DataMixin, DetailView):
    model = Discussion
    template_name = 'forum/discussion.html'
    context_object_name = 'discussion'
    paginate_by = 15

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = DiscussionComments.objects.select_related('comment', 'comment__author', 'comment__parent_comment', 'comment__parent_comment__author')
        comments = comments.only('id', 'comment__id', 'comment__upload_date', 'comment__comment', 'comment__rating',
                                 'comment__author__avatar', 'comment__author__username',
                                 'comment__parent_comment__author__username').filter(
            DDA_id=self.kwargs.get('discussion_id')).order_by('id')

        paginator = Paginator(comments, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        if self.request.user.is_authenticated:
            mix = self.get_user_context(title='discussion', user_id=self.request.user.id, comments=page_obj)
        else:
            mix = self.get_user_context(title='discussion', comments=page_obj)
        return context | mix

    def get_object(self, queryset=None):
        discussion = self.kwargs.get('discussion_id')
        queryset = Discussion.objects.select_related('creator').only('id', 'theme', 'content', 'creation_date', 'creator__username').filter(id=discussion)
        return get_object_or_404(queryset)

    def post(self, request, *args, **kwargs):
        print(request.POST)
        request_type = request.POST.get('request_type')
        if request_type == 'comment_grade':
            action = request.POST.get('action')
            comment_id = request.POST.get('comment_id')
            grader_id = request.POST.get('user_id')
            if grader_id is None:
                return JsonResponse({'message': 'mistake'})
            if Comments.objects.filter(id=comment_id).exclude(author_id=grader_id).exists():
                comment = Comments.objects.get(id=comment_id)
                if not CommentsRating.objects.filter(comment_id=comment_id, user_id=grader_id).exists():
                    if action == 'up':
                        comment.rating += 1
                        comment.save()
                        CommentsRating.objects.create(user_grade='1', comment_id=comment_id, user_id=grader_id)
                    elif action == 'down':
                        comment.rating -= 1
                        comment.save()
                        CommentsRating.objects.create(user_grade='0', comment_id=comment_id, user_id=grader_id)
                else:
                    grade = CommentsRating.objects.get(comment_id=comment_id, user_id=grader_id)
                    if action == 'up' and grade.user_grade == '0':
                        comment.rating += 2
                        grade.user_grade = '1'
                        comment.save()
                        grade.save()
                    elif action == 'down' and grade.user_grade == '1':
                        comment.rating -= 2
                        grade.user_grade = '0'
                        comment.save()
                        grade.save()
                return JsonResponse({'new_rating': comment.rating})
            return JsonResponse({'message': 'mistake'})
        elif request_type == 'comment_delete':
            comment_id = request.POST.get('comment_id')
            dda_id = request.POST.get('discussion_id')
            request_id = request.POST.get('user_id')
            if Comments.objects.filter(id=comment_id, dda_id=dda_id, author_id=request_id).exists():
                comment = Comments.objects.get(id=comment_id, dda_id=dda_id, author_id=request_id)
                if comment.parent_comment is None:
                    comment.delete()
        elif request_type == 'comment_editing':
            print('editing')
            comment_id = request.POST.get('comment_id')
            dda_id = request.POST.get('discussion_id')
            request_id = request.POST.get('user_id')
            if Comments.objects.filter(id=comment_id, dda_id=dda_id, author_id=request_id).exists():
                comment = Comments.objects.get(id=comment_id, dda_id=dda_id, author_id=request_id)
                if comment.is_replied is False:
                    edited_text = request.POST.get('edited_text')
                    comment.comment = edited_text
                    comment.save()
        elif request_type == 'comment_reply':
            print('reply')
            comment_id = request.POST.get('comment_id')
            dda_id = request.POST.get('discussion_id')
            request_id = request.POST.get('user_id')
            replied_text = request.POST.get('repliedText')
            if Comments.objects.filter(id=comment_id, dda_id=dda_id).exists():
                comment = Comments(comment=replied_text, dda_id=dda_id, author_id=request_id, parent_comment_id=comment_id)
                comment.save()
                discussion_comment = DiscussionComments(DDA_id=dda_id, comment_id=comment.id)
                discussion_comment.save()
                replied_comment = Comments.objects.get(id=comment_id)
                replied_comment.is_replied = True
                replied_comment.save()
        elif request_type == 'comment_new':
            print('new comment')
            comment_text = request.POST.get('comment_text')
            dda_id = request.POST.get('discussion_id')
            request_id = request.POST.get('user_id')
            comment = Comments(comment=comment_text, dda_id=dda_id, author_id=request_id)
            comment.save()
            discussion_comment = DiscussionComments(DDA_id=dda_id, comment_id=comment.id)
            discussion_comment.save()
        return JsonResponse({'message': 'mistake'})


def pageNotFoundError(request, exception):
    return HttpResponseNotFound('<h1>try more</h1>')

def logout_user(request):
    logout(request)
    return redirect('home')

