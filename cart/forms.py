from django import forms

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 5)]

class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, 
                                      coerce=int, 
                                      widget=forms.Select(attrs={'class': 'form qty', }))
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)