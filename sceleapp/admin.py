from django.contrib import admin
from .models import UserApp, Course, UserPost, PostLike, GivenPostLike, UserReply, ReplyLike, GivenReplyLike, Notif, Badge, UserBadge

# Register your models here.
admin.site.register(UserApp)
admin.site.register(Course)
admin.site.register(UserPost)
admin.site.register(PostLike)
admin.site.register(GivenPostLike)
admin.site.register(UserReply)
admin.site.register(ReplyLike)
admin.site.register(GivenReplyLike)
admin.site.register(Notif)
admin.site.register(Badge)
admin.site.register(UserBadge)