from django import template
from sceleapp.models import UserPost, UserReply

register = template.Library()

@register.filter(name="get_replies")
def get_all_post_replies(value):
    replies = UserReply.objects.filter(user_post=value)
    return replies

@register.filter(name="get_replies_size")
def get_post_replies_size(value):
    return get_all_post_replies(value).count()