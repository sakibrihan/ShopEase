"""
End-to-end test for the ShopEase e-commerce application.
Tests the complete user flow: register -> OTP -> login -> cart -> checkout -> payment -> orders.
"""
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'ecommerce.settings'

import django
django.setup()

from django.test import Client, TestCase
from django.contrib.auth.models import User
from products.models import Product
from orders.models import Order, OrderItem
from accounts.models import OTP

results = []


def test(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append((name, status, detail))
    icon = "+" if condition else "X"
    print(f"  [{icon}] {name}" + (f" ({detail})" if detail else ""))
    return condition


print("=" * 60)
print("  ShopEase - End-to-End Test Suite")
print("=" * 60)

# Clean up leftover test data from previous runs
test_usernames = ['testuser', 'otheruser', 'debuguser']
cleanup_count = User.objects.filter(username__in=test_usernames).count()
if cleanup_count:
    User.objects.filter(username__in=test_usernames).delete()
    print(f"  [cleanup] Removed {cleanup_count} leftover test user(s)")

c = Client()

# ============================================
# 1. PUBLIC PAGES
# ============================================
print("\n--- PUBLIC PAGES ---")

r = c.get('/')
test("Homepage loads", r.status_code == 200)
content = r.content.decode()
test("Homepage has hero", "Welcome to ShopEase" in content)
test("Homepage has Shop Now", "Shop Now" in content)
test("Homepage has categories", "Electronics" in content)

r = c.get('/products/')
test("Product list loads", r.status_code == 200)
test("Product list has products", "card-title" in r.content.decode())

# Search
r = c.get('/products/?q=headphones')
test("Search works", r.status_code == 200 and "Wireless Headphones" in r.content.decode())

# Category filter
r = c.get('/products/?category=electronics')
test("Category filter works", r.status_code == 200 and "Bluetooth Speaker" in r.content.decode())

# Sort
r = c.get('/products/?sort=price_low')
test("Sort by price works", r.status_code == 200)

# Product detail
p = Product.objects.first()
r = c.get(f'/products/{p.id}/')
test("Product detail loads", r.status_code == 200 and p.name in r.content.decode())

# Product 404
r = c.get('/products/99999/')
test("Invalid product returns 404", r.status_code == 404)

# ============================================
# 2. CART (Anonymous)
# ============================================
print("\n--- CART (Anonymous) ---")

r = c.get('/cart/')
test("Cart page loads", r.status_code == 200)
test("Cart is empty", "Your cart is empty" in r.content.decode())

# Add to cart
p = Product.objects.filter(stock__gt=0).first()
r = c.post(f'/cart/add/{p.id}/', {'quantity': 2})
test("Add to cart redirects", r.status_code == 302)

r = c.get('/cart/')
content = r.content.decode()
test("Cart has product", p.name in content)

# Update cart
r = c.post(f'/cart/update/{p.id}/', {'quantity': 3})
test("Update cart redirects", r.status_code == 302)

# Remove from cart
r = c.post(f'/cart/remove/{p.id}/')
test("Remove from cart redirects", r.status_code == 302)

r = c.get('/cart/')
test("Cart empty after remove", "Your cart is empty" in r.content.decode())

# ============================================
# 3. AUTHENTICATION
# ============================================
print("\n--- AUTHENTICATION ---")

r = c.get('/accounts/login/')
test("Login page loads", r.status_code == 200 and "Welcome Back" in r.content.decode())

r = c.get('/accounts/register/')
test("Register page loads", r.status_code == 200 and "Create Account" in r.content.decode())

# Register a new user
r = c.post('/accounts/register/', {
    'username': 'testuser',
    'email': 'test@example.com',
    'password1': 'TestPass123!',
    'password2': 'TestPass123!',
})
test("Registration redirects to OTP", r.status_code == 302 and '/verify-otp' in r.url)

# Check user was created (inactive)
user = User.objects.get(username='testuser')
test("User created", user is not None)
test("User is inactive (pre-OTP)", not user.is_active)

# Check OTP was created
otp_obj = OTP.objects.get(user=user)
test("OTP created", otp_obj is not None)
test("OTP is 6 digits", len(otp_obj.otp) == 6 and otp_obj.otp.isdigit())
test("OTP not verified yet", not otp_obj.verified)

# Verify OTP page loads
r = c.get('/accounts/verify-otp/')
content = r.content.decode()
test("OTP page loads", r.status_code == 200)
test("OTP page shows demo OTP", otp_obj.otp in content)

# Submit wrong OTP
r = c.post('/accounts/verify-otp/', {'otp': '000000'})
test("Wrong OTP shows error", r.status_code == 200)
otp_obj.refresh_from_db()
test("OTP attempts incremented", otp_obj.attempts == 1)

# Submit correct OTP
r = c.post('/accounts/verify-otp/', {'otp': otp_obj.otp})
test("Correct OTP redirects to login", r.status_code == 302 and '/login' in r.url)

user.refresh_from_db()
test("User is now active", user.is_active)

otp_obj.refresh_from_db()
test("OTP marked verified", otp_obj.verified)

# Login with wrong password
r = c.post('/accounts/login/', {'username': 'testuser', 'password': 'wrongpass'})
test("Wrong password stays on login", r.status_code == 200)

# Login with correct password
r = c.post('/accounts/login/', {'username': 'testuser', 'password': 'TestPass123!'})
test("Correct login redirects", r.status_code == 302)

# Profile
r = c.get('/accounts/profile/')
test("Profile page loads", r.status_code == 200 and 'testuser' in r.content.decode())

# ============================================
# 4. DUPLICATE REGISTRATION
# ============================================
print("\n--- DUPLICATE HANDLING ---")

c2 = Client()
r = c2.post('/accounts/register/', {
    'username': 'testuser',
    'email': 'test2@example.com',
    'password1': 'TestPass123!',
    'password2': 'TestPass123!',
})
test("Duplicate username rejected", r.status_code == 200, "stays on form")

# ============================================
# 5. CART + CHECKOUT FLOW (Authenticated)
# ============================================
print("\n--- CART + CHECKOUT (Authenticated) ---")

# Add products to cart
p1 = Product.objects.filter(stock__gt=0)[0]
p2 = Product.objects.filter(stock__gt=0)[1]
original_stock_p1 = p1.stock
original_stock_p2 = p2.stock

r = c.post(f'/cart/add/{p1.id}/', {'quantity': 2})
test("Add product 1 to cart", r.status_code == 302)

r = c.post(f'/cart/add/{p2.id}/', {'quantity': 1})
test("Add product 2 to cart", r.status_code == 302)

r = c.get('/cart/')
content = r.content.decode()
test("Cart has both products", p1.name in content and p2.name in content)

# ============================================
# 6. CHECKOUT
# ============================================
print("\n--- CHECKOUT ---")

r = c.get('/checkout/')
test("Checkout page loads", r.status_code == 200 and "Shipping Information" in r.content.decode())

# Submit shipping info
r = c.post('/checkout/', {
    'full_name': 'Test User',
    'email': 'test@example.com',
    'phone': '9876543210',
    'address': '123 Test Street',
    'city': 'Mumbai',
    'state': 'Maharashtra',
    'postal_code': '400001',
})
test("Checkout redirects to payment", r.status_code == 302 and '/payment' in r.url)

# ============================================
# 7. PAYMENT
# ============================================
print("\n--- DEMO PAYMENT ---")

r = c.get('/checkout/payment/')
content = r.content.decode()
test("Payment page loads", r.status_code == 200)
test("Payment has demo badge", "Demo Payment Gateway" in content)
test("Payment has Card option", "Credit / Debit Card" in content)
test("Payment has UPI option", "UPI" in content)
test("Payment has COD option", "Cash on Delivery" in content)

# Process payment with guaranteed success card
r = c.post('/checkout/payment/process/', {
    'payment_method': 'card',
    'card_number': '4111 1111 1111 1111',
})
test("Payment processes", r.status_code == 302)
test("Payment redirects to success", '/success/' in r.url)

# ============================================
# 8. ORDER VERIFICATION
# ============================================
print("\n--- ORDER VERIFICATION ---")

order = Order.objects.filter(user=user).first()
test("Order created", order is not None)
test("Order status is pending", order.status == 'pending')
test("Payment status is paid_demo", order.payment_status == 'paid_demo')
test("Order has correct name", order.full_name == 'Test User')
test("Order has correct email", order.email == 'test@example.com')
test("Order has correct city", order.city == 'Mumbai')

items = order.items.all()
test("Order has items", items.count() > 0, f"{items.count()} items")

# Check stock reduced
p1.refresh_from_db()
p2.refresh_from_db()
test("Stock reduced for product 1", p1.stock == original_stock_p1 - 2)
test("Stock reduced for product 2", p2.stock == original_stock_p2 - 1)

# Check cart cleared
r = c.get('/cart/')
test("Cart cleared after order", "Your cart is empty" in r.content.decode())

# ============================================
# 9. ORDER PAGES
# ============================================
print("\n--- ORDER PAGES ---")

# Payment success page
r = c.get(f'/checkout/payment/success/{order.id}/')
test("Payment success page loads", r.status_code == 200 and "Payment Successful" in r.content.decode())

# My Orders
r = c.get('/orders/')
content = r.content.decode()
test("My Orders page loads", r.status_code == 200)
test("My Orders shows order", str(order.id) in content)

# Order Detail
r = c.get(f'/orders/{order.id}/')
content = r.content.decode()
test("Order detail loads", r.status_code == 200)
test("Order detail has shipping info", 'Mumbai' in content)
test("Order detail has items", p1.name in content)

# Order confirmation
r = c.get(f'/orders/confirmation/{order.id}/')
test("Order confirmation loads", r.status_code == 200)

# ============================================
# 10. SECURITY: Cannot view other user's orders
# ============================================
print("\n--- SECURITY ---")

c3 = Client()
# Register another user
c3.post('/accounts/register/', {
    'username': 'otheruser',
    'email': 'other@example.com',
    'password1': 'OtherPass123!',
    'password2': 'OtherPass123!',
})
other_user = User.objects.get(username='otheruser')
otp2 = OTP.objects.get(user=other_user)
c3.post('/accounts/verify-otp/', {'otp': otp2.otp})
c3.post('/accounts/login/', {'username': 'otheruser', 'password': 'OtherPass123!'})

r = c3.get(f'/orders/{order.id}/')
test("Other user cannot view order", r.status_code == 404)

# ============================================
# 11. CHECKOUT REQUIRES LOGIN
# ============================================
print("\n--- AUTH PROTECTION ---")

c4 = Client()  # Not logged in
r = c4.get('/checkout/')
test("Checkout requires login", r.status_code == 302 and '/login' in r.url)

r = c4.get('/orders/')
test("My Orders requires login", r.status_code == 302 and '/login' in r.url)

r = c4.get('/accounts/profile/')
test("Profile requires login", r.status_code == 302 and '/login' in r.url)

# ============================================
# 12. COD PAYMENT
# ============================================
print("\n--- COD PAYMENT ---")

# Add item and checkout again
c.post(f'/cart/add/{p1.id}/', {'quantity': 1})
c.post('/checkout/', {
    'full_name': 'Test User COD',
    'email': 'test@example.com',
    'phone': '9876543210',
    'address': '456 COD Street',
    'city': 'Delhi',
    'state': 'Delhi',
    'postal_code': '110001',
})
r = c.post('/checkout/payment/process/', {'payment_method': 'cod'})
test("COD payment succeeds", r.status_code == 302 and '/success/' in r.url)

cod_order = Order.objects.filter(user=user, payment_status='cod').first()
test("COD order created", cod_order is not None)
test("COD payment status correct", cod_order.payment_status == 'cod' if cod_order else False)

# ============================================
# 13. PAYMENT FAILURE
# ============================================
print("\n--- PAYMENT FAILURE ---")

r = c.get('/checkout/payment/failed/')
test("Payment failed page loads", r.status_code == 200 and "Payment Failed" in r.content.decode())

# ============================================
# 14. LOGOUT
# ============================================
print("\n--- LOGOUT ---")

r = c.get('/accounts/logout/')
test("Logout redirects", r.status_code == 302)

r = c.get('/accounts/profile/')
test("Cannot access profile after logout", r.status_code == 302 and '/login' in r.url)

# ============================================
# 15. ADMIN
# ============================================
print("\n--- ADMIN ---")

c_admin = Client()
c_admin.login(username='admin', password='admin123')
r = c_admin.get('/admin/')
test("Admin loads", r.status_code == 200)

r = c_admin.get('/admin/products/product/')
test("Admin product list loads", r.status_code == 200)

r = c_admin.get('/admin/orders/order/')
test("Admin order list loads", r.status_code == 200)

# ============================================
# SUMMARY
# ============================================
print("\n" + "=" * 60)
passed = sum(1 for _, s, _ in results if s == "PASS")
failed = sum(1 for _, s, _ in results if s == "FAIL")
total = len(results)
print(f"  RESULTS: {passed}/{total} passed, {failed} failed")
if failed:
    print("\n  FAILED TESTS:")
    for name, s, detail in results:
        if s == "FAIL":
            print(f"    [X] {name}" + (f" ({detail})" if detail else ""))
print("=" * 60)
