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
	age = models.CharField(max_length=5, choices=AGES, default='U15')
	gender = models.IntegerField() # 0: man, 1: woman
	domisili = models.IntegerField() # 0: jabodetabek, 1: Non-Jab Jawa, 2: Luar Jawa
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
	degree = models.CharField(max_length=2, choices=DEGREES, default='D1')
	angkatan = models.IntegerField()
	faculty = models.CharField(max_length=100)

	def __str__(self):
		return self.username

