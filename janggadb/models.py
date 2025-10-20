from django.db import models
from django.contrib.auth.models import AbstractUser
from pathlib import Path

# create model here

class User(AbstractUser):
    is_admin = models.BooleanField('Is Admin', default=False)
    is_projectManager = models.BooleanField('Is Project Manager', default=False)
    is_logistik = models.BooleanField('Is Logistik', default=False)
    is_finance = models.BooleanField('Is Finance', default=False)
    is_client = models.BooleanField('Is Client', default=False)

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
    client_id = models.ForeignKey(Project, null=False, on_delete=models.CASCADE, related_name='invoices')
    uploaded_at = models.DateTimeField(auto_now_add=True)

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
    satuan = models.CharField(max_length=20, default="Kilo")
    harga_satuan = models.BigIntegerField(null=False)
    total = models.BigIntegerField(null=False)
    status = models.CharField(choices=status_po, default='Menunggu Persetujuan', null=True)
    tipe = models.CharField(choices=tipe_po, null=True)
    client_id = models.ForeignKey(Project, null=False, on_delete=models.CASCADE, related_name="pos")

    def __str__(self):
        return self.nomor_po 

class Jenis_Anggaran(models.Model):
    nama_jenis = models.CharField(max_length=100, null = False)

    def __str__(self):
        return self.nama_jenis

class Anggaran(models.Model):
    jenis_anggaran = models.ForeignKey(Jenis_Anggaran, on_delete=models.CASCADE, null = True)
    deskripsi = models.TextField(null = True)
    total_anggaran = models.BigIntegerField(null = False)
    sisa_anggaran = models.BigIntegerField(null = False)
    client_id = models.ForeignKey(Project, null=False, on_delete=models.CASCADE)

class data_Expense(models.Model):
    jenis_anggaran = models.ForeignKey(Jenis_Anggaran, on_delete=models.CASCADE, null = True)
    tanggal = models.DateField(null = False)
    total = models.BigIntegerField(null = False)
    client_id = models.ForeignKey(Project, null=False, on_delete=models.CASCADE)
    anggaran_id = models.ForeignKey(Anggaran, null=False, on_delete=models.CASCADE)
    sisa_budget = models.BigIntegerField(null = False)

class monitoring_PO(models.Model):
    client_id = models.ForeignKey(Project, null=False, on_delete=models.CASCADE)
    nomor_po = models.ForeignKey(PO, null=False, on_delete=models.CASCADE)
    jumlah = models.CharField(max_length=100, default="10 kilo")
    tanggal = models.DateField(null=False)
    lampiran_sj = models.FileField(upload_to='monitoring/sj', blank=True)
    lampiran_foto = models.FileField(upload_to='monitoring/dokumentasi', blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Pekerjaan_mapping(models.Model):
    jenis_pekerjaan = models.CharField(max_length=100) 
    fase = models.CharField(null = True)

    def __str__(self):
        return self.jenis_pekerjaan       

class Mapping_Report(models.Model):
    client_id = models.ForeignKey(Project, null=False, on_delete=models.CASCADE)
    tata_letak = models.CharField(max_length=50)
    nomor_unit = models.CharField(max_length=20, null=False)
    jenis_pekerjaan = models.ForeignKey(Pekerjaan_mapping, null=False ,on_delete=models.CASCADE)                                
    total_mapping = models.IntegerField(null=False)                                                                             
    aktual_mapping = models.IntegerField(null=False)
    tanggal = models.DateField(null=False)

class Pengajuan_Barang(models.Model):
    client_id = models.ForeignKey(Project, null=False, on_delete=models.CASCADE)
    nama_barang = models.CharField(max_length=100)
    jumlah = models.IntegerField(null=False)
    satuan = models.CharField(max_length=20)
    tanggal = models.DateField(null=False)

class Stock_Opname(models.Model):
    client_id = models.ForeignKey(Project, null=False, on_delete=models.CASCADE)
    nama_barang = models.CharField(max_length=100)
    jumlah = models.IntegerField(null=False)
    satuan = models.CharField(max_length=20)
    sisa_barang = models.IntegerField(null=False, default=0)
    persentase = models.DecimalField(max_digits=5, decimal_places=2, null=False, default=0)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.nama_barang

    def save(self, *args, **kwargs):
        self.persentase = float(self.sisa_barang) / float(self.jumlah)
        super().save(*args, **kwargs)     

class Transaksi_SO(models.Model):    
    client_id = models.ForeignKey(Project, null=False, on_delete=models.CASCADE)
    stock_opname = models.ForeignKey(Stock_Opname, null=False, on_delete=models.CASCADE)
    tanggal_transaksi = models.DateTimeField(auto_now_add=True)
    jumlah = models.IntegerField(null=False)
    satuan = models.CharField(max_length=20)

class Daily_Report(models.Model):
    client_id = models.ForeignKey(Project, null=False, on_delete=models.CASCADE)
    tampak = models.IntegerField(null=False)
    me = models.IntegerField(null=False)
    sipil = models.IntegerField(null=False)
    plumbing = models.IntegerField(null=False)
    genteng = models.IntegerField(null=False)
    lampiran_cuaca = models.FileField(upload_to='daily/', blank=True)
    lampiran_dokumentasi = models.FileField(upload_to='daily/', blank=True)
    
class Penagihan(models.Model):
    client_id = models.ForeignKey(Project, null=False, on_delete=models.CASCADE)
    lampiran_lpp = models.FileField(upload_to='penagihan/lpp/', blank=True)
    lampiran_dokumentasi = models.FileField(upload_to='penagihan/dokumentasi/', blank=True)
    lampiran_lokasi = models.FileField(upload_to='penagihan/lokasi/', blank=True)
    lampiran_mapping = models.FileField(upload_to='penagihan/mapping/', blank=True)
    lampiran_monitoring = models.FileField(upload_to='penagihan/monitoring/', blank=True)

    