from django import forms
from django.forms.widgets import Textarea
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import *
    
class LoginForm(forms.Form):
    username = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                "name": "username", 
                "id": "username", 
                "class": "bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",                
                "type": "text",
                "placeholder": "your username"
            }
        )
    )
    password = forms.CharField(
        widget = forms.PasswordInput(
            attrs = {
               "id": "hs-toggle-password", 
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
            attrs = {
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            }
        )
    )
    password1 = forms.CharField(
        widget = forms.PasswordInput(
            attrs = {
                "type":"password",
                "class": "input validator bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
                "min-length":8,
                "pattern":"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z\d\s]).{8,}$",
                "title":"Must be more than 8 characters, including number, lowercase letter, uppercase letter",
            }
        )
    )
    password2 = forms.CharField(
        widget = forms.PasswordInput(
            attrs = {
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            }
        )
    )
    email = forms.EmailField(
        widget = forms.EmailInput(
            attrs = {
                "class":"bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            }
        )
    )

    class Meta:
        model = User
        fields = ('username','email','password1','password2','is_admin','is_projectManager','is_logistik','is_management','is_client')
    
class ProjekForm(forms.ModelForm):
    client = forms.CharField(
        widget = forms.TextInput(
            attrs ={
                'class':'input validator p-2 mb-4 w-auto',
                'placeholder':'Client',
                'id':'client',
                'name':'client',
            }
        )
    )
    lokasi = forms.CharField(
        widget = forms.TextInput(
            attrs ={
                'class':'input validator p-2 mb-4 w-auto',
                'placeholder':'Lokasi',
                'id':'lokasi',
                'name':'lokasi',
            }
        )
    )
    nominal_kontrak = forms.IntegerField(
        widget = forms.NumberInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'nominal-kontrak',
                'name':'nominal-kontrak',
                'type':'number',
                'placeholder':'Nominal Kontrak',
            }
        )
    )
    jenis_projek = forms.CharField(
        widget = forms.TextInput(
            attrs ={
                'class':'input validator p-2 mb-4 w-auto',
                'placeholder':'Jenis Pekerjaan',
                'id':'jenis_projek',
                'name':'jenis_projek',
            }
        )
    )
    nomor_SPK = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'placeholder':'No.SPK',
                'id':'SPK',
                'name':'SPK',
            }
        )
    )
    lampiran_SPK = forms.FileField(
        widget = forms.FileInput(
            attrs= {
                'class':'file-input p-2 mb-4 w-auto',
                'id':'lampiran-spk',
                'name':'lampiran-spk',
                'type':'file',
            }
        )
    )
    class Meta: 
        model = Project
        fields = '__all__'
    
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
    nomor_po = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'placeholder':'No. PO',
                'id':'no-po',
                'name':'no-po',
            }
        )
    )
    tanggal_invoice = forms.DateField(
        widget = forms.DateInput(
            attrs = {
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
        widget = forms.DateInput(
            attrs = {
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
        widget = forms.NumberInput(
            attrs = {
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
    client_id = forms.ModelChoiceField(
        queryset = Project.objects.only('id'),
        empty_label = 'Pilih Client',
        widget = forms.Select(
            attrs = {
                'class':'select validator p-2 mb-4 w-auto'
            }
        )
    )

    class Meta:
        model = Invoice
        fields = ['nomor_invoice','nomor_po','tanggal_invoice','tanggal_jatuh_tempo','jumlah_tagihan','lampiran','status','client_id']

class POform(forms.ModelForm):
    client_id = forms.ModelChoiceField(
        queryset = Project.objects.only('id'),
        empty_label = 'Pilih Client',
        widget = forms.Select(
            attrs = {
                'class':'select validator p-2 mb-4 w-auto'            
            }
        )
    )
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
            }
        )
    )
    kuantitas = forms.IntegerField(
        widget = forms.NumberInput(
            attrs = {
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
        widget = forms.NumberInput(
            attrs = {
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
        widget = forms.NumberInput(
            attrs = {
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
        fields = ['vendor','nomor_po','tanggal_po','deskripsi_barang','tipe','kuantitas','harga_satuan','total','client_id']
        
class AnggaranForm(forms.ModelForm):   
    deskripsi = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'deskripsi',
                'name':'deskripsi',
                'type':'text',
                'placeholder':'Deskripsi Anggaran',
            }
        )
    )        
    total_anggaran = forms.IntegerField(
        widget = forms.NumberInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'total-anggaran',
                'name':'total-anggaran',
                'type':'number',
                'placeholder':'Jumlah Anggaran',
            }
        )
    )
    client_id = forms.ModelChoiceField(
        queryset = Project.objects.only('id'),
        empty_label = 'Pilih Client',
        widget = forms.Select(
            attrs = {
                'class':'select validator p-2 mb-4 w-auto'            
            }
        )
    )
    jenis_anggaran = forms.ModelChoiceField(
        queryset = Jenis_Anggaran.objects.only('id'),
        label = 'Jenis Anggaran:',
        widget = forms.Select(
            attrs = {
                'class':'hidden',
                'data-select':"""{
    "placeholder": "Pilih Anggaran",
    "toggleTag": "<button type=\'button\' aria-expanded=\'false\'></button>",
    "toggleClasses": "p-2 mb-4 max-w-md advance-select-toggle select select-disabled:pointer-events-none select-disabled:opacity-40",
    "hasSearch": true,
    "dropdownClasses": "advance-select-menu max-h-52 pt-0 overflow-y-auto",
    "optionClasses": "advance-select-option selected:select-active",
    "optionTemplate": "<div class=\'flex justify-between items-center w-full\'><span data-title></span></div>"
    }""",
            }
        )
    )        

    class Meta:
        model = Anggaran
        fields = ['jenis_anggaran','deskripsi','total_anggaran','client_id']

class MonitoringForm(forms.ModelForm):
    tanggal = forms.DateField(
        widget = forms.DateInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'tgl',
                'name':'tgl',
                'type':'text',
                'onfocus':"(this.type='date')",
                'onblur':"(this.type='text')",
                'placeholder':'Tanggal',
            }
        )
    )
    client_id = forms.ModelChoiceField(
        queryset = Project.objects.only('id'),
        empty_label = 'Pilih Client',
        widget = forms.Select(
            attrs = {
                'class':'select validator p-2 mb-4 w-auto'            
            }
        )        
    )
    jumlah = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'jumlah-barang',
                'name':'jumlah-barang',
                'type':'text',
                'placeholder':'Jumlah barang dan satuan',
            }
        )
    )  
    nomor_po = forms.ModelChoiceField(
        queryset = PO.objects.only('nomor_po'),
        empty_label = 'Nomor PO',
        widget = forms.Select(
            attrs = {
                'class':'select validator p-2 mb-4 w-auto'            
            }
        )        
    )
    lampiran_sj = forms.FileField(
        widget = forms.FileInput(
            attrs = {
                'class':'file-input p-2 mb-4 w-auto',
                'id':'lampiran-sj',
                'name':'lampiran-sj',
                'type':'file',
            }
        )
    )
    lampiran_foto = forms.FileField(
        widget = forms.FileInput(
            attrs= {
                'class':'file-input p-2 mb-4 w-auto',
                'id':'lampiran-foto',
                'name':'lampiran-foto',
                'type':'file',
            }
        )
    )

    class Meta:
        model = monitoring_PO
        fields = ['client_id','nomor_po','tanggal','lampiran_sj','lampiran_foto']

class ReportForm(forms.ModelForm):
    tata_letak = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'tata-letak',
                'name':'tata-letak',
                'type':'text',
                'placeholder':'Tata Letak',
                'autocomplete':'tata-letak',
            }
        )
    )        
    nomor_unit = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'nomor-unit',
                'name':'nomor-unit',
                'type':'text',
                'placeholder':'Nomor Unit',
            }
        )
    )        
    total_mapping = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'total-mapping',
                'name':'total-mapping',
                'type':'text',
                'placeholder':'Total Mapping',
            }
        )
    )        
    aktual_mapping = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'aktual-mapping',
                'name':'aktual-mapping',
                'type':'text',
                'placeholder':'Aktual Mapping',
            }
        )
    )        
    tanggal = forms.DateField(
        widget = forms.DateInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'tgl',
                'name':'tgl',
                'type':'date',
            }
        )
    )
    client_id = forms.ModelChoiceField(
        queryset = Project.objects.only('id'),
        label = 'Client:',
        widget = forms.Select(
            attrs = {
                'class':'hidden',
                'data-select':"""{
    "placeholder": "Pilih Client",
    "toggleTag": "<button type=\'button\' aria-expanded=\'false\'></button>",
    "toggleClasses": "p-2 mb-4 max-w-md advance-select-toggle select select-disabled:pointer-events-none select-disabled:opacity-40",
    "hasSearch": true,
    "dropdownClasses": "advance-select-menu max-h-52 pt-0 overflow-y-auto",
    "optionClasses": "advance-select-option selected:select-active",
    "optionTemplate": "<div class=\'flex justify-between items-center w-full\'><span data-title></span></div>"
    }""",
            }
        )
    )
    jenis_pekerjaan = forms.ModelChoiceField(
        queryset = Pekerjaan_mapping.objects.only('jenis_pekerjaan'),
        label = 'Pekerjaan:',
        widget = forms.Select(
            attrs = {
                'class':'hidden',
                'data-select':"""{
    "placeholder": "Pilih Pekerjaan",
    "toggleTag": "<button type=\'button\' aria-expanded=\'false\'></button>",
    "toggleClasses": "p-2 mb-4 max-w-md advance-select-toggle select select-disabled:pointer-events-none select-disabled:opacity-40",
    "hasSearch": true,
    "dropdownClasses": "advance-select-menu max-h-52 pt-0 overflow-y-auto",
    "optionClasses": "advance-select-option selected:select-active",
    "optionTemplate": "<div class=\'flex justify-between items-center w-full\'><span data-title></span></div>"
    }""",
            }
        )
    )

    class Meta:
        model = Mapping_Report
        fields = ['client_id','tata_letak','jenis_pekerjaan','total_mapping','aktual_mapping','tanggal','nomor_unit']

class updateProfileForm(forms.ModelForm):
    username = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                'class':'grow',
                'type':'hidden',
                'id':'username',
                'name':'username',                
            }
        )
    )
    email = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                'class':'grow',
                'type':'email',
                'id':'email',
                'name':'email',                
            }
        )
    )
    first_name = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                'class':'grow',
                'type':'text',
                'id':'first-name',
                'name':'first-name',                
            }
        )
    )
    last_name = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                'class':'grow',
                'type':'text',
                'id':'last-name',
                'name':'last-name',                
            }
        )
    )

    class Meta:
        model = User
        fields = ['username','email','first_name','last_name']

class photoProfileForm(forms.ModelForm):    
    photo = forms.FileField(
        widget = forms.FileInput(
            attrs = {
                'class':'file-input',
                'type':'file',
                'id':'images',
                'name':'images',
                'onChange':'loadFile(event);',
                'accept':'image/*',
            }
        )
    )

    class Meta:
        model = Profile
        fields = ['photo']

class changePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget = forms.PasswordInput(
            attrs = {
                'class':'py-2.5 sm:py-3 ps-4 pe-10 block w-full border-gray-200 rounded-lg sm:text-sm focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400 dark:placeholder-neutral-500 dark:focus:ring-neutral-600',
                'type':'password',
                'id':'old-password',
                'name':'old_password',
            }
        )
    )
    new_password1 = forms.CharField(
        widget = forms.PasswordInput(
            attrs = {
                'class':'py-2.5 sm:py-3 ps-4 pe-10 block w-full border-gray-200 rounded-lg sm:text-sm focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400 dark:placeholder-neutral-500 dark:focus:ring-neutral-600',
                'type':'password',
                'id':'new-password1',
                'name':'new_pass1',
            }
        )
    )
    new_password2 = forms.CharField(
        widget = forms.PasswordInput(
            attrs = {
                'class':'py-2.5 sm:py-3 ps-4 pe-10 block w-full border-gray-200 rounded-lg sm:text-sm focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400 dark:placeholder-neutral-500 dark:focus:ring-neutral-600',
                'type':'password',
                'id':'new-password2',
                'name':'new_pass2',
            }
        )
    )

    class Meta:
        model = User
        fields = ['old_password','new_password1','new_password2']

class pengajuanForm(forms.ModelForm):
    client_id = forms.ModelChoiceField(
        queryset = Project.objects.only('id'),
        label = 'Client:',
        widget = forms.Select(
            attrs = {
                'class':'hidden',
                'data-select':"""{
    "placeholder": "Pilih Client",
    "toggleTag": "<button type=\'button\' aria-expanded=\'false\'></button>",
    "toggleClasses": "p-2 mb-4 max-w-md advance-select-toggle select select-disabled:pointer-events-none select-disabled:opacity-40",
    "hasSearch": true,
    "dropdownClasses": "advance-select-menu max-h-52 pt-0 overflow-y-auto",
    "optionClasses": "advance-select-option selected:select-active",
    "optionTemplate": "<div class=\'flex justify-between items-center w-full\'><span data-title></span></div>"
    }""",
            }
        )
    )    
    nama_barang = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'nama-barang',
                'name':'nama-barang',
                'type':'text',
                'placeholder':'Nama Barang',
            }
        )
    )        
    tanggal = forms.DateField(
        widget = forms.DateInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'tgl',
                'name':'tgl',
                'type':'date',
            }
        )
    )
    jumlah = forms.IntegerField(
        widget = forms.NumberInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'jumlah',
                'name':'jumlah',
                'type':'number',
                'placeholder':'Jumlah Barang',
            }
        )
    )
    satuan = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'satuan',
                'name':'satuan',
                'type':'text',
                'placeholder':'Satuan',
            }
        )
    )

    class Meta:
        model = Pengajuan_Barang
        fields = ['client_id','nama_barang','tanggal','jumlah','satuan']

class barangKeluarForm(forms.ModelForm):
    client_id = forms.ModelChoiceField(
        queryset = Project.objects.only('id'),
        widget = forms.Select(
            attrs = {
                'class':'hidden',
                'data-select':"""{
    "placeholder": "Pilih Client",
    "toggleTag": "<button type=\'button\' aria-expanded=\'false\'></button>",
    "toggleClasses": "p-2 mb-4 max-w-lg advance-select-toggle select select-disabled:pointer-events-none select-disabled:opacity-40",
    "hasSearch": true,
    "dropdownClasses": "advance-select-menu max-h-52 pt-0 overflow-y-auto",
    "optionClasses": "advance-select-option selected:select-active",
    "optionTemplate": "<div class=\'flex justify-between items-center w-full\'><span data-title></span></div>"
    }""",
            }
        )
    )
    stock_opname = forms.ModelChoiceField(
        queryset = Stock_Opname.objects.only('id'),
        widget = forms.Select(
            attrs = {
                'class':'hidden',
                'data-select':"""{
    "placeholder": "Nama Barang",
    "toggleTag": "<button type=\'button\' aria-expanded=\'false\'></button>",
    "toggleClasses": "p-2 mb-4 max-w-lg advance-select-toggle select select-disabled:pointer-events-none select-disabled:opacity-40",
    "hasSearch": true,
    "dropdownClasses": "advance-select-menu max-h-52 pt-0 overflow-y-auto",
    "optionClasses": "advance-select-option selected:select-active",
    "optionTemplate": "<div class=\'flex justify-between items-center w-full\'><span data-title></span></div>"
    }""",
            }
        )
    )     
    jumlah = forms.IntegerField(
        widget = forms.NumberInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'jumlah',
                'name':'jumlah',
                'type':'number',
                'placeholder':'Jumlah Barang',
            }
        )
    )
    satuan = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'satuan',
                'name':'satuan',
                'type':'text',
                'placeholder':'Satuan',
            }
        )
    )
      
    class Meta:
        model = Transaksi_SO
        fields = ['client_id','stock_opname','jumlah','satuan']

class dailyForm(forms.ModelForm):
    client_id = forms.ModelChoiceField(
        queryset = Project.objects.only('id'),
        widget = forms.Select(
            attrs = {
                'class':'hidden',
                'data-select':"""{
    "placeholder": "Pilih Client",
    "toggleTag": "<button type=\'button\' aria-expanded=\'false\'></button>",
    "toggleClasses": "p-2 mb-4 max-w-lg advance-select-toggle select select-disabled:pointer-events-none select-disabled:opacity-40",
    "hasSearch": true,
    "dropdownClasses": "advance-select-menu max-h-52 pt-0 overflow-y-auto",
    "optionClasses": "advance-select-option selected:select-active",
    "optionTemplate": "<div class=\'flex justify-between items-center w-full\'><span data-title></span></div>"
    }""",
            }
        )
    )
    harian = forms.IntegerField(
        widget = forms.NumberInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'harian',
                'name':'harian',
                'type':'number',
                'placeholder':'Harian',
            }
        )
    )
    sipil = forms.IntegerField(
        widget = forms.NumberInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'sipil',
                'name':'sipil',
                'type':'number',
                'placeholder':'Sipil',
            }
        )
    )
    me = forms.IntegerField(
        widget = forms.NumberInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'me',
                'name':'me',
                'type':'number',
                'placeholder':'ME',
            }
        )
    )
    plumbing = forms.IntegerField(
        widget = forms.NumberInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'plumbing',
                'name':'plumbing',
                'type':'number',
                'placeholder':'Plumbing',
            }
        )
    )
    genteng = forms.IntegerField(
        widget = forms.NumberInput(
            attrs = {
                'class':'input validator p-2 mb-4 w-auto',
                'id':'genteng',
                'name':'genteng',
                'type':'number',
                'placeholder':'Genteng',
            }
        )
    )
    lampiran_dokumentasi = forms.FileField(
        widget = forms.FileInput(
            attrs= {
                'class':'file-input p-2 mb-4 w-auto',
                'id':'lampiran-dokumentasi',
                'name':'lampiran-dokumentasi',
                'type':'file',
            }
        )
    )
    lampiran_cuaca = forms.FileField(
        widget = forms.FileInput(
            attrs= {
                'class':'file-input p-2 mb-4 w-auto',
                'id':'lampiran-cuaca',
                'name':'lampiran-cuaca',
                'type':'file',
            }
        )
    )

    class Meta:
        model = Daily_Report
        fields = '__all__'

class penagihanForm(forms.ModelForm):
    client_id = forms.ModelChoiceField(
        queryset = Project.objects.only('id'),
        widget = forms.Select(
            attrs = {
                'class':'hidden',
                'data-select':"""{
    "placeholder": "Pilih Client",
    "toggleTag": "<button type=\'button\' aria-expanded=\'false\'></button>",
    "toggleClasses": "p-2 mb-4 max-w-lg advance-select-toggle select select-disabled:pointer-events-none select-disabled:opacity-40",
    "hasSearch": true,
    "dropdownClasses": "advance-select-menu max-h-52 pt-0 overflow-y-auto",
    "optionClasses": "advance-select-option selected:select-active",
    "optionTemplate": "<div class=\'flex justify-between items-center w-full\'><span data-title></span></div>"
    }""",
            }
        )
    )   
    lampiran_dokumentasi = forms.FileField(
        widget = forms.FileInput(
            attrs= {
                'class':'file-input p-2 mb-4 w-auto',
                'id':'lampiran-dokumentasi',
                'name':'lampiran-dokumentasi',
                'type':'file',
            }
        )
    )
    lampiran_lpp = forms.FileField(
        widget = forms.FileInput(
            attrs= {
                'class':'file-input p-2 mb-4 w-auto',
                'id':'lampiran-lpp',
                'name':'lampiran-lpp',
                'type':'file',
            }
        )
    )         
    lampiran_lokasi = forms.FileField(
        widget = forms.FileInput(
            attrs= {
                'class':'file-input p-2 mb-4 w-auto',
                'id':'lampiran-lokasi',
                'name':'lampiran-lokasi',
                'type':'file',
            }
        )
    )         
    lampiran_mapping = forms.FileField(
        widget = forms.FileInput(
            attrs= {
                'class':'file-input p-2 mb-4 w-auto',
                'id':'lampiran-mapping',
                'name':'lampiran-mapping',
                'type':'file',
            }
        )
    )         
    lampiran_monitoring = forms.FileField(
        widget = forms.FileInput(
            attrs= {
                'class':'file-input p-2 mb-4 w-auto',
                'id':'lampiran-monitoring',
                'name':'lampiran-monitoring',
                'type':'file',
            }
        )
    )    

    class Meta:
        model = Penagihan
        fields = '__all__'     