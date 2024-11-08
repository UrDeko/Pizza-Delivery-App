# Pizza Delivery App

A RESTful API for managing a pizza delivery service, built with Flask, Flask-RESTful, and SQLAlchemy. This application allows users to register, order pizzas, track order statuses, and handle payments via PayPal.

## Features

- **User Authentication**: User registration, login, and password management.
- **Pizza Management**: Manage pizza types, sizes, and details.
- **Order Management**: Create and manage orders with various statuses (pending, in transition, delivered).
- **Payment Processing**: Integrate with PayPal for payment capture.
- **User Management**: Admin functionalities to manage user profiles.
- **File Management**: Save files in the cloud via the Amazon S3 service.
- **Email Management**: Send emails via Amazon Simple Email Service (SES).
- **SMS Notifications**: Send SMS messages using the Twilio API.

## Prerequisites

- Python 3.10+
- PostgreSQL (or a configured database compatible with SQLAlchemy)

1. **Create a virtual environment (recommended):**

```
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate
```

2. **Install the dependencies:**

```
pip install -r requirements.txt
```

3. **Set up environment variables: Create a `.env` file in the root directory and add the following:**

```
DB_USER=your_db_user
DB_PASS=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_db_name
ENVIRONMENT=DevelopmentEnvironment  # or ProductionEnvironment
TWILIO_SID=your_twilio_sid
TWILIO_TOKEN=your_twilio_token
TWILIO_NUMBER=your_twilio_number
TWILIO_VERIFIED_NUMBER=your_twilio_verified_number
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
AWS_BUCKET=your_aws_bucket
AWS_REGION=your_aws_region
SES_EMAIL_SENDER=your_ses_email_sender
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
```

## Configuration

The application configuration is handled through environment-based classes in `config.py`:

* DevelopmentEnvironment: For local development with debug mode enabled.
* ProductionEnvironment: For deployment with debug mode disabled.

Set the environment using the `.env` file.

## Usage

1. **Run the application**

```
flask run
```

2. **Access the application: Open a web browser and go to `http://127.0.0.1:5000`.**

## Database Setup

1. **Initialize the database:**

   ```
   flask db init
   ```

2. **Apply migrations:**

   ```
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

## Models
The application uses SQLAlchemy models for the following entities:

- **User: Stores user information and credentials.**
- **Pizza: Represents different types of pizzas available.**
- **PizzaSize: Represents available pizza sizes.**
- **Order: Stores order details and tracks order status.**
- **OrderItem: Stores individual items in an order, linking Order and Pizza.**
- **UnpaidOrder: Stores order details temporarily until the payment is captured.**
- **UnpaidOrderItem: Stores individual items in an unpaid order.**

## API Endpoints

The routes are dynamically added from the resources.routes module.

- `POST /login` - public
- `POST /register` - public
- `POST /users` - login required; rights: admin
- `DELETE /users/<ID>` - login required; rights: admin
- `POST /user/change-password` - login required
- `GET /orders` - login required
- `POST /orders` - login required; righs: customer
- `DELETE /orders` - login required; rights: deliver, admin
- `GET /order/<ID>` - login required; rights: deliver, admin
- `DELETE /order/<ID>` - login required; rights: deliver, admin
- `PUT /order/<ID>/pending` - login required; rights: deliver, admin
- `PUT /order/<ID>/in-transition` - login required; rights: deliver, admin
- `PUT /order/<ID>/delivered` - login required; rights: deliver, admin
- `GET /pizzas` - public
- `POST /pizzas` - login required; rights: chef, admin
- `GET /pizza/<ID>` - public
- `PUT /pizza/<ID>` - login required; rights: chef, admin
- `DELETE /pizza/<ID>` - login required; rights: chef, admin
- `POST /pizza-sizes` - login required; rights: chef, admin
- `PUT /pizza-size/<ID>` - login required; rights: chef, admin
- `DELETE /pizza-size/<ID>` - login required; rights: chef, admin

## Contributing

1. Fork the repository.
 
2. Create a new branch (git checkout -b feature/your-feature-name).
 
3. Commit your changes (git commit -m 'Add some feature').
 
4. Push to the branch (git push origin feature/your-feature-name).
   
5. Create a new Pull Request.
