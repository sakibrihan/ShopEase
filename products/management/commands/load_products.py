from django.core.management.base import BaseCommand
from products.models import Product


SAMPLE_PRODUCTS = [
    {
        'name': 'Wireless Headphones',
        'description': 'Premium wireless Bluetooth headphones with active noise cancellation, '
                       '30-hour battery life, and comfortable over-ear design. Perfect for music lovers and remote workers.',
        'price': 2499.00,
        'category': 'electronics',
        'stock': 25,
    },
    {
        'name': 'Smart Watch Pro',
        'description': 'Feature-packed smartwatch with heart rate monitoring, GPS tracking, '
                       'sleep analysis, and water resistance up to 50 meters. Compatible with Android and iOS.',
        'price': 4999.00,
        'category': 'electronics',
        'stock': 15,
    },
    {
        'name': 'Bluetooth Speaker',
        'description': 'Portable Bluetooth speaker with rich bass, 360-degree surround sound, '
                       'and 12-hour playtime. Waterproof IPX7 rating for outdoor adventures.',
        'price': 1799.00,
        'category': 'electronics',
        'stock': 30,
    },
    {
        'name': 'Laptop Backpack',
        'description': 'Durable laptop backpack with padded compartment for up to 15.6" laptops, '
                       'USB charging port, anti-theft design, and multiple organized pockets.',
        'price': 1299.00,
        'category': 'accessories',
        'stock': 40,
    },
    {
        'name': 'Wireless Mouse',
        'description': 'Ergonomic wireless mouse with adjustable DPI (800-1600), silent clicks, '
                       'and long battery life. Works with USB nano receiver on any surface.',
        'price': 599.00,
        'category': 'accessories',
        'stock': 50,
    },
    {
        'name': 'Casual T-Shirt',
        'description': 'Premium cotton crew-neck T-shirt with a relaxed fit. '
                       'Soft, breathable fabric perfect for everyday wear. Available in multiple sizes.',
        'price': 499.00,
        'category': 'clothing',
        'stock': 100,
    },
    {
        'name': 'Classic Hoodie',
        'description': 'Warm and comfortable pullover hoodie made from cotton-polyester blend. '
                       'Features a kangaroo pocket, adjustable drawstring hood, and ribbed cuffs.',
        'price': 1199.00,
        'category': 'clothing',
        'stock': 35,
    },
    {
        'name': 'Modern Table Lamp',
        'description': 'Minimalist LED table lamp with touch dimmer and 3 color temperature modes. '
                       'Sleek metal body with a weighted base. Perfect for desk or bedside.',
        'price': 899.00,
        'category': 'home',
        'stock': 20,
    },
    {
        'name': 'Insulated Water Bottle',
        'description': 'Double-walled vacuum insulated stainless steel water bottle. '
                       'Keeps drinks cold for 24 hours or hot for 12 hours. 750ml capacity, leak-proof lid.',
        'price': 399.00,
        'category': 'home',
        'stock': 60,
    },
    {
        'name': 'Python Programming Book',
        'description': 'Comprehensive guide to Python programming for beginners and intermediate developers. '
                       'Covers fundamentals, web development, data analysis, and best practices with hands-on projects.',
        'price': 649.00,
        'category': 'books',
        'stock': 45,
    },
]


class Command(BaseCommand):
    help = 'Load sample products into the database'

    def handle(self, *args, **options):
        count = 0
        for product_data in SAMPLE_PRODUCTS:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data,
            )
            if created:
                count += 1
                self.stdout.write(f'  Created: {product.name}')
            else:
                self.stdout.write(f'  Already exists: {product.name}')

        self.stdout.write(self.style.SUCCESS(f'\nDone! {count} new products created.'))
