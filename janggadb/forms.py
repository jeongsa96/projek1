from django import forms
from django.forms.widgets import Textarea
from django.contrib.auth.forms import UserCreationForm
from .models import User, Project, Invoice, PO

class LoginForm(forms.Form):
    username = forms.CharField(
        widget = forms.TextInput(
            attrs={
                "name": "username", 
                "id": "username", 
                "class": "bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",                
                "type": "text",
                "placeholder": "username"
            }
        )
    )
    password = forms.CharField(
        widget = forms.PasswordInput(
            attrs={
               "id": "password", 
               "name": "password", 
                "class": "bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",                
                "type": "password",
                "placeholder": "••••••••"
            }
        )
    )

class RegisterForm(UserCreationForm):
    username = forms.CharField(
        widget = forms.TextInput(
            attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            }
        )
    )
    password1 = forms.CharField(
        widget = forms.PasswordInput(
            attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            }
        )
    )
    password2 = forms.CharField(
        widget = forms.PasswordInput(
            attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            }
        )
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            }
        )
    )

    class Meta:
        model = User
        fields = ('username','email','password1','password2','is_admin','is_projectManager','is_logistik','is_finance')
    
class ProjekForm(forms.ModelForm):
    client = forms.CharField(
        widget = forms.TextInput(
            attrs={
                'class':'input validator p-2 mb-4 w-auto',
                'placeholder':'Client',
                'id':'client',
                'name':'client',
            }
        )
    )
    lokasi = forms.CharField(
        widget = forms.TextInput(
            attrs={
                'class':'input validator p-2 mb-4 w-auto',
                'placeholder':'Lokasi',
                'id':'lokasi',
                'name':'lokasi',
            }
        )
    )
    jenis_projek = forms.CharField(
        widget = forms.TextInput(
            attrs={
                'class':'input validator p-2 mb-4 w-auto',
                'placeholder':'Jenis Pekerjaan',
                'id':'jenis_projek',
                'name':'jenis_projek',
            }
        )
    )
    SPK = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'placeholder':'SPK',
                'id':'SPK',
                'name':'SPK',
            }
        )
    )

    class Meta: 
        model = Project
        fields = ('client','lokasi','jenis_projek','SPK')
    
class InvoiceForm(forms.ModelForm):
    nomor_invoice = forms.CharField(
        widget= forms.TextInput(
            attrs= {
                'class':'input validator p-2 mb-4 w-auto',
                'placeholder':'No. Invoice',
                'id':'no-invoice',
                'name':'no-invoice',
            }
        )
    )
    tanggal_invoice = forms.DateField(
        widget= forms.DateInput(
            attrs= {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'tgl-invoice',
                'name':'tgl-invoice',
                'type':'text',
                'onfocus':"(this.type='date')",
                'onblur':"(this.type='text')",
                'placeholder':'Tanggal Terbit',
            }
        )
    )
    tanggal_jatuh_tempo = forms.DateField(
        widget= forms.DateInput(
            attrs= {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'tgl',
                'name':'tgl',
                'type':'text',
                'onfocus':"(this.type='date')",
                'onblur':"(this.type='text')",
                'placeholder':'Tanggal Jatuh Tempo',
            }
        )
    )
    jumlah_tagihan = forms.IntegerField(
        widget= forms.NumberInput(
            attrs= {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'jumlah-tagihan',
                'name':'jumlah-tagihan',
                'type':'number',
                'placeholder':'Jumlah Tagihan',
            }
        )
    )
    lampiran = forms.FileField(
        widget = forms.FileInput(
            attrs= {
                'class':'file-input p-2 mb-4 w-auto',
                'id':'lampiran',
                'name':'lampiran',
                'type':'file',
            }
        )
    )

    class Meta:
        model = Invoice
        fields = ['nomor_invoice','tanggal_invoice','tanggal_jatuh_tempo','jumlah_tagihan','lampiran','status','client_id']

class POform(forms.ModelForm):
    vendor = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'vendor',
                'name':'vendor',
                'type':'text',
                'placeholder':'Vendor'
            }
        )
    )
    nomor_po = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'nomor-po',
                'name':'nomor-po',
                'type':'text',
                'placeholder':'Nomor PO',
            }
        )
    )
    tanggal_po = forms.DateField(
        widget = forms.DateInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'tgl-po',
                'name':'tgl-po',
                'type':'date',
            }
        )
    )
    deskripsi_barang = forms.CharField(
        widget = Textarea(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'deskripsi',
                'name':'deskripsi',
                'type':'text',
                'placeholder':'Deskripsi Barang',
                'cols':30,
                'rows':4,
            }
        )
    )
    kuantitas = forms.IntegerField(
        widget= forms.NumberInput(
            attrs= {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'kuantitas',
                'name':'kuantitas',
                'type':'number',
                'placeholder':'Kuantitas',
                'oninput':'calculateTotal()',
            }
        )
    )
    harga_satuan = forms.IntegerField(
        widget= forms.NumberInput(
            attrs= {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'harga-satuan',
                'name':'harga-satuan',
                'type':'number',
                'placeholder':'Harga Satuan',
                'oninput':'calculateTotal()',
            }
        )
    )
    total = forms.IntegerField(
        widget= forms.NumberInput(
            attrs= {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'total',
                'name':'total',
                'type':'number',
                'placeholder':'Total',
            }
        )
    )

    class Meta:
        model = PO
        fields = ['vendor','nomor_po','tanggal_po','deskripsi_barang','kuantitas','harga_satuan','total','client_id']
        