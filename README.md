# ShopEase - E-Commerce Web Application

ShopEase is a robust, responsive, session-based e-commerce web application built using Python, Django, and Vanilla JavaScript/CSS. 

## Features
- **Product Browsing:** Filter by category, sort by price, view product details, and pagination.
- **Cart System:** Fully session-based anonymous and logged-in cart logic preventing accidental loss of DB constraints.
- **Authentication:** Custom OTP (One-Time Password) based two-step registration and login flows.
- **Checkout & Orders:** E2E multi-step checkout with simulated payment gateway (Cards/UPI/COD).
- **Security:** Built with `.env` based configurations, CSRF protection, and standardized header restrictions.
- **Admin Panel:** Fully hooked standard Django admin panel to manage products, categories, orders, layout.

## Setup & Dependencies
1. Create and activate a Virtual Environment.
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your environment variables (a default `.env` is provided).
4. Run standard Django setup (Migrations are already applied):
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## Demo Credentials
* User: `admin`
* Password: `admin123`

Orders and stock can be manipulated through the standard Django `/admin/` portal.

## Testing System
Ensure to run end-to-end validation through the included test script:
```bash
python test_e2e.py
```
*(Cleans up test environment autonomously).*
