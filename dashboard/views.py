from django.shortcuts import render
from django.http import HttpResponse
from core import services



def dashboard_view(request):
    # get the rate 
    usd_rate = services.get_usd_inr_rate()

    return HttpResponse(f"<h1> Currently the USD INR Rate is {usd_rate} </h1>")

