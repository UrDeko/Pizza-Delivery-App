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

### Register a customer

#### Request

`POST /register`
```
http://127.0.0.1:5000/register
```

#### Request Body

```
{
    "first_name": "Bridge",
    "last_name": "Malcolm",
    "email": "bmalcolm@mail.com",
    "password": "KL01@+",
    "phone": "0937345287"
}
```

#### Response

`201 CREATED`
```
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjkyNTg4NTMsInN1YiI6Mn0.OI-24mdmWCsswEhITClT2xfK4fpI1Jh-DRtFnco4vbQ"
}
```
**JSON Web Token that is used in the `Authorization` header in follow-up requests**

#### Errors

**One email cannot be used from two or more users!**

#### Request Body

```
{
    "first_name": " ",
    "last_name": " ",
    "email": "mail.com",
    "password": "KL01",
    "phone": "09abs"
}
```

#### Response

`400 BAD REQUEST`
```
{
    "message": "Invalid payload: {'email': ['Not a valid email address.'],
                                  'first_name': ['First name should consist of 2 or more characters'],
                                  'last_name': ['Last name should consist of 2 or more characters'], 
                                  'password': ['Invalid password. Required: uppercase - 2, numbers - 2, special - 2, nonletters - 2'],
                                  'phone': ['Invalid phone number']
                                 }"
}
```

### Login

#### Request

`POST /login`
```
http://127.0.0.1:5000/login
```

#### Request Body

```
{
    "email": "bmalcolm@mail.com",
    "password": "KL01@+"
}
```

#### Response

`200 OK`
```
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjkyNTkxNjgsInN1YiI6Mn0.shTRQaS5OW3xurqxcNKlKEG8umsbI4f9mYaf1H1uAHY"
}
```
**JSON Web Token that is used in the `Authorization` header in follow-up requests**

#### Errors

#### Request Body

```
{
    "email": "bmalcolm@mail.com",
    "password": "abv"
}
```

#### Response

`404 NOT FOUND`
```
{
    "message": "User not found"
}
```

### Add a product/pizza

**Permissions: `chef` only**

#### Request

`POST /products`
```
http://127.0.0.1:5000/products
```

#### Request Body

**Ingredients should be separated by `comma + space` in order for them to be properly evaluated**

```
{
    "name": "Margherita",
    "ingredients": "tomatoes, mozzarella, fresh basil leaves, extra virgin olive oil",
    "grammage": 350,
    "size": "s",
    "price": 4.50,
    "photo_url": "https://img.sndimg.com/food/image/upload/q_92,fl_progressive,w_1200,c_scale/v1/img/submissions/recipe/2001215136/SVs7T2FbTrmMpWri62fU_Margarita%20pizza.jpg"
}
```

#### Response

`201 CREATED`
```
{
    "message": "Product successfully created"
}
```

#### Errors

#### Request Body
```
{
    "name": "Margherita",
    "ingredients": "tomatoes, mozzarella, fresh basil leaves",
    "grammage": 0,
    "size": "k",
    "price": 0,
    "photo_url": "https://img.sndimg.com/food/image/upload/q_92,fl_progressive,w_1200,c_scale/v1/img/submissions/recipe/2001215136/SVs7T2FbTrmMpWri62fU_Margarita%20pizza.jpg"
}
```

#### Response

`400 BAD REQUEST`
```
{
    "message": "Invalid payload: {'size': ['Must be one of: s, m, l, j.'], 'grammage': ['Grammage should be above 0g'], 'price': ['Price should be above 0 BGN']}"
}
```

**If information for an existing product is inserted, error code `409 CONFLICT` is returned:**

### Get a list of all of the products/pizzas

**The `GET` method is public and available for either authenticated or non-authenticated users**

#### Request

`GET /products`
```
http://127.0.0.1:5000/products
```

#### Response

`200 OK`
```
[
    {
        "name": "Margherita",
        "ingredients": "tomatoes, mozzarella, fresh basil leaves, extra virgin olive oil",
        "size": "s",
        "grammage": 350,
        "price": "4.50",
        "photo_url": "https://img.sndimg.com/food/image/upload/q_92,fl_progressive,w_1200,c_scale/v1/img/submissions/recipe/2001215136/SVs7T2FbTrmMpWri62fU_Margarita%20pizza.jpg",
        "id": 1,
        "rating": "0"
    }
]
```

### Get info for a single product/pizza

**The `GET` method is public and available for either authenticated or non-authenticated users**

#### Request

`PUT /product/product_id`
```
http://127.0.0.1:5000/product/1
```

#### Response

`200 OK`
```
{
    "name": "Margherita",
    "ingredients": "tomatoes, mozzarella, fresh basil leaves, extra virgin olive oil",
    "size": "s",
    "grammage": 350,
    "price": "4.50",
    "photo_url": "https://img.sndimg.com/food/image/upload/q_92,fl_progressive,w_1200,c_scale/v1/img/submissions/recipe/2001215136/SVs7T2FbTrmMpWri62fU_Margarita%20pizza.jpg",
    "id": 1,
    "rating": "0"
}
```

#### Errors

**If an invalid product ID is inserted the following error will be raised:**

`404 NOT FOUNT`
```
{
    "message": "Product not found"
}
```

### Update product/pizza info

**Permissions: `chef` only**

#### Request

`PUT /product/product_id`
```
http://127.0.0.1:5000/product/1
```

#### Request Body
```
{
    "name": "Margherita",
    "ingredients": "tomatoes, mozzarella, fresh basil leaves, extra virgin olive oil",
    "grammage": 400,
    "size": "s",
    "price": 5.00,
    "photo_url": "https://img.sndimg.com/food/image/upload/q_92,fl_progressive,w_1200,c_scale/v1/img/submissions/recipe/2001215136/SVs7T2FbTrmMpWri62fU_Margarita%20pizza.jpg"
}
```

#### Response

`204 NO CONTENT'

#### Errors

**If an invalid product ID is inserted the following error will be raised:**

`404 NOT FOUNT`
```
{
    "message": "Product not found"
}
```

**The `PUT` method uses the same payload validation as `GET` which means that the same input constraints will be applied and the same errors will be raised**

### Delete product/pizza

**Permissions: `chef` only**

#### Request

`PUT /product/product_id`
```
http://127.0.0.1:5000/product/1
```

#### Response

`200 OK`
```
{
    "message": "Product deleted"
}
```

**If an invalid product ID is inserted the following error will be raised:**

`404 NOT FOUND`
```
{
    "message": "Product not found"
}
```


## Contributing

1. Fork the repository.
 
2. Create a new branch (git checkout -b feature/your-feature-name).
 
3. Commit your changes (git commit -m 'Add some feature').
 
4. Push to the branch (git push origin feature/your-feature-name).
   
5. Create a new Pull Request.
