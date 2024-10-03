# from django.shortcuts import render

from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpResponse
from .models import Item, ItemCategory
from django.views import generic


class indexView(generic.ListView):
    template_name = "supplies/supplies.html"


    def get_queryset(self):
        return Item.objects.all()

        # return HttpResponse("Welcome to the Inventory Manager! ")
