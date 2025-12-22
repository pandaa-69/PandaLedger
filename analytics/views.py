from django.http import JsonResponse
from .services.calculators import calculate_portfolio_xirr, get_sector_split
from .services.metrics import calculate_portfolio_metrics, calculate_health_score
from .models import PortfolioSnapshot
from ledger.models import Expense
from portfolio.models import Holding
from django.db.models import Sum
from django.utils import timezone


def portfolio_analytics(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    xirr_value = calculate_portfolio_xirr(request.user)
    sectors = get_sector_split(request.user)

    risk_metrics = calculate_portfolio_metrics(request.user)
    health_score = calculate_health_score(request.user)

    snapshots = PortfolioSnapshot.objects.filter(user=request.user).order_by('date')

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
            "beta": risk_metrics['beta'],
            "volatility": risk_metrics['volatility'],
            "health_score": health_score,
        },
        "sectors": sectors,
        "performance_graph": performance_data
    })


def home_summary(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    today = timezone.now()
    month_spend = Expense.objects.filter(
        user=request.user,
        date__month=today.month,
        date__year=today.year
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    holdings = Holding.objects.filter(user=request.user).select_related('asset')
    net_worth = sum(h.quantity * h.asset.last_price for h in holdings)

    return JsonResponse({
        "monthly_spend": float(month_spend),
        "monthly_budget": float(request.user.monthly_budget),
        "net_worth": float(net_worth),
        "username": request.user.username
    })
