from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'in_stock', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['price', 'stock']
    list_per_page = 20

    def in_stock(self, obj):
        return obj.stock > 0
    in_stock.boolean = True
    in_stock.short_description = 'In Stock'
