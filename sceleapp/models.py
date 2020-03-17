from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserPost(models.Model):
	subject = models.CharField(max_length=50)
	msg = models.TextField()
	created_at = models.DateTimeField(auto_now=True)
	grade = models.IntegerField()
	permalink = models.CharField(max_length=200)
	is_gamified = models.BooleanField(default=False)
	creator = models.ForeignKey(User, on_delete=models.CASCADE) #creator gak mungkin dihapus

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return 'Post {0} created by {1}'.format(self.subject, self.creator.username)

class PostLike(models.Model):
	user_post = models.OneToOneField(UserPost, on_delete=models.SET_NULL, null=True, blank=True)
	quantity = models.IntegerField()
	is_gamified = models.BooleanField(default=False)

	def __str__(self):
		return '{0} likes on post "{1}"'.format(self.quantity, self.user_post.subject)

class GivenPostLike(models.Model):
	liker = models.ForeignKey(User, on_delete=models.CASCADE) # liker gak mungkin dihapus
	post_like = models.ForeignKey(PostLike, on_delete=models.CASCADE)
	pk = models.UniqueConstraint(fields=['liker', 'post_like'], name='given_post_like_pk')

	def __str__(self):
		return '{0} gave {1} likes'.format(self.liker.username, self.post_like.quantity)

class UserReply(models.Model):
	subject = models.CharField(max_length=50)
	msg = models.TextField()
	created_at = models.DateTimeField(auto_now=True)
	grade = models.IntegerField()
	permalink = models.CharField(max_length=200)
	is_gamified = models.BooleanField(default=False)
	user_post = models.ForeignKey(UserPost, on_delete=models.CASCADE)
	creator = models.ForeignKey(User, on_delete=models.CASCADE)
	host_reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return 'Reply {0} created by {1}'.format(self.subject,  self.creator.username)

class ReplyLike(models.Model):
	user_reply = models.OneToOneField(UserReply, on_delete=models.SET_NULL, null=True, blank=True)
	quantity = models.IntegerField()
	is_gamified = models.BooleanField(default=False)

	def __str__(self):
		return '{0} likes for reply {1}'.format(self.quantity, self.user_reply.subject)

class GivenReplyLike(models.Model):
	liker = models.ForeignKey(User, on_delete=models.CASCADE) # liker gak mungkin dihapus
	reply_like = models.ForeignKey(ReplyLike, on_delete=models.CASCADE)
	pk = models.UniqueConstraint(fields=['liker', 'reply_like'], name='given_reply_like_pk')

	def __str__(self):
		return '{0} gave {1} likes'.format(self.liker, self.reply_like.quantity)

class Notif(models.Model):
	title = models.CharField(max_length=100)
	desc = models.TextField()

	NOTIF_TYPES = (
		('b', 'Badge'),
		('g', 'Grade'),
		('l', 'Like'),
		('r', 'Reply'),
		(None, '-------')
	)
	notif_type = models.CharField(max_length=1, choices=NOTIF_TYPES, default=None)
	is_gamified = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now=True)
	is_new = models.BooleanField(default=True)
	img_loc = models.CharField(max_length=200)
	user_post = models.ForeignKey(UserPost, on_delete=models.SET_NULL, null=True, blank=True)
	user_reply = models.ForeignKey(UserReply, on_delete=models.SET_NULL, null=True, blank=True)
	receiver = models.ForeignKey(User, on_delete=models.CASCADE)  # receiver gak mungkin dihapus

	def __str__(self):
		return '{0} got notif "{1}"'.format(self.receiver, self.title)

class ReplyNotif(models.Model):
	notif = models.OneToOneField(Notif, on_delete=models.CASCADE)
	rep_quantity = models.IntegerField()

	def __str__(self):
		return '{0} replies'.format(self.rep_quantity)

class LikeNotif(models.Model):
	notif = models.OneToOneField(Notif, on_delete=models.CASCADE)
	like_quantity = models.IntegerField()

	def __str__(self):
		return '{0} likes'.format(self.like_quantity)

class Badge(models.Model):
	name = models.CharField(max_length=50)
	desc = models.TextField()
	criteria = models.TextField()
	img_loc = models.CharField(max_length=200)
	RECEIVING_TYPES = (
		('p', 'Participation'),
		('s', 'Skill'),
	)
	receiving_type = models.CharField(max_length=1, choices=RECEIVING_TYPES, default='p')
	ACTIVITY_TYPES = (
		('p', 'Create a post'),
		('r', 'Create a reply'),
		('l', 'Give a like'),
	)
	activity_type = models.CharField(max_length=1, choices=ACTIVITY_TYPES, default='p')

	def __str__(self):
		return self.name

class UserBadge(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
	user_post = models.OneToOneField(UserPost, on_delete=models.SET_NULL, null=True, blank=True)
	user_reply = models.OneToOneField(UserReply, on_delete=models.SET_NULL, null=True, blank=True)

	def __str__(self):
		return 'Badge {0} owned by {1}'.format(self.badge, self.owner)
