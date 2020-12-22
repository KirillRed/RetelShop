from django import forms
from django.forms import ValidationError
from . import models

from PIL import Image

class ProductForm(forms.ModelForm):

    MIN_RESOLUTION = (400, 400)
    MAX_RESOLUTION = (1980, 1080)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['main_photo'].help_text = 'Your product resolution must be at least {0}x{1}\
            resolution and maximum {2}x{3}'.format(self.MIN_RESOLUTION[0], self.MIN_RESOLUTION[1],
            self.MAX_RESOLUTION[0], self.MAX_RESOLUTION[1])

    class Meta:
        model = models.Product
        fields = ['title', 'description', 'price', 'main_photo', 'category', 'subcategory']

class SearchForm(forms.Form):
    word = forms.CharField(max_length=50, label='word')

class ImageForm(forms.ModelForm):
    class Meta:
        model = models.ProductImage
        fields = ['image']


ImageFormSet = forms.modelformset_factory(model=models.ProductImage, fields=['image'], can_delete=True, min_num=8, validate_min=True,
                                        max_num=8, validate_max=True)
