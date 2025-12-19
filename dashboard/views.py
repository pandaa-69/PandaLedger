from django.http import JsonResponse
from .services import get_market_dashboard_data 

def market_dashboard_api(request):
    data = get_market_dashboard_data()
    return JsonResponse(data)