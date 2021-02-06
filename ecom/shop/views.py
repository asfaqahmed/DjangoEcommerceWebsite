from django.shortcuts import render, redirect
from django.contrib import messages
from . models import *
from django.conf import settings
import requests
import json
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login ,logout
from django.views.decorators.csrf import csrf_exempt
from . import Checksum
# Create your views here.







def index(request):
    cakes= Product.objects.all()
    paginator= Paginator(cakes,8)
    pageNum=request.GET.get('page', 1)
    page= paginator.page(pageNum)
    pageHasPrevious= page.has_previous()
    pageHasNext= page.has_next()
    pagerange= paginator.page_range

    
    try:
        nextpageNum=page.next_page_number()
    except:
        nextpageNum=paginator.num_pages

    try:
        previouspageNum=page.previous_page_number()
    except:
        previouspageNum=1
    

    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer= customer, complete= False )
        cartItems= order.getCartItems
    else:
        cartItems=0
    context={"page": page, 'cartItems':cartItems, 'pagerange':pagerange, 'pageHasPrevious':pageHasPrevious, 'pageHasNext':pageHasNext, 'nextpageNum':nextpageNum, 'previouspageNum':previouspageNum, 'pageNum':pageNum}
    messages.success(request, 'Welcome to Bakelogy Cakes. Everything we bake, We bake with Love.')
    return render(request, 'shop/index.html', context)







def cart(request):    
    if request.user.is_authenticated:
        customer = request.user

        #customer, created = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer= customer, complete= False )
        items= order.orderitem_set.all()
        cartItems= order.getCartItems
    else:
        messages.error(request, 'To see your cart Please Login First ')
        return redirect('home')
        # items=[]
        # order=[]
    
    context={"items": items,'order': order, 'cartItems':cartItems}
    return render(request, 'shop/cart.html', context)







def updateItem(request):
    
    data= json.loads(request.body)
    productId= data['productId']
    action= data['action']
    

    customer= request.user
    product= Product.objects.get(id= productId)
    
    order, created = Order.objects.get_or_create(customer= customer, complete= False )
    orderItem, created= OrderItem.objects.get_or_create(order=order, product= product)

    if action=='add':
        orderItem.quantity=(orderItem.quantity+1)
    elif action=="remove":
        orderItem.quantity=(orderItem.quantity-1)

    orderItem.save()

    if orderItem.quantity<=0:
        orderItem.delete()
    
    return JsonResponse("Item Updated" , safe=False)
    







def LoginUser(request):
    if request.user.is_authenticated:
        messages.error(request, 'User Already Logged In ')
        return redirect('home')

    if request.method=="POST":
        username=request.POST.get('username', '')
        password=request.POST.get('password','')
        user = authenticate(username=username, password=password)
        if user is not None:
            # A backend authenticated the credentials
            login(request, user)
            messages.success(request, "Login Successful. Hello {}".format(request.user))
            return redirect('home')    
        else:
            # No backend authenticated the credentials
            messages.error(request, "Wrong username or password")
            return redirect('LoginUser')
        

    context={}
    return render(request, 'shop/Login.html', context)







def RegisterUser(request):
    if request.user.is_authenticated:
        messages.error(request, 'User Already Logged In ')
        return redirect('home')

    if request.method=="POST":
        fullname=request.POST.get('fullname', '')
        email=request.POST.get('email', '')
        username=request.POST.get('username', '')
        password=request.POST.get('password','')
        temp=fullname.split(' ')
    
        firstName=temp[0]
        lastName=temp[1]
        user=User.objects.create_user(username, email, password)
        user.first_name= firstName
        user.last_name=lastName
        user.save()
        login(request, user)
        messages.success(request, "Account Created Successfully")
        return redirect('home')
        
    context={}
    return render(request, 'shop/Register.html', context)








def LogoutUser(request):
    logout(request)
    messages.success(request, "Logout Successful")
    return redirect('LoginUser')









def viewProduct(request,productid):
    if request.user.is_authenticated:
        customer = request.user

        #customer, created = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer= customer, complete= False )
        items= order.orderitem_set.all()
        cartItems= order.getCartItems

    if productid:
        cake=Product.objects.get(id=productid)
        context={"cake":cake, 'cartItems':cartItems}
    else:
        context={'cartItems':cartItems}
        return redirect('home')
    
    return render(request, 'shop/viewProduct.html',context)









def VerifyPaytmResponse(response):
    response_dict = {}
    if response.method == "POST":
        data_dict = {}
        for key in response.POST:
            data_dict[key] = response.POST[key]
        MID = data_dict['MID']
        ORDERID = data_dict['ORDERID']
        verify = Checksum.verify_checksum(data_dict, settings.PAYTM_MERCHANT_KEY, data_dict['CHECKSUMHASH'])
        if verify:
            STATUS_URL = settings.PAYTM_TRANSACTION_STATUS_URL
            headers = {
                'Content-Type': 'application/json',
            }
            data = '{"MID":"%s","ORDERID":"%s"}'%(MID, ORDERID)
            check_resp = requests.post(STATUS_URL, data=data, headers=headers).json()
            if check_resp['STATUS']=='TXN_SUCCESS':
                response_dict['verified'] = True
                response_dict['paytm'] = check_resp
                return (response_dict)
            else:
                response_dict['verified'] = False
                response_dict['paytm'] = check_resp
                return (response_dict)
        else:
            response_dict['verified'] = False
            return (response_dict)
    response_dict['verified'] = False
    return response_dict










def checkout(request):
    if request.user.is_authenticated:
        customer = request.user

        #customer, created = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer= customer, complete= False )
        items= order.orderitem_set.all()
        cartItems= order.getCartItems
    else:
        return redirect('home')

    if request.user.is_authenticated:
        if request.method == "POST":
            name= request.POST.get('name','')
            email= request.POST.get('email','')
            phone=request.POST.get('phone', '')
            address=request.POST.get('address', '')
            city=request.POST.get('city', '')
            state=request.POST.get('state', '')
            zipcode=request.POST.get('zipcode', '')

            SA=ShippingAddress(customer=customer, order=order, name=name, address=address, city=city, state= state, zipcode=zipcode, phone=phone)
            SA.save()
            

            
            
            totalAmount=str(order.getCartTotal)

            order_id = Checksum.__id_generator__()
            order.transaction_id=order_id
            order.complete=True
        
            order.save()
            data_dict = {
                'MID': settings.PAYTM_MERCHANT_ID,
                'INDUSTRY_TYPE_ID': settings.PAYTM_INDUSTRY_TYPE_ID,
                'WEBSITE': settings.PAYTM_WEBSITE,
                'CHANNEL_ID': settings.PAYTM_CHANNEL_ID,
                'CALLBACK_URL': settings.PAYTM_CALLBACK_URL,
                'MOBILE_NO': str(phone),
                'EMAIL': str(email),
                'CUST_ID': '123123',
                'ORDER_ID':order_id,
                'TXN_AMOUNT': totalAmount,
            } # This data should ideally come from database
            data_dict['CHECKSUMHASH'] = Checksum.generate_checksum(data_dict, settings.PAYTM_MERCHANT_KEY)
            context = {
                'payment_url': settings.PAYTM_PAYMENT_GATEWAY_URL,
                'comany_name': settings.PAYTM_COMPANY_NAME,
                'data_dict': data_dict
            }
            return render(request, 'shop/payment.html', context)

            
            



    context={"items": items, 'cartItems':cartItems, 'order': order}
    return render(request, 'shop/checkout.html', context)



@csrf_exempt
def response(request):
    resp = VerifyPaytmResponse(request)
    if resp['verified']:
        
        
        messages.success(request, 'Payment Successful ')
        # save success details to db; details in resp['paytm']
        return HttpResponse("<center><h1>Transaction Successful</h1><center>", status=200)
    else:
        messages.error(request, 'Payment Unsuccessful ')
        # check what happened; details in resp['paytm']
        return HttpResponse("<center><h1>Transaction Failed</h1><center>", status=400)