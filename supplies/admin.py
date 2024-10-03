from django.contrib import admin
from .models import Item, ItemCategory

# class ItemCategoryInLine(admin.TabularInline):
#     model = ItemCategory



# class ItemAdmin(admin.ModelAdmin):

#  #displays specified question fields in tabular format
#     list_display = ["item_name", "item_category", "quantity", "created_at", "created_by", "last_updated"]
#    #Display Item inline
#     inlines = [ItemCategoryInLine]





# Register your models here.
admin.site.register([Item,
                      ItemCategory
                      
                      
                      ])
# admin.site.register(Item, ItemAdmin)