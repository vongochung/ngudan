from django import forms
from django.contrib import admin
from home.models import  POST,Category


class POSTForm(forms.ModelForm):

    class Meta:
        model = POST
        fields = ('title', 'link', 'description' , 'category', 'start', 'end')


class CustomPOSTAdmin(admin.ModelAdmin):
    fieldsets = None
    form = POSTForm
    def save_model(self, request, obj, form, change): 
        instance = form.save(commit=False)
        instance.author = request.user
        instance.save()
        return instance

class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ('name', 'parent_id')


class CustomCategoryAdmin(admin.ModelAdmin):
    fieldsets = None
    form = CategoryForm

admin.site.register(POST, CustomPOSTAdmin)
admin.site.register(Category, CustomCategoryAdmin)