# shopapp/utils.py

from .models import Product, Category, User, Cart

def delete_product_logic(product_id):
    try:
        product = Product.objects.get(id=product_id)
        if Cart.objects.filter(product=product).exists():
            return "Cannot delete product. It's in the cart."
        product.delete()
        return "Product deleted successfully!"
    except Product.DoesNotExist:
        return "Product not found."

def delete_category_logic(category_id):
    try:
        category = Category.objects.get(id=category_id)
        if Product.objects.filter(category=category).exists():
            return "Cannot delete category. It has products."
        category.delete()
        return "Category deleted successfully!"
    except Category.DoesNotExist:
        return "Category not found."

def delete_user_logic(user_id):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return "User deleted successfully!"
    except User.DoesNotExist:
        return "User not found."
