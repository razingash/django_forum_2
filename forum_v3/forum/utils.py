"""
header = [{'title': 'Main page', 'url_name': 'home'},
          {'title': 'Search Title', 'url_name': 'search_page'},
          {'title': 'Add title', 'url_name': 'add_title'},
          {'title': 'Upload Chapter', 'url_name': 'chapter_upload'},
          {'title': 'Register', 'url_name': 'user_register'},
          {'title': 'Login', 'url_name': 'user_login'}]
"""
guest_header = [{'title': 'Discussions', 'url_name': 'discussions'},
                {'title': 'Login', 'url_name': 'login'}]

user_header = [{'title': 'Discussions', 'url_name': 'discussions'},
               {'title': 'Log out', 'url_name': 'logout'}]


class DataMixin:
    def get_user_context(self, **kwargs):
        context = kwargs
        logged_header = user_header.copy()
        unlogged_header = guest_header.copy()
        context['user_header'] = logged_header
        context['guest_header'] = unlogged_header
        # print(context)
        return context
