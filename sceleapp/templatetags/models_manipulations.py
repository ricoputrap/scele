from django import template
from sceleapp.models import UserPost, UserReply
from django.templatetags.static import static
from django.shortcuts import redirect
from django.urls import reverse

register = template.Library()

@register.filter(name="get_creator")
def get_creator_name(value):
    tags = '<p>' + str(value.creator.get_full_name()) + '</p>'
    print(add_indent(tags))
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

@register.filter(name="get_replies_tags")
def get_replies_tags(value, active_user):
    tags = ''
    for reply in value:
        tags += get_reply_box(reply, active_user)
    return tags

def add_indent(tags):
    indented_tags = '<div class="indent">' + tags + "</div>"
    return indented_tags

def get_reply_box(reply, active_user):
    profile_url = reverse('profile')
    profile_img = static('img/user-icon.png')
    creator = reply.obj.creator
    creator_fulname = creator.get_full_name()
    user_fullname = active_user.get_full_name()
    parent = reply.parent

    tags = '<div class="box-item" id="' + str(reply.comp_id) + '">' + \
                '<div class="box-item__main-content">'
    
    if creator == active_user:
        tags += '<a href="' + str(profile_url) + '">' + \
                    '<img src="' + str(profile_img) + '" alt="user-icon">' + \
                '</a>'
    else:
        tags += '<img src="' + str(profile_img) + '" alt="user-icon">'

    tags += '<div class="box-item__content">' + \
                '<div id="box-item__content__header">' + \
                    '<p class="font-bold">' + str(reply.obj.subject) + '</p>' + \
                        '<p>by <span>'

    if creator == active_user:
        tags += '<a href="' + str(profile_url) + '">' + user_fullname + '</a>'
    else:
        tags += creator_fulname
    
    tags += '</span> - ' + str(reply.obj.created_at) + '</p></div>' + \
            '<div class="box-item__content__msg">' + str(reply.obj.msg) + '</div></div></div>'

    # footer
    tags += '<div class="box-item__content__footer">' + \
                '<a href="">Like</a>' + \
                '<div class="right"><a href="#'

    if type(parent) is UserPost:
        tags += 'post-item'
    else:
        parent_comp_id = 'rep-' + str(reply.lv - 1) + '-' + str(parent.id)
        tags += parent_comp_id
    
    tags += '">Show Parent</a> | <a href="">Like</a> | <a href="">Reply</a></div>' + \
            '</div></div>'

    # tags += '''<div class="box-item__content__footer">
    #                 <a href="">Like</a>
    #                 <div class="right"><a href="">Show Parent</a> | <a href="">Like</a> | <a href="">Reply</a></div>
    #             </div></div>'''
                #     {% if post.creator == user %}
                #     <a href="{% url 'profile' %}">{{user_fullname}}</a>
                #     {% else %}
                #         {{post|get_creator}}
                #     {% endif %}
                #     </span>
                #     - {{post.created_at}}
                # </p>
    return tags
    

'''
<div class="box-item" id="reply-0">
    <div class="box-item__main-content">
        
        {% if post.creator == user %}
        <a href="{% url 'profile' %}">
            <img src="{% static 'img/user-icon.png' %}" alt="user-icon">
        </a>
        {% else %}
        <img src="{% static 'img/user-icon.png' %}" alt="user-icon">
        {% endif %}
            
        <div class="box-item__content">
            <div id="box-item__content__header">
                <p class="font-bold">{{post.subject}}</p>
                <p>by 
                    <span>
                    {% if post.creator == user %}
                    <a href="{% url 'profile' %}">{{user_fullname}}</a>
                    {% else %}
                        {{post|get_creator}}
                    {% endif %}
                    </span>
                    - {{post.created_at}}
                </p>
                    
            </div>
            <div class="box-item__content__msg">{{post.msg|safe}}</div>
        </div>
    </div>
    <div class="box-item__content__footer">
        <a href="">Like</a>
        <div class="right"><a href="">Show Parent</a> | <a href="">Like</a> | <a href="">Reply</a></div>
    </div>
</div>
'''