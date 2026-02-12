from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Category, Product, Order, OrderItem, Profile, Favorite

# ---------------- HOME ----------------
def home(request):
    products = Product.objects.all()
    return render(request, 'bag/home.html', {'products': products})

# ---------------- CATEGORY PAGES ----------------
def milk_page(request):
    category = get_object_or_404(Category, name__iexact="Milk")
    products = Product.objects.filter(category=category)
    return render(request, 'bag/category.html', {'category': 'Milk', 'products': products})

def fruits_page(request):
    category = get_object_or_404(Category, name__iexact="Fruits")
    products = Product.objects.filter(category=category)

    return render(request, 'bag/category.html', {
        'category': 'Fruits',
        'products': products,
        'favorite_ids': get_favorite_ids(request)
    })

def vegetables_page(request):
    category = get_object_or_404(Category, name__iexact="Vegetables")
    products = Product.objects.filter(category=category)
    return render(request, 'bag/category.html', {'category': 'Vegetables', 'products': products})

# ---------------- PRODUCT DETAIL ----------------
def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'bag/product_detail.html', {'product': product})

# ---------------- CART (SESSION BASED) ----------------
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    # ✅ GET quantity from URL (from product detail page)
    qty = int(request.GET.get('qty', 1))

    # ✅ ADD selected quantity
    cart[product_id] = cart.get(product_id, 0) + qty

    request.session['cart'] = cart
    return redirect('view_cart')



def update_cart_quantity(request, product_id, action):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    if product_id in cart:
        if action == 'increment':
            cart[product_id] += 1
        elif action == 'decrement':
            if cart[product_id] > 1:
                cart[product_id] -= 1
            else:
                del cart[product_id]
        request.session['cart'] = cart
    return redirect('view_cart')

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
    return redirect('view_cart')

def view_cart(request):
    cart = request.session.get('cart', {})
    products = []
    total = 0
    for product_id, qty in cart.items():
        product = Product.objects.get(id=product_id)
        product.qty = qty
        product.subtotal = qty * product.price
        total += product.subtotal
        products.append(product)
    return render(request, 'bag/cart.html', {'products': products, 'total': total})

# ---------------- CHECKOUT ----------------
@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('home')

    products = []
    total = 0
    for product_id, qty in cart.items():
        product = Product.objects.get(id=product_id)
        products.append((product, qty))
        total += product.price * qty

    if request.method == 'POST':
        full_name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method')

        # Create Order
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address=address,
            payment_method=payment_method,
            total_amount=total,
            status="Placed"
        )

        # Create Order Items
        for product, qty in products:
            OrderItem.objects.create(
                order=order,
                product=product,
                price=product.price,
                quantity=qty
            )

        request.session['cart'] = {}

        if payment_method == 'COD':
            return redirect('order_success')
        else:
            return redirect('payment', order_id=order.id)

    return render(request, 'bag/checkout.html', {'total': total})

# ---------------- PAYMENT ----------------
@login_required
def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.payment_status = 'PAID'  # Simulated payment success
        order.save()
        return redirect('order_success')
    return render(request, 'bag/payment.html', {'order': order})

# ---------------- ORDER SUCCESS ----------------
@login_required
def order_success(request):
    return render(request, 'bag/order_success.html')

# ---------------- REGISTER ----------------

def register_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        if password != confirm_password:
            error = "Passwords do not match"

        elif User.objects.filter(username=username).exists():
            error = "Username already exists"

        else:
            # 1️⃣ Create User
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # 2️⃣ Create Profile WITH DATA
            Profile.objects.create(
                user=user,
                full_name=full_name,
                phone=phone,
                address=address
            )

            login(request, user)
            return redirect('profile')   # or home

    return render(request, 'bag/register.html', {'error': error})


# ---------------- LOGIN ----------------
def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
            else:
                error = "Invalid username or password."
        else:
            error = "Please enter both username and password."
    return render(request, 'bag/login.html', {'error': error})

# ---------------- LOGOUT ----------------
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# ---------------- SEARCH ----------------
def search(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(category__name__icontains=query)
    )
    return render(request, 'bag/search_results.html', {'products': products, 'query': query})

# ---------------- PROFILE & FAVORITES ----------------
@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    favorites = Product.objects.filter(
        favorited_by__user=request.user
    )

    return render(request, 'bag/profile.html', {
        'profile': profile,
        'orders': orders,
        'favorites': favorites
    })

def get_favorite_ids(request):
    if request.user.is_authenticated:
        return Favorite.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)
    return []

@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        favorite.delete()
        status = 'removed'
    else:
        status = 'added'
    return JsonResponse({'status': status})

def product_list(request):
    products = Product.objects.all()
    favorite_ids = get_favorite_ids(request)

    return render(request, 'products.html', {
        'products': products,
        'favorite_ids': favorite_ids
    })

@login_required
def place_order(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('home')  # No items in cart

    # Calculate total
    total = 0
    products = []
    for product_id, qty in cart.items():
        product = Product.objects.get(id=product_id)
        subtotal = product.price * qty
        total += subtotal
        products.append((product, qty))

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method')

        # Create order
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address=address,
            payment_method=payment_method,
            total_amount=total,
            status="Placed"
        )

        # Create order items
        for product, qty in products:
            OrderItem.objects.create(
                order=order,
                product=product,
                price=product.price,
                quantity=qty
            )

        # Clear cart
        request.session['cart'] = {}

        # Redirect depending on payment method
        if payment_method == 'COD':
            return redirect('order_success')
        else:
            return redirect('payment', order_id=order.id)

    return render(request, 'bag/place_order.html', {
        'products': products,
        'total': total
    })
