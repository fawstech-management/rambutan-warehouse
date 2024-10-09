from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import FarmerDetailsForm,FarmerDetails,RambutanPostForm,RegisterUserForm, WishlistForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import  BillingDetail, Cart, CustomerDetails, FarmerDetails, Order, OrderItem, RambutanPost,Registeruser, Wishlist
from django.contrib import messages
from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth.hashers import make_password
from .forms import RegisterUserForm
from .forms import FarmerDetailsForm, TreeVarietyForm, RambutanPostForm
from django.contrib import messages
from django.db.models import F

def index(request):
    if request.method =='POST':
        pass
    return render(request,'index.html')

def about(request):
    return render(request,'about.html')

def contact(request):
    return render(request,'contact.html')
'''
def register(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if Registeruser.objects.filter(email=email).exists():
                messages.info(request, "Email is already registered. Please log in.")
                return redirect('login')  
            form.save()

            #messages.success(request, "Registration successful! You can now log in.")
            return redirect('login') 
        else:
            messages.error(request, form.errors)
    else:
        form = RegisterUserForm()

    return render(request, 'register.html', {'form': form})
'''
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        print(username,password)
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
          
            login(request, user)

            request.session['user_id'] = user.id
            request.session['name'] = user.username
            request.session['role'] = user.role
            if user.is_superuser:  # or user.role == 'admin' if you're using a custom role system
                return redirect('/admin') 
            elif user.role == 'farmer':
                return redirect('farmer_dashboard')
            elif user.role == 'customer':
                return redirect('customer_dashboard')
            else:
                return render(request, 'login.html', {'error': 'Invalid user role'})
        #else:
            #messages.error(request,message="Invalid Credentials")
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login') 

@login_required
def farmer_dashboard(request):
    try:
        user = Registeruser.objects.get(username=request.user.username,role='farmer')
    except Registeruser.DoesNotExist:
        return render(request, '404.html')  
    return render(request, 'farmer_dashboard.html', {'farmer': user})
def farmer_details(request):
    try:
        farmer_details = FarmerDetails.objects.get(user=request.user)
    except FarmerDetails.DoesNotExist:
        farmer_details = None

    if request.method == 'POST':
        # Extract the form data manually from request.POST
        address = request.POST.get('address')
        mobile_number = request.POST.get('mobile_number')
        aadhar_number = request.POST.get('aadhar_number')
        account_number = request.POST.get('account_number')
        ifsc_code = request.POST.get('ifsc_code')
        bank_name = request.POST.get('bank_name')
        location = request.POST.get('location')
        

        # Save or update the FarmerDetails instance
        if farmer_details:
            farmer_details.address = address
            farmer_details.mobile_number = mobile_number
            farmer_details.aadhar_number = aadhar_number
            farmer_details.account_number = account_number
            farmer_details.ifsc_code = ifsc_code
            farmer_details.bank_name = bank_name
            farmer_details.location = location
        
            farmer_details.save()
        else:
            farmer_details = FarmerDetails.objects.create(
                user=request.user,
                address=address,
                mobile_number=mobile_number,
                aadhar_number=aadhar_number,
                account_number=account_number,
                ifsc_code=ifsc_code,
                bank_name=bank_name,
                location=location,
               
            )

        
        # Redirect to the dashboard after saving
        return redirect('farmer_dashboard')

    # Render the form in the HTML template
    return render(request, 'farmer_details.html', {
        'farmer_details': farmer_details
    })




def post_rambutan(request):
    try:
        farmer_details = request.user.farmerdetails 
        print(farmer_details)
    except FarmerDetails.DoesNotExist:
        return redirect('farmer_details') 

    if request.method == 'POST':
        print(request.POST)
        form = RambutanPostForm(request.POST,request.FILES)
        if form.is_valid():
            rambutan_post = form.save(commit=False)
            rambutan_post.farmer = farmer_details  
            rambutan_post.quantity_left = rambutan_post.quantity  
            rambutan_post.save()
            return redirect('view_posts')  
        #else:
            #messages.error(request,message=form.errors)
    else:
        form = RambutanPostForm()

    return render(request, 'post_rambutan.html', {'form': form})

def create_tree_variety(request):
    if request.method == 'POST':
        form = TreeVarietyForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('sucess')
        else:
            messages.error(request,message=form.errors)    
    else:
        form = TreeVarietyForm()
    return render(request, 'forms.html', {'form': form})


@login_required
def view_posts(request):
    user = request.user  

    try:
        farmer_details = user.farmerdetails  # Assuming you have FarmerDetails linked to the user

        # Filter available and unavailable posts separately
        available_posts = RambutanPost.objects.filter(farmer=farmer_details, is_available=True)
        unavailable_posts = RambutanPost.objects.filter(farmer=farmer_details, is_available=False)

    except FarmerDetails.DoesNotExist:
        return redirect('farmer_details')  # Redirect if farmer details don't exist

    context = {
        'available_posts': available_posts,
        'unavailable_posts': unavailable_posts,
        'user': user  
    }

    return render(request, 'view_posts.html', context)

def redirect_post_rambutan(request):
    return redirect('post_rambutan') 

def update_post(request, id):
    post = get_object_or_404(RambutanPost, id=id)

    if request.method == 'POST':
        form = RambutanPostForm(request.POST, request.FILES, instance=post)
        
        if form.is_valid():
            # Save the updated post
            updated_post = form.save(commit=False)

            # Set the post to available upon updating
            updated_post.is_available = True
            updated_post.save()

            return redirect('view_posts')
        else:
            return render(request, 'update_post.html', {'form': form, 'post': post})
    
    else:
        form = RambutanPostForm(instance=post)
        return render(request, 'update_post.html', {'form': form, 'post': post})

@login_required
def delete_post_confirmation(request, id):
    post = get_object_or_404(RambutanPost, id=id)

    # Check if the post is in a wishlist, cart, or part of an order
    in_cart = Cart.objects.filter(rambutan_post=post).exists()
    in_wishlist = Wishlist.objects.filter(rambutan_post=post).exists()
    in_order = OrderItem.objects.filter(rambutan_post=post).exists()

    if request.method == 'POST':
        # If the post is in any order, show a warning and prevent deletion
        if in_order:
           # messages.warning(request, 'This post cannot be deleted because it has associated orders.')
            return redirect('view_posts')

        # If in a cart or wishlist, mark the post as unavailable (without deleting the cart/wishlist items)
        if in_cart or in_wishlist:
            post.is_available = False  # Mark as unavailable
            post.save()
            #messages.success(request, 'Post marked as unavailable because it is in a cart or wishlist.')
        else:
            post.delete()  # Delete only if not in cart or wishlist
           # messages.success(request, 'Post deleted successfully.')
        
        return redirect('view_posts')

    return render(request, 'delete_post_confirmation.html', {
        'post': post,
        'in_cart': in_cart,
        'in_wishlist': in_wishlist,
        'in_order': in_order,
    })


@login_required
def delete_post(request, id):
    return redirect('delete_post_confirmation', id=id)

@login_required
def customer_dashboard(request):
    return render(request, 'customer_dashboard.html', {'cart': cart})

@login_required
def edit_profile(request):
    return render(request, 'edit_profile.html')

@login_required
def product_single(request):
    return render(request, 'product-single.html')

@login_required
def cart(request):
    return render(request, 'cart.html')

@login_required
def checkout(request):
    return render(request, 'checkout.html')

@login_required
def blog(request):
    return render(request, 'blog.html')

@login_required
def profile_view(request):
   
    return render(request, 'customer_profile.html')
    

@login_required
def products_browse(request):
    products = RambutanPost.objects.all().values('id', 'name', 'variety', 'image', 'price_per_kg', 'created_at', 'description', 'is_available')

    # Retrieve items in cart and wishlist
    cart_items = Cart.objects.filter(user=request.user).values_list('rambutan_post_id', flat=True)
    wishlist_items = Wishlist.objects.filter(user=request.user).values_list('rambutan_post_id', flat=True)

    # Flag products that are in the cart or wishlist but are unavailable
    for product in products:
        #if product['id'] in cart_items or product['id'] in wishlist_items:
            if not product['is_available']:
                product['status_message'] = 'Unavailable'

    context = {
        'products': products,
    }
    return render(request, 'shop.html', context)

@login_required
def wishlist(request):
    
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('rambutan_post')

    wishlists = RambutanPost.objects.filter(id__in=[item.rambutan_post_id for item in wishlist_items])

    return render(request, 'wishlist.html', {'wishlist_items': wishlists})
@login_required
def add_to_wishlist(request, id):
    post = get_object_or_404(RambutanPost, id=id)

    # Check if the product is unavailable but already in the wishlist
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        rambutan_post=post
    )

    if not post.is_available and created:
        # If the product is unavailable and is being added to the wishlist for the first time
        messages.warning(request, f"{post.name} is currently unavailable, but it has been added to your wishlist.")

    return redirect('wishlist')


@login_required
def remove_from_wishlist(request, id):
    post = get_object_or_404(RambutanPost, id=id)
    wishlist_item = Wishlist.objects.filter(user=request.user, rambutan_post=post).first()

    if wishlist_item:
        wishlist_item.delete()
        #messages.success(request, 'Product removed from wishlist.')
    #else:
        #messages.info(request, 'Product is not in your wishlist.')

    return redirect('wishlist')
@login_required
def add_to_cart(request, rambutan_post_id):
    rambutan_post = get_object_or_404(RambutanPost, id=rambutan_post_id)

    if not rambutan_post.is_available:
        # If the product is unavailable, inform the user but still display it in the cart
        messages.warning(request, f"{rambutan_post.name} is currently unavailable. You can keep it in your cart but cannot purchase it.")
    else:
        # Proceed to add the product to the cart if it's available
        cart_item, created = Cart.objects.get_or_create(
            user=request.user, 
            rambutan_post=rambutan_post,
            defaults={'price': rambutan_post.price_per_kg} 
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()
    
    return redirect('cart')

@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    for item in cart_items:
        item.total_price = item.price * item.quantity
    total_price = sum(item.total_price for item in cart_items) 
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    
    return render(request, 'cart.html', context)

@login_required
def remove_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    cart_item.delete()
    
    return redirect('cart')

@login_required
def update_cart_item_quantity(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    
    if request.method == 'POST':
        new_quantity = int(request.POST.get('quantity', 1))
        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()

    return redirect('cart')
    
@login_required
def billing_view(request):
    # Check if cart items exceed available quantity
    cart_items = Cart.objects.filter(user=request.user)
    for cart_item in cart_items:
        rambutan_post = cart_item.rambutan_post
        
        # Compare the quantity in the cart with the available quantity in the post
        if cart_item.quantity > rambutan_post.quantity_left:
            #messages.error(request, f"Sorry, the quantity of '{rambutan_post.name}' in your cart exceeds the available stock.")
            return redirect('cart')  # Redirect to cart to let user adjust quantities

    # Proceed with the billing form if quantities are valid
    if request.method == 'POST':
        first_name = request.POST['first-name']
        last_name = request.POST['last-name']
        country = request.POST['country']
        street_address = request.POST['street-address']
        city = request.POST['city']
        postcode = request.POST['postcode']
        phone = request.POST['phone']
        email = request.POST['email']

        # Create the billing details
        BillingDetail.objects.create(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            country=country,
            street_address=street_address,
            city=city,
            postcode=postcode,
            phone=phone,
            email=email
        )
        
        return redirect('place_order')

    return render(request, 'checkout.html')
@login_required
def place_order(request):
    # Retrieve the latest billing details for the user
    billing_details = BillingDetail.objects.filter(user=request.user).last()

    # Check if billing details are filled
    if not billing_details:
        # Redirect to billing view if details are not filled
        return redirect('billing_view')

    # Retrieve the cart items for the user
    cart_items = Cart.objects.filter(user=request.user)

    # Ensure the cart is not empty
    if not cart_items.exists():
        return redirect('cart')

    # Check if all items in the cart are available
    unavailable_items = cart_items.filter(rambutan_post__is_available=False)
    if unavailable_items.exists():
        # Redirect to cart if any items are unavailable
        # messages.error(request, "Some items in your cart are no longer available.")
        return redirect('cart')

    # Calculate the total cost
    subtotal = sum(item.total_price for item in cart_items)
    delivery_fee = 0
    discount = 0
    total = subtotal + delivery_fee - discount

    if request.method == 'POST':
        payment_method = request.POST.get('payment-method')

        # Create the Order
        order = Order.objects.create(
            billing_detail=billing_details,
            user=request.user,
            total_amount=total,
            payment_method=payment_method
        )

        # Process each cart item and adjust the RambutanPost quantities
        for item in cart_items:
            rambutan_post = item.rambutan_post
            ordered_quantity = item.quantity

            # Ensure that there is enough quantity left in the RambutanPost
            if rambutan_post.quantity_left < ordered_quantity:
                # Redirect to cart if insufficient quantity is available
                # messages.error(request, f"Insufficient quantity for {rambutan_post.name}.")
                return redirect('cart')

            # Update the quantity_left for the RambutanPost
            rambutan_post.quantity_left -= ordered_quantity

            # If quantity_left is 0 or less, mark the post as unavailable
            if rambutan_post.quantity_left <= 0:
                rambutan_post.is_available = False

            rambutan_post.save()

            # Create the OrderItem
            OrderItem.objects.create(
                order=order,
                rambutan_post=rambutan_post,
                quantity=ordered_quantity,
                price=item.price
            )

        # Clear the user's cart after the order is placed
        cart_items.delete()

        return redirect('order_detail', order_number=order.order_number)

    return render(request, 'place_order.html', {
        'billing_details': billing_details,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'discount': discount,
        'total': total,
    })



@login_required
def order_detail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
        
        order_items = OrderItem.objects.filter(order=order)  
        
        billing_details = order.billing_detail
        subtotal = sum(item.price * item.quantity for item in order_items)
        delivery_fee = 0 
        discount = 0     
        total = subtotal + delivery_fee - discount

    except Order.DoesNotExist:
        return redirect('order')

    return render(request, 'order.html', {
        'order': order,
        'order_items': order_items,
        'billing_details': billing_details,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'discount': discount,
        'total': total,
    })

@login_required
def order_history(request):
    # Fetching the user's orders and prefetching related items
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
   # order_Item = OrderItem.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'order_history.html', {
        'orders': orders
    })


import random
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterUserForm
from .models import Registeruser  # Ensure this is your user model

# OTP storage (in production, consider storing this securely)
otp_storage = {}

# Function to send the OTP email
def send_otp_email(user_email):
    otp = random.randint(1000, 9999)  # Generate a random 4-digit OTP
    otp_storage[user_email] = otp  # Store OTP temporarily (in memory for now)

    subject = 'Your OTP for Email Verification'
    message = f'Your OTP is {otp}. Please use this to verify your email.'
    from_email = 'your_email@gmail.com'  # Replace with your email
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)

# Main register view with OTP logic
def register(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')

            # Check if the email is already registered
            if Registeruser.objects.filter(email=email).exists():
                messages.info(request, "Email is already registered. Please log in.")
                return redirect('login')

            # Save the user but deactivate the account until OTP is verified
            user = form.save(commit=False)
            user.is_active = False  # Deactivate the account initially
            user.save()

            # Send OTP to the user's email
            send_otp_email(user.email)

            # Store the user's email in session for OTP verification
            request.session['user_email'] = user.email

            # Redirect to the OTP verification page
            return redirect('verify_otp')
        else:
            messages.error(request, form.errors)
    else:
        form = RegisterUserForm()

    return render(request, 'register.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages

# Assuming you're using a custom user model
User = get_user_model()

def verify_otp(request):
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        email = request.session.get('user_email')  # Get email from session

        if not email:
            messages.error(request, "Session expired. Please register again.")
            return redirect('register')

        # Verify OTP
        if otp_storage.get(email) and otp_storage[email] == int(otp_input):
            try:
                user = User.objects.get(email=email)
                user.is_active = True  # Activate the user
                user.save()

                # Remove the OTP from storage once it's verified
                del otp_storage[email]
                del request.session['user_email']  # Clear email from session

                messages.success(request, "Your account has been successfully verified! You can now log in.")
                return redirect('login')

            except User.DoesNotExist:
                messages.error(request, "User with this email does not exist.")
                return redirect('register')

        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, 'verify_otp.html')

    # If the request is GET, just display the OTP form
    return render(request, 'verify_otp.html')
