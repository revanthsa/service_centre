from django.db import models
# Imports for Abstract User
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group

# Imports for Input validation
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import RegexValidator

# Import for Sending Mail
from django.db import transaction
from django.utils.translation import gettext_lazy as _

# Regex for Indian Pincode
pincode_regex = RegexValidator(
	regex=r'^[1-9]{1}[0-9]{2}\\s{0, 1}[0-9]{3}$',
	message="Invalid Indian pincode Detail!\nContact Us, if you have entered the correct Pincode Detail and sill it didn't accept the given Input"
)

# Create your models here.
class User_Manager(BaseUserManager):
	use_in_migrations = True
	def _create_user(self, name, phone, email, address, pin_code, password=None, **extra_fields):
		# Create and save both users
		if not name:
			raise ValueError('The given name must be set')
		if not phone:
			raise ValueError('The given phone must be set')
		if not email:
			raise ValueError('The given email must be set')
		if not address:
			raise ValueError('The given address must be set')
		if not pin_code:
			raise ValueError('The given pincode must be set')
		email = self.normalize_email(email)
		user = self.model(name=name, phone=phone, email=email, address=address, pin_code=pin_code **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	#Create Customer
	def create_user(self, name, phone, email, address, pin_code, password=None, **extra_fields):
		extra_fields.setdefault('is_superuser', False)
		extra_fields.setdefault('is_staff', True)
		return self._create_user(name, phone, email, address, pin_code, password, **extra_fields)

	#Create Admin
	def create_superuser(self, name, phone, email, address, pin_code, password=None, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError('Superuser must have is_staff=True.')
		if extra_fields.get('is_superuser') is not True:
			raise ValueError('Superuser must have is_superuser=True.')

		return self._create_user(name, phone, email, address, pin_code, password, **extra_fields)

class Users(AbstractUser):
	class Meta:
		verbose_name_plural = "View / Manage User Detail"

	username = None
	first_name = None
	last_name = None

	name = models.CharField(max_length=50)
	email = models.EmailField(unique=True)
	phone = PhoneNumberField(max_length=13, unique=True)
	address = models.TextField()
	pin_code = models.CharField(max_length=10, validators=[pincode_regex])
	is_staff = models.BooleanField(
		_('staff status'),
		default=True,
		help_text=_('Designates whether the user can log into this admin site.'),
	)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['name', 'phone', 'address', 'pin_code']

	objects = User_Manager()

	def __str__(self):
		return str(self.email)

	def save(self, **kwargs):
		super().save()
		transaction.on_commit(self.addingGroup)

	# save the user as customer if he is not a superuser or mechanic
	def addingGroup(self):
		if self.is_superuser == False:
			if not self.groups.filter(name='mechanics').exists():
				self.groups.add(Group.objects.get(name='customers'))
		super().save()