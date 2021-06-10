from django.shortcuts import render
from django.views import generic


class IndexView(generic.View):
    template_name = 'TradingAPP/index.html'


def menu_principal(request):
    return render(request, "TradingAPP/menu_principal.html")
