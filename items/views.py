from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ItemForm
from .models import Item


@login_required
def item_create(request, kind):
    if kind not in Item.Kind.values:  # only "lost" or "found"
        raise Http404
    form = ItemForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            item = form.save(commit=False)
            item.kind = kind
            item.reporter = request.user  # never trust the client for this
            item.save()
            messages.success(request, "Your report has been posted.")
            return redirect(item)
        messages.error(request, "We couldn't post your report. Fix the highlighted fields.")
    return render(request, "items/form.html", {"form": form, "kind": kind})


@login_required
def item_detail(request, pk):
    item = get_object_or_404(Item.objects.select_related("category", "reporter"), pk=pk)
    return render(request, "items/detail.html", {"item": item})