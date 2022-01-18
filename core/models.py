from django.db import models
# Imports for Abstract User
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group

# Imports for Input validation
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import RegexValidator

# Others
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from smart_selects.db_fields import ChainedForeignKey

# Regex validators
pincode_regex = RegexValidator(
	regex=r'^[1-9]{1}[0-9]{5}$',
	message="Invalid Indian pincode Detail!\nContact Us, if you have entered the correct Pincode Detail and still it didn't accept the given Input"
)

vehicle_number_regex = RegexValidator(
	regex=r'^[A-Z]{2}[ -][0-9]{1,2}(?: [A-Z])?(?: [A-Z]*)? [0-9]{1,4}$', 
	message="Invalid Number Plate Detail!\nContact Us, if you have entered the correct Number Plate Detail and sill it didn't accept the given Input"
)

# Choice fields
VEHICLE_TYPE = (
	('2 WHEELER', '2 WHEELER'),
	('4 WHEELER', '4 WHEELER'),
	('HEAVY VEHICLE', 'HEAVY VEHICLE'),
)

STATUS = (
	('Pending','Pending'),
	('Booked','Booked'),
	('Under Service','Under Service'),
	('Ready for delivery','Ready for delivery'),
	('Completed','Completed'),
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
		user = self.model(name=name, phone=phone, email=email, address=address, pin_code=pin_code, **extra_fields)
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
		verbose_name_plural = "User Detail"

	username = None
	first_name = None
	last_name = None

	name = models.CharField(max_length=50)
	email = models.EmailField(unique=True)
	phone = PhoneNumberField(max_length=13, unique=True)
	address = models.TextField()
	pin_code = models.CharField(max_length=10, validators=[pincode_regex])
	mechanic_threshold = models.IntegerField(default=5)
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

class Services(models.Model):
	class Meta:
		verbose_name_plural = "Service(s)"

	mechanic = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to=Q(groups__name = 'mechanics'), blank=True)
	service_name = models.CharField(max_length=30)
	desc = models.TextField()
	vehicle_type = models.CharField(max_length=15, choices=VEHICLE_TYPE)

	def __str__(self):
		return str(str(self.service_name) + ' - ' + str(self.vehicle_type))

class ServiceBooking(models.Model):
	class Meta:
		verbose_name_plural = "Service Booking(s)"

	customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer', limit_choices_to=Q(groups__name = 'customers'), blank=True)
	mechanic = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mechanic', limit_choices_to=Q(groups__name = 'mechanics'))
	vehicle_model =  models.CharField(max_length=50, verbose_name="Model")
	vehicle_number = models.CharField(max_length=20, verbose_name="number", validators=[vehicle_number_regex])
	service = ChainedForeignKey(Services, chained_field="mechanic", chained_model_field="mechanic", show_all=False, sort=True)
	issues = models.TextField(blank=True, null=True, verbose_name="Describe Any Specific Issues")
	status = models.CharField(max_length=50, choices=STATUS, default="Pending")
	booked_date = models.DateField(default=timezone.now, editable=False)
	service_date = models.DateField(default=timezone.now, editable=False)