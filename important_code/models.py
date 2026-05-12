from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# Create your models here.

# Create Customer Profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=20, blank=True)
    address1 = models.CharField(max_length=200, blank=True)
    address2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)  # Corrected here
    pincode = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    old_cart = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.username


# Create a user Profile by default when user signs up

def create_profile(sender, instance, created, **kwargs):
	if created:
		user_profile = Profile(user=instance)
		user_profile.save()

# Automate the profile thing
post_save.connect(create_profile, sender=User)


# Brand model
class Brand(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

#categories of products

class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def __str__ (self):
        return self.name
    
    class Meta:
        verbose_name_plural= 'categories'


'''class GenderCategory(models.Model):
    CATEGORY_CHOICES = (
        ('Men', 'Men'),
        ('Women', 'Women'),
        ('Unisex', 'Unisex'),
    )
    gender_category = models.CharField(max_length=6, choices=CATEGORY_CHOICES, default='Unisex')

    def __str__(self):
        return self.gender_category'''

class GenderCategory(models.Model):
    gender_category = models.CharField(max_length=50)

    def __str__(self):
        return self.gender_category


#customer
class customer(models.Model):
    f_name = models.CharField(max_length=20)
    l_name = models.CharField(max_length=20)
    phone = models.CharField(max_length=10)
    email = models.EmailField(max_length=50)
    pass_wd = models.CharField(max_length=100)
   
    def __str__ (self):
        return f'{self.f_name} {self.l_name}'



#all of our products
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(default=0,decimal_places=2,max_digits=8)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,default=1)
    description = models.CharField(max_length=1000, default='', blank=True, null=True)
    main_image = models.ImageField(upload_to='uploads/product/')
    gender_category = models.ForeignKey(GenderCategory, on_delete=models.SET_NULL, null=True, blank=True)
   

#sale_or_offer price
    
    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0,decimal_places=2,max_digits=8)
    
    def __str__(self):
        return self.name
    
    

#for image gallery
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='uploads/product/')


# product size chart
    
class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    size = models.CharField(max_length=5)
    is_available = models.BooleanField(default=True)
    # New field to track the quantity of each size
    quantity = models.IntegerField(default=0)  

    def __str__(self):
        return f'{self.product.name} - Size: {self.size} - Quantity: {self.quantity}'

#product Review
class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    rating = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user.username} for {self.product.name}'

# ReviewImage model
class ReviewImage(models.Model):
    review = models.ForeignKey(Review, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='review_images/')

    def __str__(self):
        return f'Image for {self.review}'


# whislist
class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField(Product, related_name='wishlisted_by')

    def __str__(self):
        return f"{self.user.username}'s Wishlist"
    



