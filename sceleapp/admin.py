from django.contrib import admin
from .models import Gamification, UserPost, PostLike, GivenPostLike, UserReply, ReplyLike, GivenReplyLike, Notif, PostNotif, ReplyNotif, LikeNotif, Badge, UserBadge, UserParticipation, UserActivity

# Register your models here.
admin.site.register(Gamification)
admin.site.register(UserPost)
admin.site.register(PostLike)
admin.site.register(GivenPostLike)
admin.site.register(UserReply)
admin.site.register(ReplyLike)
admin.site.register(GivenReplyLike)
admin.site.register(Notif)
admin.site.register(PostNotif)
admin.site.register(ReplyNotif)
admin.site.register(LikeNotif)
admin.site.register(Badge)
admin.site.register(UserBadge)
admin.site.register(UserParticipation)
admin.site.register(UserActivity)