# Pizza Delivery App


## Brief overview

A RESTful API created using Python and Flask. The application uses relational database model based on PostgreSQL and the database interraction is held by Flask's SQLAlchemy ORM package. JWT is used as a method for authentication. In order to be authorized for perfoming certain actions a user needs to be registered as either `admin`, `chef`, `deliver` or `customer`. The data that is part of the body of each request is validated by using schemas from the Python's Marshmallow package.

## Run application

```
python app.py
```

## Register a customer

### Request

`POST /register`
```
http://127.0.0.1:5000/register
```

### Request Body

```
{
    "first_name": "Bridge",
    "last_name": "Malcolm",
    "email": "bmalcolm@mail.com",
    "password": "KL01@+",
    "phone": "0937345287"
}
```

### Response

`201 CREATED`
```
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjkyNTg4NTMsInN1YiI6Mn0.OI-24mdmWCsswEhITClT2xfK4fpI1Jh-DRtFnco4vbQ"
}
```
**JSON Web Token that is used in the `Authorization` header in follow-up requests**

### Errors

**One email cannot be used from two or more users!**

### Request Body

```
{
    "first_name": " ",
    "last_name": " ",
    "email": "mail.com",
    "password": "KL01",
    "phone": "09abs"
}
```

### Response

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

## Login

### Request

`POST /login`
```
http://127.0.0.1:5000/login
```

### Request Body

```
{
    "email": "bmalcolm@mail.com",
    "password": "KL01@+"
}
```

### Response

`200 OK`
```
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjkyNTkxNjgsInN1YiI6Mn0.shTRQaS5OW3xurqxcNKlKEG8umsbI4f9mYaf1H1uAHY"
}
```
**JSON Web Token that is used in the `Authorization` header in follow-up requests**

### Errors

### Request Body

```
{
    "email": "bmalcolm@mail.com",
    "password": "abv"
}
```

### Response

`404 NOT FOUND`
```
{
    "message": "User not found"
}
```

## Add a product/pizza

**Permissions: `chef` only**

### Request

`POST /products`
```
http://127.0.0.1:5000/products
```

### Request Body

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

### Response

`201 CREATED`
```
{
    "message": "Product successfully created"
}
```

### Errors

### Request Body
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

### Response

`400 BAD REQUEST`
```
{
    "message": "Invalid payload: {'size': ['Must be one of: s, m, l, j.'], 'grammage': ['Grammage should be above 0g'], 'price': ['Price should be above 0 BGN']}"
}
```

**If information for an existing product is inserted, error code `409 CONFLICT` is returned:**

## Get a list of all of the products/pizzas

**The `GET` method is public and available for either authenticated or non-authenticated users**

### Request

`GET /products`
```
http://127.0.0.1:5000/products
```

### Response

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

## Get info for a single product/pizza

**The `GET` method is public and available for either authenticated or non-authenticated users**

### Request

`PUT /product/product_id`
```
http://127.0.0.1:5000/product/1
```

### Response

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

### Errors

**If an invalid product ID is inserted the following error will be raised:**

`404 NOT FOUNT`
```
{
    "message": "Product not found"
}
```

## Update product/pizza info

**Permissions: `chef` only**

### Request

`PUT /product/product_id`
```
http://127.0.0.1:5000/product/1
```

### Request Body
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

### Response

`204 NO CONTENT'

### Errors

**If an invalid product ID is inserted the following error will be raised:**

`404 NOT FOUNT`
```
{
    "message": "Product not found"
}
```

**The `PUT` method uses the same payload validation as `GET` which means that the same input constraints will be applied and the same errors will be raised**

## Delete product/pizza

**Permissions: `chef` only**

### Request

`PUT /product/product_id`
```
http://127.0.0.1:5000/product/1
```

### Response

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
