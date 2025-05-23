# EcoFind

**EcoFind** is a web platform designed to encourage reuse and reduce waste by allowing users to **buy and sell used goods**. Whether you're decluttering your home or searching for affordable items, EcoFind provides a sustainable and user-friendly marketplace.

## ✨ Key Features

- **User Authentication**: Secure registration and login for users.
- **Profile Management**: Users can view and update their profile information, including password changes.
- **Product Listings**: Sellers can list used items with images, descriptions, categories, and prices.
- **Browse & Search Products**: Users can browse all available products, search by keywords, and filter by category.
- **Product Detail View**: Dedicated page for each product showing detailed information.
- **My Listings Page**: Sellers can view and manage their own listed products.
- **Edit Product Listings**: Sellers can edit the details of their existing product listings.
- **Delete Product Listings**: Sellers can delete their products.
- **Shopping Cart**: Users can add products to a shopping cart.
- **Checkout Process**: Users can "purchase" items from their cart, marking products as sold.
- **Purchase History**: Users can view their past orders.

## 🎨 Key UI/UX Enhancements

Recent updates have focused on improving the user experience and interface:

- **Consistent Navigation Header**: Implemented a standardized header across all authenticated pages for easy navigation to Products, My Listings, Cart, and Profile, along with a Logout button.
- **Standardized Styling**: Applied consistent styling using Tailwind CSS for buttons, forms, cards, and typography, providing a modern and cohesive look and feel.
- **Product Detail Page**: Added a dedicated page for viewing detailed information about each product, including an "Add to Cart" function.
- **Improved User Feedback**: Replaced browser alerts with toast notifications for actions like login success/failure, product updates, items added to cart, etc. Standardized loading indicators provide visual feedback during data fetching and processing.
- **Full "Edit Product" Functionality**: Users can now fully edit their existing product listings through a dedicated form, pre-filled with the product's current details.
- **Clear "Sold" Item Handling**:
    - Sold items are no longer shown in general product listings.
    - On the "My Listings" page, sold items are clearly marked with a "SOLD" badge, and the "Edit" button is disabled for these items.
    - The Product Detail page for a sold item indicates its status and disables the "Add to Cart" button.

## 🛠️ Tech Stack

- **Frontend**: Vue.js (v3), Tailwind CSS
- **Backend**: Flask (Python)
- **Database**: SQLite (as per `app.py` configuration: `app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecofind.db'`)
- **JavaScript Libraries**: Axios (for some frontend API calls), `utils.js` (for global toast notifications).

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js and npm (primarily for Tailwind CSS if further development/compilation is needed, Vue.js is used via CDN)
- (Optional) Virtual environment tool like `venv`

---

### 🔧 Backend Setup (Flask)

1.  Clone the repository:
    ```bash
    git clone https://github.com/Aditya0612raj/EcoFind.git
    cd EcoFind/backend 
    ```
    *(Note: If you are working within a specific branch or fork, adjust the clone URL accordingly.)*

2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt 
    ```
    *(Ensure `requirements.txt` is up-to-date with all necessary packages like Flask, Flask-Login, Flask-SQLAlchemy, Flask-CORS, Werkzeug, etc.)*

4.  Initialize the database (if setting up for the first time):
    Open a Python interpreter in the `backend` directory:
    ```python
    from app import app, db
    with app.app_context():
        db.create_all()
    exit()
    ```

5.  Run the Flask server:
    ```bash
    flask run 
    ```
    The backend will typically run on `http://127.0.0.1:5000`.

---

### 🖥️ Frontend Setup (Vue.js & Tailwind CSS)

1.  The frontend files are located in the `EcoFind/frontend` directory.
2.  Vue.js is included via a CDN link in the HTML files, so no separate build step is strictly necessary for Vue itself.
3.  Tailwind CSS is also included via a CDN link. For development or customizing Tailwind, you would typically install it via npm and run its build process:
    ```bash
    # Example for setting up Tailwind for development (if not already done)
    # cd EcoFind/frontend 
    # npm install -D tailwindcss
    # npx tailwindcss init
    # npx tailwindcss -i ./path/to/your/input.css -o ./path/to/your/output.css --watch
    ```
    However, for simply running the existing files with CDN Tailwind, these steps are not immediately required.
4.  Serve the HTML files:
    *   You can open `frontend/index.html` directly in your browser.
    *   For a better experience, especially to avoid CORS issues if the backend is on a different port, use a simple HTTP server or a live server extension (like "Go Live" in VS Code if it handles paths correctly for static assets like `utils.js`).
    *   Example using Python's HTTP server (from the `EcoFind` root directory):
        ```bash
        python -m http.server --directory frontend 8080 
        ```
        Then open your browser and visit: `http://localhost:8080/frontend/index.html` or other relevant HTML files.
        *(Adjust port if 8080 is in use. Ensure your API calls in JS point to the correct backend URL, e.g., `http://127.0.0.1:5000/api/...`)*

---

## 📸 Screenshots/Video

The project includes various UI enhancements for a smoother user experience.
*(The existing video link provides a general overview: [EcoFind Video Demo](https://drive.google.com/file/d/16EgGOiX6Iv6Er267ZwXWqtfSchsFqOFv/view?usp=drive_link))*

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.

---

## 📄 License

This project is licensed under the **MIT License**.
