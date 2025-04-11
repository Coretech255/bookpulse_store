from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.shortcuts import get_object_or_404, render, redirect
from .models import Order, OrderItem
from.forms import OrderCreateForm
from cart.cart import Cart

import weasyprint
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.template.loader import render_to_string

def order_create(request):
    cart = Cart(request)

        # Check if cart is empty
    if len(cart) == 0:
        return redirect(reverse('cart:cart_detail'))
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            # clear the cart
            cart.clear()

            #set the order in the session
            request.session['order_id'] = order.id
            #redirect for payment
            return redirect(reverse('payment:process'))
    else:
        form = OrderCreateForm()
    return render(request,
                      'orders/order.html',
                        {'cart': cart})


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/orders/order/detail.html', {'order': order})


@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('orders/order/pdf.html', {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    print(finders.find('css/pdf.css'))
    weasyprint.HTML(string=html).write_pdf(response, stylesheets=[weasyprint.CSS(finders.find('css/pdf.css'))])
    return response