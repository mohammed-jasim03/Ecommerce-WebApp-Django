from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
from .models import Product,Brand,ReviewImage,Category,Wishlist,Profile
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib.auth.forms import UserCreationForm 
from django import forms
from .forms import SignUpForm,UpdateUserForm,ChangePasswordForm,UserInfoForm,ProductFilterForm
from cart.forms import ShippingForm
from cart.models import ShippingAddress





# Create your views here.
def main_home(requset):
     return render(requset,'main_home.html')

def product_by_brand(request, brand_name):
    brand = get_object_or_404(Brand, name__iexact=brand_name)
    products = Product.objects.filter(brand=brand)
    return render(request, 'product_list.html', {'products': products, 'brand': brand})

def product_list_by_category(request, category_name):
    # Get the category by its name
    category = get_object_or_404(Category, name=category_name)
    
    # Filter products by the category
    products = Product.objects.filter(category=category)
    
    context = {
        'category': category,
        'products': products,
    }
    
    return render(request, 'category_products.html', context)


def category_summary(request):
	categories = Category.objects.all()
	return render(request, 'category_summary.html', {"categories":categories})	


def category(request,dd):
    # replace hyphons with space
    dd = dd.replace('-',' ')
    #grap the category from url
    try:
        #lookup categoy
        category = Category.objects.get(name=dd)
        products = Product.objects.filter(category=category)
        return render(request,'category.html',{'products':products,'category':category})
    except:
        messages.success(request,('There is no such category exits...'))
        return redirect('home')


def home(request):
    products = Product.objects.all()
    filter_form = ProductFilterForm(request.GET)
    sort_by = request.GET.get('sortby', 'id')  # Default sort by 'id'

    if filter_form.is_valid():
        if filter_form.cleaned_data['brand']:
            products = products.filter(brand__in=filter_form.cleaned_data['brand'])
        if filter_form.cleaned_data['category']:
            products = products.filter(category__in=filter_form.cleaned_data['category'])
        if filter_form.cleaned_data['gender']:
            products = products.filter(gender_category__in=filter_form.cleaned_data['gender'])
        if filter_form.cleaned_data['is_sale']:
            products = products.filter(is_sale=filter_form.cleaned_data['is_sale'])

    if sort_by == 'newest':
        products = products.order_by('-id')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'discount':
        products = products.filter(is_sale=True).order_by('-sale_price')
    else:
        products = products.order_by('id')  # Default sort

    return render(request, 'home.html', {'products': products, 'filter_form': filter_form})

def product(request, pk):
    product = get_object_or_404(Product, id=pk)
    reviews = product.reviews.all()
    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            # Save review images if there are any
            for file in request.FILES.getlist('images'):
                ReviewImage.objects.create(review=review, image=file)
            messages.success(request, 'Your review has been submitted!')
            return redirect('product', pk=pk)
    else:
        form = ReviewForm()
    return render(request, 'product.html', {'product': product, 'reviews': reviews, 'form': form})

@login_required
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()

            # Save review images if there are any
            for file in request.FILES.getlist('images'):
                ReviewImage.objects.create(review=review, image=file)

            messages.success(request, 'Your review has been submitted!')
            return redirect('product', pk=product_id)
    else:
        form = ReviewForm()

    return render(request, 'product.html', {'product': product, 'form': form})

def about(request):
    return render(request, 'about.html',{})

@login_required
def add_to_wishlist(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        
        # Get or create the wishlist for the user
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        
        # Check if the product is already in the wishlist
        if product not in wishlist.products.all():
            wishlist.products.add(product)
            return JsonResponse({'status': 'success', 'message': 'Product added to wishlist'})
        else:
            return JsonResponse({'status': 'fail', 'message': 'Product is already in wishlist'})
    else:
        return JsonResponse({'status': 'fail', 'message': 'User not authenticated or incorrect request method'})
def view_wishlist(request):
    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        products = wishlist.products.all()  # Get all products in the wishlist
        return render(request, 'wishlist.html', {'products': products})
    else:
        return redirect('login')



def login_user(request):
    if request.method == 'POST':
        username = request.POST['usrname']
        password = request.POST['passwrd']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, ('You have been logged in...'))
            return redirect('home')
        else:
            messages.success(request, ('Oops..something went wrong...try again'))
            return redirect('login')
    else:
        return render(request, 'login.html', {})

def check_username(request):
    username = request.GET.get('username')
    data = {
        'is_taken': User.objects.filter(username=username).exists()
    }
    if data['is_taken']:
        data['error_message'] = 'Username already exists'
    return JsonResponse(data) 

def update_info(request):
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user=request.user)
        if request.method == 'POST':
            form = UserInfoForm(request.POST, instance=current_user)
            if form.is_valid():
                form.save()
                messages.success(request, "User info has been updated!")
                return redirect('main_home')
        else:
            form = UserInfoForm(instance=current_user)
        return render(request, "update_info.html", {'form': form})
    else:
        messages.success(request, "You must be logged in to access that page!")
        return redirect('login')

def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)
        if user_form.is_valid():
            user_form.save()
            login(request, current_user)
            messages.success(request, "User has been updated!")
            return redirect('main_home')
        return render(request, "update_user.html", {'user_form': user_form})
    else:
        messages.success(request, "You must be logged in to access that page!")
        return redirect('login')

def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been updated...")
                login(request, current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                return redirect('update_password')
        else:
            form = ChangePasswordForm(current_user)
        return render(request, "update_password.html", {'form': form})
    else:
        messages.success(request, "You must be logged in to view that page...")
        return redirect('home')

def logout_user(request):
    logout(request)
    messages.success(request, ('You have been logged out...'))
    return redirect('home')

def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the form to create the user
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')  # Get the raw password
            user = authenticate(username=username, password=raw_password)  # Use the raw password here
            login(request, user)
            messages.success(request, ('User has been created.... please, fill up your Info'))
            return redirect('update_info')
        else:
            print(form.errors)  # Print form errors
            messages.success(request, ('Oops!! Something went wrong...try again'))
            return redirect('register')
    else:
        return render(request, 'register.html', {'form': form})
