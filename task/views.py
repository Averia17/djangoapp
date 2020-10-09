import stripe
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.http import JsonResponse
import json
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login, logout

from .forms import CreateUserForm, CreateAddressForm
from .models import Product, Customer
from .utils import cookieCart, cartData, guestOrder

stripe.api_key = settings.STRIPE_SECRET_KEY


def home(request):
    data = cartData(request)
    cartItems = data['cartItems']

    order = data['order']
    items = data['items']

    all_items = Product.objects.all()
    context = {'all_items': all_items, 'cartItems': cartItems}
    return render(request, 'index.html', context)


def women(request):
    data = cartData(request)
    cartItems = data['cartItems']

    women_items = Product.objects.filter(gender="W")
    # if len(women_items) < 1:
    gender = women_items[0].get_gender_display()
    context = {'all_items': women_items, 'gender': gender, 'cartItems': cartItems}
    return render(request, 'women.html', context)


def men(request):
    data = cartData(request)
    cartItems = data['cartItems']

    men_items = Product.objects.filter(gender="M")
    gender = men_items[0].get_gender_display()
    context = {'all_items': men_items, 'gender': gender, 'cartItems': cartItems}
    return render(request, 'men.html', context)


def menProductType(request, productType):
    data = cartData(request)
    cartItems = data['cartItems']

    all_items = Product.objects.filter(productType=productType, gender="M")
    context = {'all_items': all_items, 'cartItems': cartItems}
    return render(request, 'men.html', context)


def womenProductType(request, productType):
    data = cartData(request)
    cartItems = data['cartItems']

    all_items = Product.objects.filter(productType=productType, gender="W")
    context = {'all_items': all_items, 'cartItems': cartItems}
    return render(request, 'women.html', context)


def item_detail(request, item_id):
    data = cartData(request)
    cartItems = data['cartItems']

    item = Product.objects.get(id=item_id)
    context = {'item': item, 'cartItems': cartItems}
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
    data = cartData(request)
    cartItems = data['cartItems']

    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)

            return redirect('/login')

    context = {'form': form, 'cartItems': cartItems}
    return render(request, 'signup.html', context)


def AddAddress(request):
    form = CreateAddressForm()
    if request.method == 'POST':
        form = CreateAddressForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('')


def loginPage(request):
    data = cartData(request)
    cartItems = data['cartItems']

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Username OR password is incorrect')

    context = {'cartItems': cartItems}
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
    user = request.user
    print(user)
    context = {'items': items, 'order': order, 'cartItems': cartItems, 'user': user}
    if cartItems == 0:
        return redirect('/')

    return render(request, 'checkout.html', context)


def SuccessView(request):
    return render(request, 'success.html')


def CancelledView(request):
    return render(request, 'cancelled.html')


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    size = data['size']

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product, size=size)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def addAddress(request):
    return "add"


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
    print(order.transaction_id)
    print("SUCCESS")

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            name=data['form']['name'],
            surname=data['form']['surname'],
            mobile_phone=data['form']['mobile_phone'],
            country=data['shipping']['country'],
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            region=data['shipping']['region'],
            postcode=data['shipping']['postcode'],
        )

    return JsonResponse('Payment submitted..', safe=False)


@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        domain_url = 'http://localhost:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # Create new Checkout Session for the order
            # Other optional params include:
            # [billing_address_collection] - to display billing address details on the page
            # [customer] - if you have an existing Stripe Customer ID
            # [payment_intent_data] - capture the payment later
            # [customer_email] - prefill the email input in the form
            # For full details see https://stripe.com/docs/api/checkout/sessions/create

            # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
            checkout_session = stripe.checkout.Session.create(
                client_reference_id=request.user.id if request.user.is_authenticated else None,
                success_url=domain_url + 'success/',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        'name': 'T-shirt',
                        'quantity': 1,
                        'currency': 'usd',
                        'amount': '2000',
                    }
                ]
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")
        # TODO: run some custom code here

    return HttpResponse(status=200)