from django import forms
from .models import Purchase, Transfer, Assignment, Asset, Base

class PurchaseForm(forms.ModelForm):
    asset = forms.ModelChoiceField(queryset=Asset.objects.all(), empty_label="Select Asset")
    class Meta:
        model = Purchase
        fields = ['asset', 'quantity']

class TransferForm(forms.ModelForm):
    asset = forms.ModelChoiceField(queryset=Asset.objects.all(), empty_label="Select Asset")
    from_base = forms.ModelChoiceField(queryset=Base.objects.all(), empty_label="Select From Base")
    to_base = forms.ModelChoiceField(queryset=Base.objects.all(), empty_label="Select To Base")
    class Meta:
        model = Transfer
        fields = ['asset', 'from_base', 'to_base', 'quantity']

class AssignmentForm(forms.ModelForm):
    asset = forms.ModelChoiceField(queryset=Asset.objects.all(), empty_label="Select Asset")
    class Meta:
        model = Assignment
        fields = ['asset', 'personnel', 'quantity', 'expended']
