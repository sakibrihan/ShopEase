from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product, CATEGORY_CHOICES


def home(request):
    """Homepage with featured products and categories."""
    featured_products = Product.objects.filter(stock__gt=0)[:6]
    categories = CATEGORY_CHOICES
    return render(request, 'home.html', {
        'featured_products': featured_products,
        'categories': categories,
    })


def product_list(request):
    """Product listing with search and category filter."""
    products = Product.objects.all()
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    sort = request.GET.get('sort', '')

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    if category:
        products = products.filter(category=category)

    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')

    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'products/product_list.html', {
        'products': page_obj,
        'page_obj': page_obj,
        'categories': CATEGORY_CHOICES,
        'current_query': query,
        'current_category': category,
        'current_sort': sort,
    })


def product_detail(request, product_id):
    """Single product detail page."""
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'products/product_detail.html', {
        'product': product,
    })
