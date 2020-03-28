from django import template
from sceleapp.models import UserPost, UserReply

register = template.Library()

@register.filter(name="get_creator")
def get_creator_name(value):
    return value.creator.get_full_name()

@register.filter(name="get_fullname")
def get_fullname(value):
    return value.get_full_name()

@register.filter(name="get_replies")
def get_replies(value):
    # if value is UserPost:
    if type(value) is UserPost:
        return UserReply.objects.filter(user_post=value)
    return UserReply.objects.filter(host_reply=value)

@register.filter(name="get_replies_size")
def get_replies_size(value):
    replies = get_replies(value)
    replies_size = replies.count()
    if replies_size > 0:
        for reply in replies:
            replies_size += get_replies_size(reply)
    return replies_size

@register.filter(name="get_last_reply")
def get_last_reply(value):
    return get_replies(value).last()

@register.filter(name="get_last_user")
def get_last_activity_user_fullname(value):
    if get_replies_size(value) == 0:
        return value.creator.get_full_name()
    else:
        return "x"