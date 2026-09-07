from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from .models import Product, Category, Cart, CartProduct
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from shopapp.utils import delete_product_logic, delete_category_logic, delete_user_logic  # Import utility functions
import re
# Admin check function
def is_admin(user):
    return user.is_superuser


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    if request.method == 'POST':
        # Add product logic
        if 'add_product' in request.POST:
            name = request.POST.get('name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            image = request.FILES.get('image')
            category_id = request.POST.get('category')
            category = Category.objects.get(id=category_id)
            Product.objects.create(name=name, description=description, price=price, image=image, category=category)
            messages.success(request, "Product added successfully!")

        # Add category logic
        elif 'add_category' in request.POST:
            category_name = request.POST.get('category_name')
            Category.objects.create(name=category_name)
            messages.success(request, "Category added successfully!")

        # Delete product logic
        elif 'delete_product' in request.POST:
            product_id = request.POST.get('delete_product')
            message = delete_product_logic(int(product_id))
            if "successfully" in message:
                messages.success(request, message)
            else:
                messages.error(request, message)

        # Delete category logic
        elif 'delete_category' in request.POST:
            category_id = request.POST.get('delete_category')
            message = delete_category_logic(int(category_id))
            if "successfully" in message:
                messages.success(request, message)
            else:
                messages.error(request, message)

        # Delete user logic
        elif 'delete_user' in request.POST:
            user_id = request.POST.get('delete_user')
            message = delete_user_logic(int(user_id))
            if "successfully" in message:
                messages.success(request, message)
            else:
                messages.error(request, message)

    # Query all products, categories, and users (excluding admin)
    products = Product.objects.all()
    categories = Category.objects.all()
    users = User.objects.exclude(is_superuser=True)  # Excluding the admin users

    return render(request, 'admin_dashboard.html', {'products': products, 'categories': categories, 'users': users})

@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        messages.success(request, 'User deleted successfully.')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin)
def delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.delete()
        messages.success(request, 'Product deleted successfully.')
    except Product.DoesNotExist:
        messages.error(request, 'Product not found.')
    return redirect('admin_dashboard')

# Home Page
def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'home.html', {'products': products, 'categories': categories})

# Login View
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            if user.is_staff:
                return redirect("/admin_dashboard/")
            else:
                return redirect("/user_home/")
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "login.html")

# User Signup

def user_signup(request):
    if request.method == 'POST':
        username = request.POST.get('uname')
        email = request.POST.get('email')
        password = request.POST.get('pwd')
        password_confirm = request.POST.get('password_confirm')

        # Validate username length
        if len(username) > 6:
            messages.error(request, "Username should not exceed 6 characters.")
            return render(request, 'signup.html', {'username': username}, status=400)

        # Validate username for special characters
        if not re.match("^[a-zA-Z0-9]*$", username):
            messages.error(request, "Username should not contain special characters.")
            return render(request, 'signup.html', {'username': username}, status=400)

        # Validate password match
        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html', {'username': username}, status=400)

        # Check for existing username
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'signup.html', {'username': username}, status=400)

        # Check for existing email
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'signup.html', {'username': username, 'email': email}, status=400)

        # Validate password strength
        password_pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$'
        if not re.match(password_pattern, password):
            messages.error(request, "Password must be at least 6 characters long, contain a letter, a number, and a special character.")
            return render(request, 'signup.html', {'username': username}, status=400)

        # Create user
        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')

    return render(request, 'signup.html')


# Logout
def user_logout(request):
    auth_logout(request)
    return redirect('/')

# Search Function
def search(request):
    query = request.GET.get('query')
    if not query:
        messages.error(request, "Please enter a search term.")
        return render(request, 'search.html')
    products = Product.objects.filter(name__icontains=query)
    return render(request, 'search_results.html', {'products': products})

# User Home (Dashboard)
@login_required
def user_home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'user_home.html', {'products': products, 'categories': categories})

# Cart View
@login_required
def cart(request):
    try:
        # Get the user's cart
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        # Handle case where the user has no cart
        cart = None

    cart_items = CartProduct.objects.filter(cart=cart)
    
    total_price = 0  # Initialize total price
    if cart_items:
        total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)  # Get the product to be added to the cart
    existing_item = Cart.objects.filter(user=request.user, product=product).first()

    if existing_item:  # If the item already exists in the cart, increase the quantity
        existing_item.quantity += 1
        existing_item.save()
        messages.success(request, f"Updated {product.name} quantity in your cart.")
    else:  # If the item does not exist, create a new cart item
        Cart.objects.create(user=request.user, product=product, quantity=1)
        messages.success(request, f"Added {product.name} to your cart.")

    return redirect('cart')

@login_required
def remove_from_cart(request, product_id):
    product = Product.objects.get(id=product_id)  # Get the product to be removed
    cart_item = Cart.objects.filter(user=request.user, product=product).first()

    if cart_item:
        cart_item.delete()  # Delete the cart item
        messages.success(request, f"Removed {product.name} from your cart.")
    else:
        messages.error(request, f"{product.name} was not found in your cart.")

    return redirect('cart')

@login_required
def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        product = Product.objects.get(id=product_id)
        cart_item = Cart.objects.filter(user=request.user, product=product).first()

        if cart_item:
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, f"Updated {product.name} quantity to {quantity}.")
            else:
                cart_item.delete()  # Remove the product if quantity is 0
                messages.success(request, f"Removed {product.name} from your cart.")
        else:
            messages.error(request, f"{product.name} is not in your cart.")

    return redirect('cart')

# Categories View
def category_view(request):
    categories = Category.objects.all()
    return render(request, 'categories.html', {'categories': categories})

# Contact Page
def contact(request):
    return render(request, 'contact.html')
