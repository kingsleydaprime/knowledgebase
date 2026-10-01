from django.http import JsonResponse

from core.models import Customer


def user_list(request):
    return JsonResponse({"users": list(Customer.objects.values("id", "email"))})
