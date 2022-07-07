# Merak
Merak is a software that provides appropritate tool for inventory management, staff tracking, and accounting.

# Features

## Inventory Management

  - Product
  - Order
 

## Staff Tracking

  - Active Tracking
  - Attendance
  - Customer
  
## Accounting

  - Expense
  - Invoices
  
# Installation

- [X] Clone this repository
- [X] Install [python](https://www.python.org/)
- [X] After installation navigate to the project directory

After installation generally creating a virtual enviornment is recommended.
```pythom -m venv venv```

Then activate the venv and install the requirements.
```pip install -r requirements.txt```

After the installation is done the server can be easily booted using the basic command.
```python manage.py runserver```

# Try it out

### Link
Here is the link to the default admin-dashboard.

https://merak-test.herokuapp.com/admin/

### Credentials
```
email: admin@admin.com
pass : root
```

### Using Api
Every api calls requires `jwt token` which can be fetched by using POST request in:

https://merak-test.herokuapp.com/user/auth/login/

with credentials:
```
{
    "email":"admin@admin.com",
    "password":"root"
}
```
From which you will get a response with `Refresh Token` and `Access Token`
```
{
  "refresh": "",
  "access": ""
}
```
For every api request you are required to send the `Access Token` on authorization hearder like such:

```
Bearer <Access Token>
```
![image](https://user-images.githubusercontent.com/48282663/177761096-aef06cb8-e509-47d4-a56a-f17c3b63ae04.png)


# API Documentation
This project consist of auto generated documentation which can be accessed here:

https://merak-test.herokuapp.com/swagger/

https://merak-test.herokuapp.com/redoc/

