from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Cart, Favorites, Ingredient, IngredientAmount, Recipe, Tag


class IngridientResource(resources.ModelResource):

    class Meta:
        model = Ingredient


class IngredientInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1


class IngredientAdmin(ImportExportModelAdmin):
    resource_classes = [IngridientResource]
    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    list_filter = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'name',
        'image',
        'text',
        'is_favorited',
    )
    search_fields = ('author__username', 'name',)
    list_filter = ('author', 'name', 'tags')
    inlines = (IngredientInline,)

    def is_favorited(self, obj):
        return obj.favorite_recipe.count()


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientAmount)
admin.site.register(Tag)
admin.site.register(Cart)
admin.site.register(Favorites)
