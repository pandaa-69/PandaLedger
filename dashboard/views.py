import logging
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .services import get_market_dashboard_data 

logger = logging.getLogger(__name__)

@require_GET
def market_dashboard_api(request):
    """
    API Endpoint: Returns the consolidated market dashboard data.
    
    Data Source logic is handled by the service layer:
    1. Returns directly from Cache if available.
    2. Fallbacks to Database if cache misses.
    3. Triggers background refresh lazily if data is stale/missing.
    
    Returns:
        JSON response: { "market_summary": [...], "news": [...] }
    """
    try:
        data = get_market_dashboard_data()
        return JsonResponse(data)
    except Exception as e:
        logger.error(f"Market Dashboard View Error: {e}", exc_info=True)
        return JsonResponse({"error": "Failed to load dashboard data"}, status=500)
