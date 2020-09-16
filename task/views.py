from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.http import JsonResponse
import json
import datetime
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login, logout

from .forms import CreateUserForm
from .models import Product, Customer
from .utils import cookieCart, cartData, guestOrder


def home(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    all_items = Product.objects.all()
    context = {'all_items': all_items, 'cartItems': cartItems}
    return render(request, 'index.html', context)


def women(request):
    women_items = Product.objects.filter(gender="W")
    # if len(women_items) < 1:
    gender = women_items[0].get_gender_display()
    context = {'all_items': women_items, 'gender': gender}
    return render(request, 'women.html', context)


def men(request):
    men_items = Product.objects.filter(gender="M")
    gender = men_items[0].get_gender_display()
    context = {'all_items': men_items, 'gender': gender}
    return render(request, 'men.html', context)


def item_detail(request, item_id):
    item = Product.objects.get(id=item_id)
    context = {'item': item}
    return render(request, 'item_detail.html', context)


def subscribe(request):
    if request.POST:
        to_mail = request.POST['email']
        gender = request.POST['gender']
    subject = 'Thank you for subscribing'
    message = ' it  means a world to us '
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [to_mail, ]
    if subject and message and email_from:
        try:
            send_mail(subject, message, email_from, recipient_list)
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return HttpResponseRedirect('/')
    else:
        return HttpResponse('Make sure all fields are entered and valid.')


def signup(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)

            return redirect('/login')

    context = {'form': form}
    return render(request, 'signup.html', context)


def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Username OR password is incorrect')

    context = {}
    return render(request, 'login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('/login')


def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'cart.html', context)


def checkout(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    # if order.shipping == True:
    #     ShippingAddress.objects.create(
    #         customer=customer,
    #         order=order,
    #         address=data['shipping']['address'],
    #         city=data['shipping']['city'],
    #         state=data['shipping']['state'],
    #         zipcode=data['shipping']['zipcode'],
    #     )

    return JsonResponse('Payment submitted..', safe=False)
