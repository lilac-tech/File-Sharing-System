from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


class UserManager(BaseUserManager):
    def create_user(self, id, name, password=None, division=None):
        """
        Creates and saves a User with the given id and password.
        """
        if not id:
            raise ValueError('Users must have a id')
        if not name:
            raise ValueError('Users must have a name')

        user = self.model(
            id=id,
            name=name,
            division=division,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, id, name, password, division=None):
        """
        Creates and saves a staff user with the given id and password.
        """
        user = self.create_user(
            id=id,
            name=name,
            password=password,
            division=division,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, id, name, password, division=None):
        """
        Creates and saves a superuser with the given id and password.
        """
        user = self.create_user(
            id=id,
            name=name,
            password=password,
            division=division,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    id = models.CharField(max_length=8, unique=True, primary_key=True)
    name = models.CharField(max_length=25)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    division = models.CharField(max_length=3, null=True)
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)  # a admin user; non super-user
    admin = models.BooleanField(default=False)  # a superuser

    # Password field is built in.

    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = ['name']  # id & Password are required by default.

    object = UserManager()

    def __str__(self):
        return self.id

    def has_perm(self, perm, obj=None):
        # Does the user have a specific permission?
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        # Does the user have permissions to view the app `app_label`?
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        # Is the user a member of staff?
        return self.staff

    @property
    def is_admin(self):
        # Is the user a admin member?
        return self.admin
