# SteerX
It is a Django web based online platform for booking automobile services.

# Specifications

### Mechanics:
```bash
- Should be able to create / edit / delete all services and their details
- View a list of all bookings (pending, ready for delivery and completed)
- View details of each booking.
- Ability to accept or deny the booking, as well as alter the status of the scheduled service
- Can set threshold to auto accept the Service bookings
- Receive an email whenever a booking is made
```

### Customers:
```bash
- Should be able to register for an account with email address
- Can sort mechanics based on their location, requirements, and availability
- Book a service at a particular date
- See the status of his booking
- See all his previous bookings
- Receive an email as soon as his booking is ready for delivery
```

## Installing requirements: (Install python (min_ver: 3.7.8) before using pip (min_ver: 20.1.1) commands):
Creating an virtual environment is recommended

```bash
pip install -r requirements.txt
```

## Perform database migration:
By default, Django takes the sqlite as the Database.
Change the DATABASES dictionary in the settings.py file to use the local database.
```bash
python manage.py makemigrations
python manage.py migrate
```

## Create superuser:
```bash
python manage.py createsuperuser
```

## Run Development Server:
```bash
python manage.py runserver
```

## Links
#### Localhost: [Local EndPoint](http://localhost:8000) and [For Admin usage](http://localhost:8000/login)
