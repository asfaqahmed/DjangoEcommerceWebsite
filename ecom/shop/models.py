from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)
    price = models.IntegerField()
    weight = models.FloatField()
    Availability = models.CharField( max_length=50)
    image = models.ImageField(upload_to="", blank=True)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url=self.image.url
        except:
            url=''
        return url





class Order(models.Model):
	customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	date_ordered = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False)
	transaction_id = models.CharField(max_length=100, null=True)

	def __str__(self):
		customer=self.customer
		id=self.customer.id
		return str(customer)+"-"+str(id)

	@property
	def getCartTotal(self):
		orderitems = self.orderitem_set.all()
		total= sum([item.getTotal for item in orderitems])
		return total

	@property
	def getCartItems(self):
		orderitems = self.orderitem_set.all()
		total= sum([item.quantity for item in orderitems])
		return total


class OrderItem(models.Model):
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(default=0, null=True, blank=True)
	dateAdded = models.DateTimeField(auto_now_add=True)

	@property
	def getTotal(self):
		total = self.product.price * self.quantity
		return total

	def __str__(self):
		try:
			orderit=self.order.customer
			prod=self.product.name
			return str(orderit)+"-"+prod
		except Exception as e:
			return e

		
	
	


class ShippingAddress(models.Model):
	customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	name = models.CharField(max_length=50, null=False, default=customer)
	address = models.CharField(max_length=200, null=False)
	city = models.CharField(max_length=200, null=False)
	state = models.CharField(max_length=200, null=False)
	zipcode = models.CharField(max_length=200, null=False)
	phone = models.CharField(max_length=15, null=False)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		temp= str(self.customer)+  ' ' +str(self.date_added)
		return temp



class CustomerMessages(models.Model):
	name = models.CharField(max_length=50, null=False)
	phone = models.CharField(max_length=15, null=False)
	email=models.CharField(max_length=50, null=False)
	message = models.CharField( max_length=500, null=False, blank=True)

	def __str__(self):
		temp= str(self.name)+ '-' + str(self.email)
		return temp