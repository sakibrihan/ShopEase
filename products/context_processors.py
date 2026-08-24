from .cart import Cart


def cart_count(request):
    """Make cart item count available to all templates via context."""
    cart = Cart(request)
    return {'cart_item_count': len(cart)}
