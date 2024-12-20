# Co-Working Spaces Booking Application

This application is a decentralized web application designed specifically for booking co-working spaces. It offers a modern solution that prioritizes user data privacy and sovereignty. Unlike traditional centralized applications, this platform leverages the Solid framework integrated with Django and Python to ensure that users retain full control over their personal data. Solid PODs (Personal Online Datastores) are utilized to store user information, meaning data is kept in individual, user-managed pods rather than a central database. This approach enhances data security and privacy while aligning with the principles of data decentralization and user empowerment.

## Features

- **Decentralized Data Storage:** User data is stored in individual Solid PODs, ensuring privacy and control.
- **User-Friendly Interface:** Easy registration, login, and space management.
- **Secure Booking System:** Book and manage co-working spaces securely.

## Requirements

- Python 3.10 or above
- Django 5.0 or above
- Solid POD (Personal Online Datastore provided by [Solid Community](https://solidcommunity.net/))

## Installation

1. **Clone the Repository:**

```sh
   git clone https://gitlab.hrz.tu-chemnitz.de/vsr/edu/advising/ma-md-arifur-rahman-solid.git
   cd ma-md-arifur-rahman-solid

```

2. **Create and Activate a Virtual Environment:**

```sh
   python -m venv venv
   # On Mac/Linux
       source venv/bin/activate
   # On Windows
       venv\Scripts\activate
```

3. **Install Dependencies:**
```sh
   pip install -r requirements.txt
```
4. **Run the Development Server:**

```sh
   python manage.py runserver
```

4. **Open the Application in Your Browser:**

```sh
   Navigate to http://127.0.0.1:8000/ to access the application.
```

# Usage Instructions

## Registration and Login

1. **Registration:**

- Navigate to the registration page.
- Fill out the form with a unique username, password, name, and email.
- Click "Register" to create a new account. This will also create a new Solid POD and WebID for you.

1. **Login:**

- Go to the login page.
- Enter your username and password.
- Click "Login" to authenticate. Successful login will redirect you to the main dashboard.

# Managing Spaces

1. **Creating New Listings:**

- Log in.
- Select "Manage Spaces" tab or navigate to
  “http://127.0.0.1:8000/home/create-space/”.
- Fill out the form to create a new co-working space listing (details include availability, amenities, and prices).
- Click "Create" to save the listing in your Solid POD.

2. **Updating Listings:**

- In the "Manage Spaces" tab, find the listing you want to update.
- Click "Edit" next to the listing.
- Modify the details as necessary and click "Update" to save changes.

3. **Deleting Listings:**

- In the "Manage Spaces" tab, find the listing you want to delete.
- Click "Delete" next to the listing.
- Confirm the deletion. The listing will be removed from your Solid POD.
- Booking and Reservation

## Booking a Space:

1. **Booking a Space:**

- Log in.
- Select "Book a space" tab or navigate to
  “http://127.0.0.1:8000/home/all-data/”.
- Select a booking time.
- Click "Book" to save the booking information in your Solid POD.

2. **Managing Bookings:**

- Select "My Bookings" tab to view your bookings.
- All booking data is stored in your Solid POD, ensuring your data privacy and control.

