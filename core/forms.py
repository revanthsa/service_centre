from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

# Custom form for creating new customers
class NewCustomerForm(UserCreationForm):
	class Meta:
		model = get_user_model()
		fields = ['name', 'email', 'phone', 'address', 'pin_code']

		help_texts = {
		'email': "You will be notified via E-mail, once your service has been completed.",
		'phone': "We will also call you, if we have any issues related the service that you've requested."
		}

		labels = {
		'name' : ' Enter your Name : ',
		'email' : ' Enter your E-mail : ',
		'phone':'Enter your Contact Number : ',
		'address':'Enter your Address : ',
		'pin code':'Enter your pincode : ',
		}

	def save(self, commit=True):
		user = super(NewCustomerForm, self).save(commit=False)
		if commit:
			user.save()
		return user