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
            if user.role == 'farmer':
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
        
        form = FarmerDetailsForm(request.POST, request.FILES, instance=farmer_details)
        if form.is_valid():
            farmer_profile = form.save()
            farmer_profile.user = request.user  
            farmer_profile.save()
            messages.success(request, "Your profile has been updated successfully." if farmer_details else "Profile created successfully.")
            return redirect('farmer_dashboard') 
        else:
            messages.error(request,message=form.errors) 
    else:
        form = FarmerDetailsForm(instance=farmer_details)

    return render(request, 'farmer_details.html', {
        'form': form
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
            rambutan_post.save()
            return redirect('view_posts')  
        else:
            messages.error(request,message=form.errors)
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
        farmer_details = user.farmerdetails  

        posts = RambutanPost.objects.filter(farmer=farmer_details)

    except FarmerDetails.DoesNotExist:
        return redirect('farmer_details')  

    context = {
        'posts': posts,
        'user': user  
    }

    print(context)

    return render(request, 'view_posts.html', context)

def redirect_post_rambutan(request):
    return redirect('post_rambutan') 

@login_required
def update_post(request, id):
    post = get_object_or_404(RambutanPost, id=id)

    if request.method == 'POST':
        form = RambutanPostForm(request.POST, request.FILES, instance=post)
        
        if form.is_valid():
            form.save() 
            return redirect('view_posts')
        else:
            return render(request, 'update_post.html', {'form': form, 'post': post})
    
    else:
        form = RambutanPostForm(instance=post)
        return render(request, 'update_post.html', {'form': form, 'post': post})
'''
@login_required
def delete_post_confirmation(request, id):
    post = get_object_or_404(RambutanPost, id=id)
    associated_order_items = OrderItem.objects.filter(cart_item__rambutan_post=post)

    if request.method == 'POST':
        if associated_order_items.exists():
            messages.warning(request, 'This post cannot be deleted because it has associated orders.')
            return redirect('view_posts')
        post.delete()
        messages.success(request, 'Post deleted successfully.')
        return redirect('view_posts')  
    return render(request, 'confirm_delete.html', {
        'post': post,
        'has_orders': associated_order_items.exists(),
        'associated_orders': associated_order_items
    })'''
@login_required
def delete_post_confirmation(request, id):
    post = get_object_or_404(RambutanPost, id=id)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully.')
        return redirect('view_posts')

    return render(request, 'confirm_delete.html', {
        'post': post,
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
    products = RambutanPost.objects.values('id','name', 'variety', 'image', 'price_per_kg', 'created_at', 'description')
    
    context = {
        'products': products
    }
    return render(request, 'shop.html', context)

@login_required
def wishlist(request):
    
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('rambutan_post')

    wishlists = RambutanPost.objects.filter(id__in=[item.rambutan_post_id for item in wishlist_items])

    return render(request, 'wishlist.html', {'wishlist_items': wishlists})

@login_required
def add_to_wishlist(request,id):
    post = RambutanPost.objects.get(id=id)
    wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            rambutan_post=post 
        )

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
    if request.method == 'POST':
        first_name = request.POST['first-name']
        last_name = request.POST['last-name']
        country = request.POST['country']
        street_address = request.POST['street-address']
        city = request.POST['city']
        postcode = request.POST['postcode']
        phone = request.POST['phone']
        email = request.POST['email']

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
    billing_details = BillingDetail.objects.filter(user=request.user).last()
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect('cart')  

    subtotal = sum(item.total_price for item in cart_items)
    delivery_fee = 0
    discount = 0
    total = subtotal + delivery_fee - discount

    if request.method == 'POST':
        payment_method = request.POST.get('payment-method')

        order = Order.objects.create(
            billing_detail=billing_details,
            user=request.user,
            total_amount=total,
            payment_method=payment_method
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                #cart_item=item,
                #rambutan_post=item.rambutan_post,
                quantity=item.quantity,
                price=item.price
            )

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
