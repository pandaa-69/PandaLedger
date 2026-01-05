import logging
from django.http import JsonResponse
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

from .services.calculators import calculate_portfolio_xirr, get_sector_split
from .services.metrics import calculate_portfolio_metrics, calculate_health_score
from .models import PortfolioSnapshot
from ledger.models import Expense
from portfolio.models import Holding

logger = logging.getLogger(__name__)

@require_GET
def portfolio_analytics(request):
    """
    API Endpoint: Returns detailed portfolio analytics.

    Data Included:
    - XIRR (Extended Internal Rate of Return)
    - Risk Metrics (Beta, Volatility)
    - Portfolio Health Score
    - Sector Allocation
    - Historical Performance Graph Data

    Returns:
        JSON response with metrics and graph data.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        user = request.user
        
        # Calculate complex metrics (delegated to services)
        xirr_value = calculate_portfolio_xirr(user)
        sectors = get_sector_split(user)
        risk_metrics = calculate_portfolio_metrics(user)
        health_score = calculate_health_score(user)

        # Fetch historical data for the graph
        snapshots = PortfolioSnapshot.objects.filter(user=user).order_by('date')
        
        performance_data = [{
            "name": s.date.strftime('%b-%y'),
            "date": s.date.isoformat(),
            "portfolio": float(s.total_value),
            "invested": float(s.invested_value),
            "benchmark": float(s.benchmark_value) if s.benchmark_value else None,
        } for s in snapshots]

        return JsonResponse({
            "metrics": {
                "xirr": xirr_value,
                "beta": risk_metrics.get('beta', 0),
                "volatility": risk_metrics.get('volatility', 0),
                "health_score": health_score,
            },
            "sectors": sectors,
            "performance_graph": performance_data
        })

    except Exception as e:
        logger.error(f"Error generating portfolio analytics for user {request.user.username}: {e}", exc_info=True)
        return JsonResponse({"error": "Failed to calculate analytics"}, status=500)


@require_GET
def home_summary(request):
    """
    API Endpoint: Returns a high-level summary for the dashboard home screen.

    Data Included:
    - Current Month's Spend
    - Monthly Budget
    - Net Worth (Real-time calculation based on current asset prices)

    Returns:
        JSON response with summary stats.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        today = timezone.now()
        
        # 1. Calculate Monthly Spend
        month_spend = Expense.objects.filter(
            user=request.user,
            date__month=today.month,
            date__year=today.year
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # 2. Calculate Real-time Net Worth
        holdings = Holding.objects.filter(user=request.user).select_related('asset')
        net_worth = sum(h.quantity * h.asset.last_price for h in holdings)

        return JsonResponse({
            "monthly_spend": float(month_spend),
            "monthly_budget": float(getattr(request.user, 'monthly_budget', 0)), # Safe access using getattr
            "net_worth": float(net_worth),
            "username": request.user.username
        })

    except Exception as e:
        logger.error(f"Error generating home summary for user {request.user.username}: {e}", exc_info=True)
        return JsonResponse({"error": "Failed to load summary"}, status=500)
