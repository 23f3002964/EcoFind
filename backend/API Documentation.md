# API Documentation: EcoFinds - Sustainable Second-Hand Marketplace

---

## 🔐 Authentication

### `POST /api/register`

**Description**: Register a new user.

* **Body** (JSON):

```json
{
  "email": "user@example.com",
  "username": "user123",
  "password": "securepass",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "1234567890",
  "address": "123 Street"
}
```

* **Responses**:

  * `201 Created`: User registered
  * `400 Bad Request`: Missing required fields
  * `409 Conflict`: Email or username already exists

---

### `POST /api/login`

**Description**: Log in a user.

* **Body** (JSON):

```json
{
  "email": "user@example.com",
  "password": "securepass"
}
```

* **Responses**:

  * `200 OK`: Login successful
  * `400/401`: Missing or invalid credentials

---

### `POST or GET /api/logout`

**Description**: Log out the current user.

* **Responses**:

  * `200 OK`: Logout successful

---

### `GET /api/user`

**Description**: Get current logged-in user.

* **Auth Required**: Yes
* **Response**:

  * `200 OK`: User data

---

### `PUT /api/user/profile`

**Description**: Update user profile.

* **Auth Required**: Yes
* **Body** (partial or full update):

```json
{
  "username": "new_username",
  "email": "new_email@example.com",
  "first_name": "New",
  "last_name": "Name",
  "phone_number": "9999999999",
  "address": "New Address",
  "password": "newpassword"
}
```

* **Responses**:

  * `200 OK`: Updated
  * `409 Conflict`: Username/email already taken

---

## 📦 Product Management

### `GET /api/products`

**Description**: List available (unsold) products.

* **Query Params**:

  * `category_id` (optional)
  * `q` (search query)
* **Response**:

  * `200 OK`: List of products

---

### `GET /api/products/<product_id>`

**Description**: Get product details by ID.

* **Response**:

  * `200 OK`: Product detail
  * `404 Not Found`: Invalid ID

---

### `POST /api/products`

**Description**: Create a new product listing.

* **Auth Required**: Yes
* **Body**:

```json
{
  "title": "Used Phone",
  "description": "Good condition",
  "price": 10000,
  "category_id": 1,
  "image_url": "https://example.com/image.jpg"
}
```

* **Responses**:

  * `201 Created`: Product added
  * `400/409`: Missing fields / invalid category

---

### `PUT /api/products/<product_id>`

**Description**: Update a product listing.

* **Auth Required**: Yes (must be seller)
* **Body**: Any fields to update
* **Responses**:

  * `200 OK`: Updated
  * `403 Forbidden`: Not seller

---

### `DELETE /api/products/<product_id>`

**Description**: Delete a product.

* **Auth Required**: Yes (must be seller)
* **Response**:

  * `200 OK`: Deleted

---

### `GET /api/user/products`

**Description**: Get products listed by current user.

* **Auth Required**: Yes
* **Response**:

  * `200 OK`: User's products

---

## 🗂️ Category Management

### `GET /api/categories`

**Description**: Get all product categories.

* **Response**:

  * `200 OK`: List of categories

### `POST /api/categories`

**Description**: Create a new category.

* **Auth Required**: Yes
* **Body**:

```json
{
  "name": "Books",
  "description": "All kinds of books"
}
```

* **Response**:

  * `201 Created`: Category added
  * `409 Conflict`: Already exists

---

## 🛒 Cart

### `GET /api/cart`

**Description**: Get all items in user's cart.

* **Auth Required**: Yes
* **Response**:

  * `200 OK`: List of cart items

### `POST /api/cart`

**Description**: Add a product to the cart.

* **Auth Required**: Yes
* **Body**:

```json
{
  "product_id": 2,
  "quantity": 1
}
```

* **Response**:

  * `201 Created`: Added
  * `400`: Already sold or missing

### `PUT /api/cart/<cart_item_id>`

**Description**: Update quantity or delete (if quantity=0).

* **Auth Required**: Yes
* **Body**:

```json
{
  "quantity": 2
}
```

* **Response**:

  * `200 OK`: Updated or deleted

### `DELETE /api/cart/<cart_item_id>`

**Description**: Remove an item from cart.

* **Auth Required**: Yes
* **Response**:

  * `200 OK`: Removed

---

## 💳 Purchases

### `POST /api/purchases`

**Description**: Checkout cart items.

* **Auth Required**: Yes
* **Response**:

  * `201 Created`: Purchase successful
  * `400`: Cart empty

### `GET /api/purchases`

**Description**: Get current user purchase history.

* **Auth Required**: Yes
* **Response**:

  * `200 OK`: List of purchases

### `GET /api/purchases/<purchase_id>`

**Description**: Get details of a single purchase.

* **Auth Required**: Yes
* **Response**:

  * `200 OK`: Purchase detail
  * `403 Forbidden`: Not your purchase

---

## ⚠️ Error Handlers

* `404 Not Found` → `{"error": "Resource not found"}`
* `500 Internal Server Error` → `{"error": "Internal server error"}`
* `401 Unauthorized` → `{"error": "Unauthorized"}`
* `403 Forbidden` → `{"error": "Forbidden"}`
