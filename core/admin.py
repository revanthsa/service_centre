from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import *

# Few customizations
admin.site.site_title = "Steerx Login"
admin.site.index_title = "Steerx - Dashboard"
admin.site.site_header = "Steerx - Service"

# Register your models here.

User = get_user_model()

# User Model views based on user type
class CustomUserAdmin(UserAdmin):
	fieldsets = (
		(None, {'fields': ('email', 'password')}),
		(_('Personal info'), {'fields': ('name', 'phone', 'address', 'pin_code')}),
		(_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
		                               'groups', 'user_permissions')}),
		(_('Important dates'), {'fields': ('last_login', 'date_joined')}),
	)
	staff_fieldsets = (
		(None, {'fields': ('email', 'password')}),
		(_('Personal info'), {'fields': ('name', 'phone', 'address', 'pin_code')}),
		(_('Important dates'), {'fields': ('last_login', 'date_joined')}),
	)
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('email', 'name', 'phone', 'address', 'pin_code', 'password1', 'password2'),
		}),
	)
	list_display = ('email', 'name', 'phone', 'is_staff',)
	search_fields = ('name', 'phone', 'email', 'pin_code',)
	ordering = ('date_joined',)
	staff_readonly_fields = ('last_login', 'date_joined', 'email',)

	def get_readonly_fields(self, request, obj=None):
		if not request.user.is_superuser:
			return self.staff_readonly_fields
		else:
			return super(CustomUserAdmin, self).get_readonly_fields(request, obj)

	def get_fieldsets(self, request, obj=None):
		if not request.user.is_superuser:
			return self.staff_fieldsets
		else:
			return super(CustomUserAdmin, self).get_fieldsets(request, obj)

	def get_queryset(self, request):
		if not request.user.is_superuser:
			if request.user.groups.filter(name='customers').exists():
				return User.objects.filter(email=request.user.email)
		return User.objects.all()

class ServicesAdmin(admin.ModelAdmin):
	list_display = ["service_name", "vehicle_type", "desc", "mechanic"]
	search_fields = ["mechanic__email", "service_name"]
	list_filter = ["vehicle_type"]
	staff_readonly_fields = ('mechanic',)

	def get_readonly_fields(self, request, obj=None):
		if not request.user.is_superuser:
			return self.staff_readonly_fields
		else:
			return super(ServicesAdmin, self).get_readonly_fields(request, obj)

	def get_queryset(self, request):
		if not request.user.is_superuser:
			if request.user.groups.filter(name='mechanics').exists():
				return Services.objects.filter(mechanic__email=request.user.email)
		return Services.objects.all()
	
	def save_model(self, request, obj, form, change):
		if not obj.pk and request.user.groups.filter(name='mechanics').exists():
			obj.mechanic = request.user
		super().save_model(request, obj, form, change)

class ServiceBookingAdmin(admin.ModelAdmin):
	list_display = ["customer", "service", "service_date", "vehicle_number", "status"]
	search_fields = ["customer", "mechanic", "vehicle_number" ,"vehicle_model", "service__service_name", "service_date", "status", "booked_date"]
	list_filter = ["service", "status"]
	ordering = ('service_date',)
	# autocomplete_fields = ('mechanic', 'service',)
	mechanic_readonly_fields = ('customer', 'mechanic', 'service', 'issues', 'service_date', 'vehicle_model', 'vehicle_number', 'booked_date',)
	customer_readonly_fields = ('customer', 'status', 'booked_date',)
	all_readonly_fields = [field.name for field in ServiceBooking._meta.fields]

	def get_readonly_fields(self, request, obj=None):
		if request.user.groups.filter(name='mechanics').exists():
			return self.mechanic_readonly_fields
		elif request.user.groups.filter(name='customers').exists():
			if obj:
				if obj.status in ['Completed', 'Ready for delivery']:
					return self.all_readonly_fields
			return self.customer_readonly_fields
		return super(ServiceBookingAdmin, self).get_readonly_fields(request, obj)

	def get_queryset(self, request):
		if not request.user.is_superuser:
			if request.user.groups.filter(name='customers').exists():
				return ServiceBooking.objects.filter(customer__email=request.user.email)
			elif request.user.groups.filter(name='mechanics').exists():
				return ServiceBooking.objects.filter(mechanic__email=request.user.email)
		return ServiceBooking.objects.all()

	def save_model(self, request, obj, form, change):
		if not obj.pk and request.user.groups.filter(name='customers').exists():
			obj.customer = request.user
		super().save_model(request, obj, form, change)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Services, ServicesAdmin)
admin.site.register(ServiceBooking, ServiceBookingAdmin)
