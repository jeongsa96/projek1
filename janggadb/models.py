from django.db import models
from django.contrib.auth.models import AbstractUser
from pathlib import Path

# create model here

class User(AbstractUser):
    is_admin = models.BooleanField('Is Admin', default=False)
    is_projectManager = models.BooleanField('Is Project Manager', default=False)
    is_logistik = models.BooleanField('Is Logistik', default=False)
    is_finance = models.BooleanField('Is Finance', default=False)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(default='default.jpg', upload_to='photo_profile/')

    def __str__(self):
        return f'{self.user.username} Profile'

class Project(models.Model):
    client = models.CharField(max_length=100)
    lokasi = models.CharField(max_length=100)
    jenis_projek = models.CharField(max_length=100)
    SPK = models.CharField(max_length=100)

    def __str__(self):
        return self.client 

class Invoice(models.Model):
    status_invoice = [
        ('belum lunas', 'Belum Lunas'), 
        ('lunas', 'Lunas'),
    ]

    nomor_invoice = models.CharField(max_length=50)
    nomor_po = models.CharField(max_length=50, null=False)
    tanggal_invoice = models.DateField(null=False)
    tanggal_jatuh_tempo = models.DateField(null=False)
    jumlah_tagihan = models.BigIntegerField(null=True)
    status = models.CharField(choices=status_invoice, default='Belum Lunas', null=True)
    lampiran = models.FileField(upload_to='invoice/', blank=True)
    client_id = models.ForeignKey(Project, null=False, on_delete=models.CASCADE)

    def get_filename(self):
        return Path(self.lampiran.name).name
    
class PO(models.Model):
    status_po = [
        ('menunggu persetujuan', 'Menunggu Persetujuan'),
        ('disetujui', 'Disetujui'),
        ('telah dikirim', 'Telah Dikirim'),
        ('barang sampai', 'Barang Sampai'),
    ]
    tipe_po = [
        ('struktur', 'Struktur'),
        ('arsitektur', 'Arsitektur'),
        ('MEP', 'MEP'),
    ]

    vendor = models.CharField(max_length=100)
    nomor_po = models.CharField(max_length=100)
    tanggal_po = models.DateField(null=False)
    deskripsi_barang = models.TextField(max_length=100)
    kuantitas = models.BigIntegerField(null=False)
    harga_satuan = models.BigIntegerField(null=False)
    total = models.BigIntegerField(null=False)
    status = models.CharField(choices=status_po, default='Menunggu Persetujuan', null=True)
    tipe = models.CharField(choices=tipe_po, null=True)
    client_id = models.ForeignKey(Project, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.nomor_po 

class Jenis_Anggaran(models.Model):
    jenis_anggaran= models.CharField(max_length=100, null = False)

    def __str__(self):
        return self.jenis_anggaran 

class Anggaran(models.Model):
    jenis_anggaran = models.ForeignKey(Jenis_Anggaran, on_delete=models.CASCADE, null = True)
    deskripsi = models.TextField(null = True)
    total_anggaran = models.BigIntegerField(null = False)
    client_id = models.ForeignKey(Project, null=False, on_delete=models.CASCADE)

class data_Expense(models.Model):
    jenis_anggaran = models.ForeignKey(Jenis_Anggaran, on_delete=models.CASCADE, null = True)
    tanggal = models.DateField(null = False)
    total = models.BigIntegerField(null = False)
    client_id = models.ForeignKey(Project, null=False, on_delete=models.CASCADE)
    anggaran_id = models.ForeignKey(Anggaran, null=False, on_delete=models.CASCADE)

class monitoring_PO(models.Model):
    client_id = models.ForeignKey(Project, null=False, on_delete=models.CASCADE)
    nomor_po = models.ForeignKey(PO, null=False, on_delete=models.CASCADE)
    tanggal = models.DateField(null=False)
    lampiran_sj = models.FileField(upload_to='monitoring/', blank=True)
    lampiran_foto = models.FileField(upload_to='monitoring/', blank=True)

class Pekerjaan_mapping(models.Model):
    jenis_pekerjaan = models.CharField(max_length=100) 

    def __str__(self):
        return self.jenis_pekerjaan       

class Mapping_Report(models.Model):
    client_id = models.ForeignKey(Project, null=False, on_delete=models.CASCADE)
    tata_letak = models.CharField(max_length=50)
    jenis_pekerjaan = models.ForeignKey(Pekerjaan_mapping, null=False ,on_delete=models.CASCADE)
    total_mapping = models.IntegerField(null=False)
    aktual_mapping = models.IntegerField(null=False)
    tanggal = models.DateField(null=False)
