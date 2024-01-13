from django.db import models
from enum import Enum
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models import Max


class Role(Enum):
    U = "USER"
    A = "ADMIN"
    V = "VISITOR"


class Colour(Enum):
    YEL = "YELLOW"
    BL = "BLUE"
    GR = "GREEN"


class Genre(Enum):
    ROM = "ROMANCE"
    HOR = "HORROR"
    HIST = "HISTORICAL"
    BAT = "BATTLE"
    COM = "COMEDY"
    DRA = "DRAMA"


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


class Show(models.Model):
    title = models.CharField(max_length=500, null=True, blank=True)
    year = models.IntegerField(null=False, blank=False)
    genre = models.CharField(max_length=10, choices=[(choice.value, choice.name) for choice in Genre])
    popularity = models.FloatField(validators=[MinValueValidator(0.00), MaxValueValidator(9.99)], null=True, blank=True)
    seasons = models.IntegerField(null=False, blank=False)
    description = models.CharField(max_length=500, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            # Get the maximum value of the id field and add 1
            max_id = Show.objects.all().aggregate(Max('id'))['id__max'] or 0
            self.id = max_id + 1

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['popularity']


class Folder(models.Model):
    name = models.CharField(max_length=30, null=False, blank=False)
    colour = models.CharField(max_length=10, choices=[(choice.value, choice.name) for choice in Colour])
    id_show = models.ManyToManyField(Show)
    id_subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE)
    favourites = models.ManyToManyField(Show, related_name='favorited_by')

    def save(self, *args, **kwargs):
        if not self.id:
            # Get the maximum value of the id field and add 1
            max_id = Folder.objects.all().aggregate(Max('id'))['id__max'] or 0
            self.id = max_id + 1

        super().save(*args, **kwargs)