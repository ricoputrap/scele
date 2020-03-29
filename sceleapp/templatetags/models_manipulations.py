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
    replies = UserReply.objects.filter(user_post=value)
    last_reply = replies.last()
    deepest = []
    for rep in replies:
        deepest = get_deepest_replies(deepest, rep)
    for reply in deepest:
        if reply.created_at > last_reply.created_at:
            last_reply = reply
    return last_reply

def get_deepest_replies(deepest_replies, rep):
    replies = UserReply.objects.filter(host_reply=rep)
    if replies.count() == 0:
        deepest_replies.append(rep)
    else:
        for reply in replies:
            get_deepest_replies(deepest_replies, reply)
    return deepest_replies

@register.filter(name="get_last_user")
def get_last_activity_user_fullname(value):
    if get_replies_size(value) == 0:
        return value.creator.get_full_name()
    else:
        return get_last_reply(value).creator.get_full_name()

@register.filter(name="get_last_updated")
def get_last_updated(value):
    if get_replies_size(value) == 0:
        return value.created_at
    else:
        return get_last_reply(value).created_at