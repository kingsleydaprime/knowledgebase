from django.http import JsonResponse

from .models import Order


def order_list(request):
    return JsonResponse({"orders": list(Order.objects.values("id", "total_pence"))})
