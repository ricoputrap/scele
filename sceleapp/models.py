from django.db import models

# Create your models here.

class UserApp(models.Model):
	username = models.CharField(max_length=40, primary_key=True)
	password = models.CharField(max_length=100)
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	contact = models.CharField(max_length=100)

	AGES = (
		('U15', '< 15 tahun'),
		('15-19', '15 - 19 tahun'),
		('20-24', '20 - 24 tahun'),
		('25-29', '25 - 29 tahun'),
		('30-34','30 - 34 tahun'),
		('35-39', '35 - 39 tahun'),
		('40-44', '40 - 44 tahun'),
		('O44', '>= 45 tahun'),
		)
	age = models.CharField(max_length=5, choices=AGES)

	GENDERS = (
		('L', 'laki-laki'),
		('P', 'perempuan'),
	)
	gender = models.CharField(max_length=1, choices=GENDERS)

	DOMISILIS = (
		('jab', 'jabodetabek'),
		('njj', 'non-jabodetabek jawa'),
		('lpj', 'luar pulau jawa'),
	)
	domisili = models.CharField(max_length=3, choices=DOMISILIS)
	univ = models.CharField(max_length=200)

	DEGREES = (
		('D1', 'Ahli Pratama'),
		('D2', 'Ahli Muda'),
		('D3', 'Ahli Madya'),
		('D4', 'Sarjana Sains Terapan'),
		('S1', 'Sarjana'),
		('S2', 'Magister'),
		('S3', 'Doktor'),
		)
	degree = models.CharField(max_length=2, choices=DEGREES)
	angkatan = models.IntegerField()
	faculty = models.CharField(max_length=100)

	class Meta:
		ordering = ['first_name']

	def __str__(self):
		return self.username

class Course(models.Model):
	name = models.CharField(max_length=20)
	is_active = models.BooleanField()

	class Meta:
		ordering = ['is_active']

	def __str__(self):
		return self.name

class UserPost(models.Model):
	subject = models.CharField(max_length=50)
	msg = models.TextField()
	created_at = models.DateTimeField(auto_now=True)
	grade = models.IntegerField()
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	creator = models.ForeignKey(UserApp, on_delete=models.CASCADE) # raise ProtectedError in views if needed

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return 'Post {0} in {1} created by {2}'.format(self.subject, self.course.name,  self.creator.username)

class PostLike(models.Model):
	quantity = models.IntegerField()
	user_post = models.OneToOneField(UserPost, on_delete=models.CASCADE)
	# likers = models.ManyToManyField(UserApp)

	def __str__(self):
		return '{0} likes for post {1}'.format(self.quantity, self.user_post.subject)

class GivenPostLike(models.Model):
	liker = models.ForeignKey(UserApp, on_delete=models.CASCADE) # raise ProtectedError in views if needed
	post_like = models.ForeignKey(PostLike, on_delete=models.CASCADE)

	def __str__(self):
		return '{0} gave {1} likes'.format(self.liker, self.post_like.quantity)

class UserReply(models.Model):
	subject = models.CharField(max_length=50)
	msg = models.TextField()
	created_at = models.DateTimeField(auto_now=True)
	grade = models.IntegerField()
	user_post = models.ForeignKey(UserPost, on_delete=models.CASCADE)
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	creator = models.ForeignKey(UserApp, on_delete=models.CASCADE)
	host_reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return 'Reply {0} in {1} created by {2}'.format(self.subject, self.course.name,  self.creator.username)

class ReplyLike(models.Model):
	quantity = models.IntegerField()
	user_reply = models.OneToOneField(UserReply, on_delete=models.CASCADE)
	# likers = models.ManyToManyField(UserApp)

	def __str__(self):
		return '{0} likes for reply {1}'.format(self.quantity, self.user_reply.subject)

class GivenReplyLike(models.Model):
	liker = models.ForeignKey(UserApp, on_delete=models.CASCADE) # raise ProtectedError in views if needed
	reply_like = models.ForeignKey(ReplyLike, on_delete=models.CASCADE)

	def __str__(self):
		return '{0} gave {1} likes'.format(self.liker, self.reply_like.quantity)

class Notif(models.Model):
	title = models.CharField(max_length=100)
	desc = models.TextField()

	NOTIF_TYPES = (
		('b', 'badge'),
		('g', 'grade'),
		('l', 'like'),
		('r', 'reply'),
	)
	notif_type = models.CharField(max_length=1, choices=NOTIF_TYPES, default='b')
	created_at = models.DateTimeField(auto_now_add=True)
	is_new = models.BooleanField()
	img = models.CharField(max_length=200)
	link = models.URLField()
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	receiver = models.ForeignKey(UserApp, on_delete=models.CASCADE)

	def __str__(self):
		return '"{0}" got notif "{1}" in {2}'.format(self.receiver, self.title, self.course)

class Badge(models.Model):
	name = models.CharField(max_length=50)
	desc = models.TextField()
	criteria = models.TextField()

	BADGE_TYPES = (
		('p', 'participation'),
		('s', 'skill'),
	)
	badge_type = models.CharField(max_length=1, choices=BADGE_TYPES, default='p')
	img = models.CharField(max_length=200)

	def __str__(self):
		return self.name

class UserBadge(models.Model):
	owner = models.ForeignKey(UserApp, on_delete=models.CASCADE)
	badge = models.ForeignKey(Badge, on_delete=models.CASCADE)

	def __str__(self):
		return 'Badge {0} owned by {1}'.format(self.badge, self.owner)