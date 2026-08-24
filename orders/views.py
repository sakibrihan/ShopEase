import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from products.cart import Cart
from .models import Order, OrderItem
from .forms import ShippingForm


@login_required
def checkout(request):
    """Checkout page — collect shipping info and show order summary."""
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty. Add some products first!')
        return redirect('products:product_list')

    if request.method == 'POST':
        form = ShippingForm(request.POST)
        if form.is_valid():
            # Store shipping info in session
            request.session['shipping'] = form.cleaned_data
            return redirect('orders:payment')
    else:
        # Pre-fill form with user info
        initial = {
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        }
        form = ShippingForm(initial=initial)

    return render(request, 'checkout/checkout.html', {
        'form': form,
        'cart': cart,
    })


@login_required
def payment(request):
    """Demo payment gateway page."""
    cart = Cart(request)
    shipping = request.session.get('shipping')

    if len(cart) == 0 or not shipping:
        messages.warning(request, 'Please complete checkout first.')
        return redirect('orders:checkout')

    return render(request, 'checkout/payment.html', {
        'cart': cart,
        'shipping': shipping,
    })


@login_required
def payment_process(request):
    """Process the demo payment."""
    if request.method != 'POST':
        return redirect('orders:payment')

    cart = Cart(request)
    shipping = request.session.get('shipping')

    if len(cart) == 0 or not shipping:
        messages.warning(request, 'Please complete checkout first.')
        return redirect('orders:checkout')

    payment_method = request.POST.get('payment_method', 'card')

    # Simulate payment result
    if payment_method == 'cod':
        # COD always succeeds
        payment_success = True
        payment_status = 'cod'
    else:
        # For card/UPI — simulate
        card_number = request.POST.get('card_number', '').replace(' ', '')
        if card_number == '4111111111111111':
            payment_success = True
        else:
            # 80% success, 20% failure for demo
            payment_success = random.random() < 0.8
        payment_status = 'paid_demo'

    if payment_success:
        # Create Order
        from products.models import Product

        order = Order.objects.create(
            user=request.user,
            full_name=shipping['full_name'],
            email=shipping['email'],
            phone=shipping['phone'],
            address=shipping['address'],
            city=shipping['city'],
            state=shipping['state'],
            postal_code=shipping['postal_code'],
            total_amount=cart.get_total(),
            status='pending',
            payment_status=payment_status,
        )

        # Create Order Items and reduce stock
        for item in cart:
            product = item['product']
            qty = item['qty']

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                price=item['price'],
            )

            # Reduce stock
            product.stock -= qty
            product.save()

        # Clear cart and shipping session
        cart.clear()
        if 'shipping' in request.session:
            del request.session['shipping']

        return redirect('orders:payment_success', order_id=order.id)
    else:
        return redirect('orders:payment_failed')


@login_required
def payment_success(request, order_id):
    """Payment success / order confirmation page."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'checkout/payment_success.html', {'order': order})


@login_required
def payment_failed(request):
    """Payment failure page."""
    return render(request, 'checkout/payment_failed.html')


@login_required
def order_confirmation(request, order_id):
    """Order confirmation page."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_confirmation.html', {'order': order})


@login_required
def my_orders(request):
    """List the logged-in user's orders."""
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """View details of a specific order — only own orders."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})
