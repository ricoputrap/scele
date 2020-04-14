from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.

class UserActivity(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	post_count = models.IntegerField(default=0)
	reply_count = models.IntegerField(default=0)
	likes_given_count = models.IntegerField(default=0)
	likes_earned_count = models.IntegerField(default=0)
	grades = models.IntegerField(default=0)
	bonuses = models.IntegerField(default=0)
	is_gamified = models.BooleanField(default=False)

	def __str__(self):
	 return "Activity of {0}: [post: {1}, reply: {2}, likes_given: {3}, likes_earned: {4}, grades: {5}, bonuses: {6}, is_gamified: {7}]".format(self.user, self.post_count, self.reply_count, self.likes_given_count, self.likes_earned_count, self.grades, self.bonuses, self.is_gamified)


class UserParticipation(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	has_posted = models.BooleanField(default=False)
	has_replied = models.BooleanField(default=False)
	has_liked = models.BooleanField(default=False)
	has_been_liked_3_times = models.BooleanField(default=False) 

	class Meta:
		ordering = ['user']

	def __str__(self):
		return "Participation of {0}: [has_posted: {1}, has_replied: {2}, has_liked: {3}, has_been_liked_3_times: {4}]".format(self.user.first_name, self.has_posted, self.has_replied, self.has_liked, self.has_been_liked_3_times)
	
class Gamification(models.Model):
	is_gamified = models.BooleanField(default=False)

class UserPost(models.Model):
	subject = models.CharField(max_length=100)
	msg = models.TextField()
	created_at = models.DateTimeField(auto_now=True)
	grade = models.IntegerField(default=0)
	permalink = models.CharField(max_length=200)
	is_gamified = models.BooleanField(default=False)
	creator = models.ForeignKey(User, on_delete=models.CASCADE) #creator gak mungkin dihapus

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return self.subject

class PostLike(models.Model):
	user_post = models.OneToOneField(UserPost, on_delete=models.SET_NULL, null=True, blank=True)
	quantity = models.IntegerField()
	is_gamified = models.BooleanField(default=False)
	post_owner = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		if self.user_post:
			return '{0} likes on post "{1}"'.format(self.quantity, self.user_post.subject)
		else:
			return '{0} likes on post'.format(self.quantity)

class GivenPostLike(models.Model):
	liker = models.ForeignKey(User, on_delete=models.CASCADE) # liker gak mungkin dihapus
	post_like = models.ForeignKey(PostLike, on_delete=models.CASCADE)
	is_gamified = models.BooleanField(default=False)

	def __str__(self):
		return '{0} gave {1}likes'.format(self.liker.username, self.post_like.quantity)

class UserReply(models.Model):
	subject = models.CharField(max_length=100)
	msg = models.TextField()
	created_at = models.DateTimeField(auto_now=True)
	grade = models.IntegerField(default=0)
	permalink = models.CharField(max_length=200)
	is_gamified = models.BooleanField(default=False)
	user_post = models.ForeignKey(UserPost, on_delete=models.CASCADE, null=True, blank=True)
	creator = models.ForeignKey(User, on_delete=models.CASCADE)
	host_reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

	class Meta:
		ordering = ['created_at']

	def __str__(self):
		return self.subject

class ReplyLike(models.Model):
	user_reply = models.OneToOneField(UserReply, on_delete=models.SET_NULL, null=True, blank=True)
	quantity = models.IntegerField()
	is_gamified = models.BooleanField(default=False)
	reply_owner = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		if self.user_reply is None:
			return '{0} likes for reply NULL'.format(self.quantity)
		else:
			return '{0} likes for reply {1}'.format(self.quantity, self.user_reply.subject)

class GivenReplyLike(models.Model):
	liker = models.ForeignKey(User, on_delete=models.CASCADE) # liker gak mungkin dihapus
	reply_like = models.ForeignKey(ReplyLike, on_delete=models.CASCADE)
	is_gamified = models.BooleanField(default=False)

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
		('p', 'Post'),
		(None, '-------')
	)
	notif_type = models.CharField(max_length=1, choices=NOTIF_TYPES, default=None)
	is_gamified = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	is_new = models.BooleanField(default=True)
	img_loc = models.CharField(max_length=200)
	user_post = models.ForeignKey(UserPost, on_delete=models.SET_NULL, null=True, blank=True)
	user_reply = models.ForeignKey(UserReply, on_delete=models.SET_NULL, null=True, blank=True)
	receiver = models.ForeignKey(User, on_delete=models.CASCADE)  # receiver gak mungkin dihapus

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return '{0} got notif "{1}"'.format(self.receiver, self.title)

class PostNotif(models.Model):
	notif = models.OneToOneField(Notif, on_delete=models.CASCADE)
	post_quantity = models.IntegerField()

	def __str__(self):
		return '{0} got {1} new posts'.format(self.notif.receiver, self.post_quantity)

class ReplyNotif(models.Model):
	notif = models.OneToOneField(Notif, on_delete=models.CASCADE)
	rep_quantity = models.IntegerField()
	reply = models.ForeignKey(UserReply, on_delete=models.SET_NULL, null=True, blank=True)

	def __str__(self):
		return '{0} replies'.format(self.rep_quantity)

class LikeNotif(models.Model):
	notif = models.OneToOneField(Notif, on_delete=models.CASCADE)
	like_quantity = models.IntegerField()

	def __str__(self):
		return '{0} likes'.format(self.like_quantity)

class Badge(models.Model):
	code = models.CharField(max_length=3, unique=True)
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
		('n', 'Receive 3 likes'),
	)
	activity_type = models.CharField(max_length=1, choices=ACTIVITY_TYPES, default='p')

	def __str__(self):
		return self.name

class UserBadge(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
	user_post = models.ForeignKey(UserPost, on_delete=models.SET_NULL, null=True, blank=True)
	user_reply = models.ForeignKey(UserReply, on_delete=models.SET_NULL, null=True, blank=True)

	def __str__(self):
		return 'Badge {0} owned by {1}'.format(self.badge, self.owner)
