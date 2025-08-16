from cart.models import Cart, CartItem

def cart_items(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.session.session_key or request.session.create()
        cart, _ = Cart.objects.get_or_create(session_id=session_id)
    return {'cart_items': cart.cartitem_set.all()}