
# 🍔 FoodOnline – Online Food Ordering System

FoodOnline is a Django-based web application designed to provide users with an easy and convenient way to browse food items, manage their profiles, save delivery addresses, and place food orders.

The project is being developed step by step using Django, Python, HTML, CSS, Bootstrap, and SQLite.

## 🚀 Project Features

### 1. User Authentication & Accounts
- User Registration
- User Login and Logout
- User Profile Management
- Update Personal Information
- Change Password
- Login Required Authentication
- Success and Error Messages

### 2. Address Management
- Add Delivery Address
- View Saved Addresses
- Edit Existing Address
- Delete Address
- Set Default Delivery Address
- Manage Multiple Addresses

### 3. Food Menu Management
- Food Categories
- Restaurant Management
- Food Item Management
- Food Information and Pricing
- Django Admin Integration

### 4. Shopping Cart (In Progress)
- Add Food Items to Cart
- Automatically Increase Item Quantity
- Manage Cart Items
- Calculate Subtotal
- Remove Items from Cart

### 5. Order Management (Planned)
- Checkout System
- Place Food Orders
- Order History
- Order Tracking
- Order Status Management

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend Programming |
| Django | Backend Web Framework |
| SQLite | Database |
| HTML5 | Web Page Structure |
| CSS3 | Styling |
| Bootstrap 5 | Responsive UI |
| JavaScript | Frontend Interactions |
| Django ORM | Database Operations |
| Django Admin | Data Management |
| Git & GitHub | Version Control |

## 📂 Project Structure

```text
FoodOnline/
│
├── accounts/
│   ├── migrations/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── signals.py
│
├── cart/
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── core/
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── menu/
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── orders/
│   ├── migrations/
│   ├── models.py
│   ├── admin.py
│   └── views.py
│
├── templates/
│   ├── accounts/
│   ├── cart/
│   ├── core/
│   ├── menu/
│   ├── orders/
│   ├── partials/
│   └── base.html
│
├── static/
├── media/
├── manage.py
└── requirements.txt
```

## ⚙️ Installation and Setup

Follow these steps to run the project locally.

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Navigate to the Project Directory

```bash
cd FoodOnline
```

### 3. Create a Virtual Environment

```bash
python -m venv env
```

### 4. Activate the Virtual Environment

For Windows:

```bash
env\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Apply Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create a Superuser

```bash
python manage.py createsuperuser
```

### 8. Run the Development Server

```bash
python manage.py runserver
```

Open the application in your browser:

```text
http://127.0.0.1:8000/
```

Django Admin:

```text
http://127.0.0.1:8000/admin/
```

## 🗄️ Database Models

The project uses Django ORM to manage database relationships.

Some important models include:

- User – Stores user authentication information.
- Profile – Stores additional user information.
- Address – Stores user delivery addresses.
- Category – Stores food categories.
- Restaurant – Stores restaurant information.
- Food – Stores food item details.
- Cart – Stores the user's shopping cart.
- CartItem – Stores food items and their quantities.
- Order – Stores customer order information.
- OrderItem – Stores individual items within an order.

## 📸 Application Screenshots

Screenshots of the application will be added as development progresses.

Planned screenshots:

- Homepage
  <img width="1744" height="831" alt="image" src="https://github.com/user-attachments/assets/d84a9201-78aa-4983-b84a-fdecfb20d50e" />

- Registration Page
  <img width="1512" height="905" alt="image" src="https://github.com/user-attachments/assets/f8320088-e86b-475a-a071-93f7e9bbe896" />

- Login Page
  <img width="1579" height="900" alt="image" src="https://github.com/user-attachments/assets/841f8780-dcb0-40f4-816b-89bab71c5dd7" />

- User Profile
  <img width="1541" height="907" alt="image" src="https://github.com/user-attachments/assets/1ee6df01-7a38-4261-a145-110ca4c61acd" />


- Address Management
  <img width="1620" height="899" alt="image" src="https://github.com/user-attachments/assets/bb103071-6363-4905-b4d9-32c342d04db3" />

- Food Menu
  <img width="1520" height="896" alt="image" src="https://github.com/user-attachments/assets/24bddda8-1730-4ed9-ac68-661c0942bfcf" />

- Shopping Cart
  <img width="1614" height="827" alt="image" src="https://github.com/user-attachments/assets/0e7daafd-b3c3-49f9-ad18-c98b69558be4" />

- Checkout Page
  <img width="1610" height="896" alt="image" src="https://github.com/user-attachments/assets/55691d7a-ae89-49be-b582-dd20c8cf32c7" />

- Django Admin Dashboard
  <img width="1894" height="903" alt="image" src="https://github.com/user-attachments/assets/f0679eb4-7c1b-4b80-977b-c7b527a795a7" />

## 🎯 Project Objectives

- Develop a full-stack web application using Django.
- Understand Django MVT architecture.
- Implement user authentication and authorization.
- Perform database operations using Django ORM.
- Build reusable templates using Django Template Language.
- Implement database relationships using ForeignKey and OneToOneField.
- Develop shopping cart and order management functionality.
- Create a responsive and user-friendly interface.

## 🔮 Future Enhancements

- Restaurant Search and Filtering
- Food Search Functionality
- Shopping Cart Management
- Checkout and Payment Integration
- Order Tracking
- Order History
- User Reviews and Ratings
- Responsive Design Improvements

## 👨‍💻 Developer

**Sumit Todkar**

B.Tech – Electronics & Computer Science  
Honors – Artificial Intelligence and Machine Learning

## 📌 Project Status

**Currently Under Development**

FoodOnline is being developed incrementally, with a focus on understanding Django concepts and implementing each feature step by step.

---

⭐ If you find this project interesting, feel free to explore the repository!
