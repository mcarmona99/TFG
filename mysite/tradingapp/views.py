from django.shortcuts import render, get_object_or_404
from django.views import generic

from .models import Currencies


class IndexView(generic.ListView):
    template_name = 'tradingapp/index.html'
    context_object_name = 'currencies_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Currencies.objects.all()


def graph_form(request, pair_id):
    return render(request, "tradingapp/graph_form.html")


def detail(request, pair_id):
    if request.method == "POST":
        start = request.POST["datetimeStart"]
        end = request.POST["datetimeEnd"]
        curr = get_object_or_404(Currencies, pk=pair_id)
        graph = curr.return_graph_range(start, end)
        context = {
            'graph': graph,
        }
        return render(request, 'tradingapp/detail.html', context)
