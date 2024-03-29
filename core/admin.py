from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import *
from django.utils.safestring import mark_safe

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
		(_('Personal info'), {'fields': ('name', 'phone', 'address', 'pin_code', 'mechanic_threshold')}),
		(_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
		                               'groups', 'user_permissions')}),
		(_('Important dates'), {'fields': ('last_login', 'date_joined')}),
	)
	staff_fieldsets = (
		(None, {'fields': ('email', 'password')}),
		(_('Personal info'), {'fields': ('name', 'phone', 'address', 'pin_code', 'mechanic_threshold')}),
		(_('Important dates'), {'fields': ('last_login', 'date_joined')}),
	)
	customer_fieldsets = (
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
			if request.user.groups.filter(name='customers').exists():
				return self.customer_fieldsets
			return self.staff_fieldsets
		else:
			return super(CustomUserAdmin, self).get_fieldsets(request, obj)

	def get_queryset(self, request):
		if not request.user.is_superuser:
			if request.user.groups.filter(name='customers').exists():
				return User.objects.filter(email=request.user.email)
		return User.objects.all()

class ServicesAdmin(admin.ModelAdmin):
	mech_list_display = ["service_name", "vehicle_type", "desc", "mechanic"]
	customer_list_display = ["service_name", "vehicle_type", "desc", "mechanic", "getAddService"]
	search_fields = ["mechanic__email", "service_name", "desc"]
	list_filter = ["vehicle_type"]
	staff_readonly_fields = ('mechanic',)
	customer_readonly_fields = ('service_name', 'vehicle_type', 'desc', 'mechanic')


	def get_list_display(self, request):
		if not request.user.is_superuser:
			if request.user.groups.filter(name='customers').exists():
				return self.customer_list_display
			return self.mech_list_display
		return super().get_list_display(request)

	def getAddService(self, ServicesAdmin):
		url = '/dashboard/core/servicebooking/add/'
		# <button type="submit" class="btn btn-fill btn-sm btn-primary" title="{% trans "Run the selected action" %}" name="index" value="{{ action_index|default:0 }}">
        #         {% trans "Book a Service" %}
        # </button>
		return mark_safe("""<a href="{url}" class="btn btn-fill btn-sm btn-primary" target="_blank">{text}</a>""".format(url=url,text=_("Book a Service"),))
	getAddService.short_description = _("Book Service")

	def get_readonly_fields(self, request, obj=None):
		if not request.user.is_superuser:
			if request.user.groups.filter(name='customers').exists():
				return self.customer_readonly_fields
			return self.staff_readonly_fields
		else:
			return super(ServicesAdmin, self).get_readonly_fields(request, obj)

	def get_queryset(self, request):
		if not request.user.is_superuser:
			if request.user.groups.filter(name='mechanics').exists():
				return Services.objects.filter(mechanic__email=request.user.email)
			elif request.user.groups.filter(name='customers').exists():
				# return Services.objects.filter(mechanic__pin_code=request.user.pin_code)
				return Services.objects.all()
		return Services.objects.all()
	
	def save_model(self, request, obj, form, change):
		if not obj.pk and request.user.groups.filter(name='mechanics').exists():
			obj.mechanic = request.user
		super().save_model(request, obj, form, change)

class ServiceBookingAdmin(admin.ModelAdmin):
	customer_list_display = ["mechanic", "service", "service_date", "vehicle_number", "status"]
	mech_list_display = ["customer", "service", "service_date", "vehicle_number", "status"]
	search_fields = ["customer", "mechanic", "vehicle_number" ,"vehicle_model", "service__service_name", "service_date", "status", "booked_date"]
	list_filter = ["service", "status"]
	ordering = ('service_date',)
	# autocomplete_fields = ('mechanic', 'service',)
	mechanic_readonly_fields = ('customer', 'mechanic', 'service', 'issues', 'service_date', 'vehicle_model', 'vehicle_number', 'booked_date',)
	customer_readonly_fields = ('customer', 'status', 'booked_date', 'payable_amount', 'delivery_date',)
	all_readonly_fields = [field.name for field in ServiceBooking._meta.fields]

	def get_list_display(self, request):
		if not request.user.is_superuser:
			if request.user.groups.filter(name='customers').exists():
				return self.customer_list_display
			return self.mech_list_display
		return super().get_list_display(request)

	def get_readonly_fields(self, request, obj=None):
		if request.user.groups.filter(name='mechanics').exists():
			if obj:
				if obj.status in ['Completed', 'Ready for delivery']:
					return self.all_readonly_fields
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
	
	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if request.user.groups.filter(name='customers').exists():
			if db_field.name == "mechanic":
				kwargs["queryset"] = Users.objects.filter(pin_code=request.user.pin_code)
		return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Services, ServicesAdmin)
admin.site.register(ServiceBooking, ServiceBookingAdmin)
