from django.db import models
from enum import Enum
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models import Max, Avg, Count
from django.urls import reverse


class Role(Enum):
    U = "USER"
    A = "ADMIN"
    V = "VISITOR"


class MyUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("Users must have an email!")
        if not username:
            raise ValueError("Users must have an username!")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(models.Model):
    id = models.AutoField(primary_key=True, db_index=True, unique=True)
    password = models.CharField(max_length=100)
    email = models.fields.EmailField(max_length=200, unique=True)
    role = models.CharField(max_length=10, choices=[(choice.value, choice.name) for choice in Role])

    def save(self, *args, **kwargs):
        if not self.id:
            max_id = User.objects.all().aggregate(Max('id'))['id__max'] or 0
            self.id = max_id + 1

        super().save(*args, **kwargs)


class Admin(User):
    admin_name = models.CharField(max_length=100, null=False, blank=False, unique=True)


class Subscriber(User, AbstractBaseUser):
    username = models.CharField(max_length=100, null=False, blank=False, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = MyUserManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class SubscriberProfile(models.Model):
    user = models.OneToOneField(Subscriber, on_delete=models.CASCADE)
    profile_picture = models.ImageField(blank=True, upload_to='userprofile')

    def __str__(self):
        return self.user.username


class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.category_name

    def get_url(self):
        return reverse('shows_by_category', args=[self.slug])


class Show(models.Model):
    TYPE_CHOICES = (
        ('movie', 'Movie'),
        ('tv_show', 'TV Show'),
    )
    title = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    poster = models.ImageField(upload_to='images/shows', blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="shows")
    show_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='movie')
    video = models.FileField(upload_to='videos', blank=True, null=True)  # Used only for movies

    def __str__(self):
        return self.title

    def is_movie(self):
        return self.show_type == 'movie'

    def is_tv_show(self):
        return self.show_type == 'tv_show'

    def average_review(self):
        reviews = ReviewRating.objects.filter(show=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def count_review(self):
        reviews = ReviewRating.objects.filter(show=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count


class Season(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name="seasons")
    season_number = models.IntegerField()

    def __str__(self):
        return f"{self.show.title} - Season {self.season_number}"


class Episode(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="episodes")
    title = models.CharField(max_length=250)
    episode_number = models.IntegerField()
    video = models.FileField(upload_to='videos')

    def __str__(self):
        return f"{self.season.show.title} - S{self.season.season_number}E{self.episode_number} {self.title}"


class Folder(models.Model):
    name = models.CharField(max_length=30, null=False, blank=False)
    id_show = models.ManyToManyField(Show)
    id_subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE)
    favourites = models.ManyToManyField(Show, related_name='favorited_by')

    def save(self, *args, **kwargs):
        if not self.id:
            # Get the maximum value of the id field and add 1
            max_id = Folder.objects.all().aggregate(Max('id'))['id__max'] or 0
            self.id = max_id + 1

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ReviewRating(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    user = models.ForeignKey(Subscriber, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
