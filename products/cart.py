from decimal import Decimal
from django.conf import settings
from .models import Product


class Cart:
    """Session-based shopping cart."""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        """Add a product to the cart or update its quantity."""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'qty': 0,
                'price': str(product.price),
            }
        self.cart[product_id]['qty'] += quantity
        # Cap at available stock
        if self.cart[product_id]['qty'] > product.stock:
            self.cart[product_id]['qty'] = product.stock
        self.save()

    def remove(self, product_id):
        """Remove a product from the cart."""
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def update(self, product_id, quantity):
        """Update the quantity of a product."""
        product_id = str(product_id)
        if product_id in self.cart:
            if quantity > 0:
                self.cart[product_id]['qty'] = quantity
            else:
                del self.cart[product_id]
            self.save()

    def save(self):
        """Mark the session as modified."""
        self.session.modified = True

    def get_total(self):
        """Calculate total cart price."""
        return sum(
            Decimal(item['price']) * item['qty']
            for item in self.cart.values()
        )

    def clear(self):
        """Remove cart from session."""
        del self.session['cart']
        self.save()

    def __iter__(self):
        """Iterate over items, attaching Product objects."""
        product_ids = list(self.cart.keys())
        products = Product.objects.filter(id__in=product_ids)
        product_map = {str(p.id): p for p in products}

        for product_id, item in self.cart.copy().items():
            if product_id in product_map:
                item['product'] = product_map[product_id]
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['qty']
                yield item
            else:
                pass

    def __len__(self):
        """Return the total number of items in the cart."""
        return sum(item['qty'] for item in self.cart.values())
