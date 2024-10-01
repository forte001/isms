from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.contrib.auth.models import User


def category_name_default():
    return {"category_name_default": "General"}

class ItemCategory(models.Model):
    cat_name = models.CharField(max_length=70)
    cat_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cat_name


# Item model
class Item(models.Model):
    item_name = models.CharField(max_length=200)
    description = models.TextField()
    item_category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE, default=None, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.item_name
    
    # @admin.display(
    #     boolean=True,
    #     ordering='created_by',
    #     description='Items added by',
    # )