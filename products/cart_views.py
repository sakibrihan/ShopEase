from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Product
from .cart import Cart


def cart_detail(request):
    """Display the shopping cart."""
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})


@require_POST
def cart_add(request, product_id):
    """Add a product to the cart."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    if quantity < 1:
        quantity = 1

    if not product.in_stock:
        messages.error(request, f'"{product.name}" is out of stock.')
        return redirect('products:product_detail', product_id=product.id)

    if quantity > product.stock:
        messages.warning(request, f'Only {product.stock} units available. Added {product.stock} to cart.')
        quantity = product.stock

    cart.add(product, quantity)
    messages.success(request, f'"{product.name}" added to cart.')
    return redirect('cart:cart_detail')


@require_POST
def cart_update(request, product_id):
    """Update the quantity of a cart item."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    if quantity > product.stock:
        messages.warning(request, f'Only {product.stock} units of "{product.name}" available.')
        quantity = product.stock

    if quantity < 1:
        cart.remove(product_id)
        messages.info(request, f'"{product.name}" removed from cart.')
    else:
        cart.update(product_id, quantity)
        messages.success(request, f'Cart updated.')

    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    """Remove an item from the cart."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product_id)
    messages.info(request, f'"{product.name}" removed from cart.')
    return redirect('cart:cart_detail')
