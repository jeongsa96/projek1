from django.db import models
from django.contrib.auth.models import AbstractUser
from pathlib import Path

# create model here

class User(AbstractUser):
    is_admin = models.BooleanField('Is Admin', default=False)
    is_projectManager = models.BooleanField('Is Project Manager', default=False)
    is_logistik = models.BooleanField('Is Logistik', default=False)
    is_finance = models.BooleanField('Is Finance', default=False)

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
    tanggal_invoice = models.DateField(null=False)
    tanggal_jatuh_tempo = models.DateField(null=False)
    jumlah_tagihan = models.IntegerField(null=True)
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

    vendor = models.CharField(max_length=50)
    nomor_po = models.CharField(max_length=50)
    tanggal_po = models.DateField(null=False)
    deskripsi_barang = models.TextField(max_length=100)
    kuantitas = models.IntegerField(null=False)
    harga_satuan = models.IntegerField(null=False)
    total = models.IntegerField(null=False)
    status = models.CharField(choices=status_po, default='Menunggu Persetujuan', null=True)
    tipe = models.CharField(choices=tipe_po, null=True)
    client_id = models.ForeignKey(Project, null=False, on_delete=models.CASCADE)
