from copy import copy

from django import template
from django.core.paginator import Paginator
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from livechat.models import LiveChat

current_site = Site.objects.get_current()

register = template.Library()


@register.inclusion_tag('livechat/inclusion_tags/live_chat_banner.html',
                        takes_context=True)
def live_chat_banner(context):
    """ Display any available live chats as advertisements.
    """
    context = copy(context)

    # Find any upcoming or current live chat. These are LiveChat's with primary
    # category of 'ask-mama' and category of 'live-chat'. The Chat date must be
    # less than 5 days away, or happening now.

    chat = LiveChat.chat_finder.upcoming_live_chat()
    if chat is not None:
        context['live_chat_advert'] = {
            'title': chat.title,
            'description': chat.description
        }
        if chat.is_in_progress():
            context['live_chat_advert']['url'] = reverse(
                'livechat:show_livechat', 
                kwargs={
                    'slug': chat.slug
                })
        else:
            context['live_chat_advert']['url'] = reverse('askmama_object_list')
    return context


@register.inclusion_tag('livechat/inclusion_tags/live_chat.html',
                        takes_context=True)
def show_live_chat(context):
    context = copy(context)
    return context


@register.simple_tag(takes_context=True)
def get_livechat_for_article(context, post, var_name):
    post_type = ContentType.objects.get_for_model(post.__class__)
    chats = LiveChat.permitted.filter(content_type=post_type,
                                      object_id=post.id)
    try:
        context[var_name] = chats.latest('created')
    except LiveChat.DoesNotExist:
        pass
    return ''


# @register.simple_tag(takes_context=True)
# def get_livechat_page(context, livechat, var_name):
#     """
#     Fetches a page object for the given livechat
#
#     Usage:
#     {% get_livechat_page `livechat` `var_name` %}
#     """
#     request = context['request']
#
#     comments_qs = livechat.comment_set().exclude(is_removed=True)
#     comments_qs = comments_qs.distinct().select_related('user')
#     comments_qs = comments_qs.order_by('-submit_date')
#
#     answered = request.GET.get('answered', '')
#     popular = request.GET.get('popular', '')
#     if answered == 'true':
#         comments_qs = comments_qs.filter(livechatresponse__isnull=False)
#     if answered == 'false':
#         comments_qs = comments_qs.filter(livechatresponse__isnull=True)
#     if popular == 'true':
#         comments_qs = comments_qs.order_by('-like_count')
#
#     paginator = Paginator(comments_qs, per_page=10)
#     page = paginator.page(request.GET.get('p', 1))
#     context['page'] = page
#     return ''


@register.simple_tag(takes_context=True)
def get_mylivechat(context, livechat, var_name='my_comments'):
    """
    Fetches user's comments for the given livechat

    Usage:
    {% get_mylivechat `livechat` `var_name` %}
    """
    request = context['request']

    if not request.user.is_authenticated():
        return None

    comments_qs = livechat.comment_set().distinct()
    comments_qs = comments_qs.filter(user=request.user)
    comments_qs = comments_qs.select_related('user').order_by('-submit_date')
    context[var_name] = comments_qs
    return ''
