from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.http import StreamingHttpResponse
from .forms import LoginForm, RegisterForm, ProjekForm, InvoiceForm, POform, AnggaranForm, MonitoringForm, ReportForm, updateProfileForm, photoProfileForm, changePasswordForm, pengajuanForm, barangKeluarForm, dailyForm, penagihanForm, breakdownForm
from .models import *
import cv2
import threading
from django.contrib import messages
from django.http import JsonResponse
import pandas as pd
import numpy as np
from sqlalchemy import create_engine


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()
            messages.success(request, 'akun telah dibuat, tunggu konfirmasi admin!')
            return redirect('index')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = RegisterForm()

    context = {'form': form}        
    return render(request,'register.html', context)

def index(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                request.session['username'] = user.username

                role_map = {
                    'is_adminProject': 'admin-jangga',
                    'is_projectManager': 'project-manager',
                    'is_management': 'management',
                    'is_logistik': 'logistik',
                    'is_client': 'client',
                }

                for role, url in role_map.items():
                    if getattr(user, role):
                        request.session['url'] = url
                        return redirect(reverse(url))

                messages.error(request, 'akses tidak valid')
            else:
                messages.error(request, 'username atau password salah')
        else:
            messages.error(request, 'input anda salah')
    else:
        form = LoginForm()

    context = {'form': form}        
    return render(request, 'login.html', context)
 
def Change_Password(request):
    if request.method == 'POST':
        form = changePasswordForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Password anda berhasil diganti')
            return redirect('change-password')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = changePasswordForm(user=request.user)

    context = {'form':form}
    return render(request, 'auth/ganti-password.html', context)                 
    
    

@login_required
def Profil(request, pk):
    user = User.objects.get(pk=pk)
    profile = Profile.objects.get(user__id=pk)
    if request.method == 'POST':
        user_form = updateProfileForm(request.POST, request.FILES, instance=user)
        photo_form = photoProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and photo_form.is_valid():
            user_form.save()
            photo_form.save()
            messages.success(request, 'Profil anda telah diupdate ')
            return redirect('edit-profil', pk=user.id)
        else:
            messages.error(request, 'Input anda salah')
    else:
        user_form = updateProfileForm(instance=user)  
        photo_form = photoProfileForm(instance=profile)

    context = {'user_form':user_form,'photo_form':photo_form}                
    return render(request, 'auth/edit-profile.html', context)

@login_required
def Admin(request):   
    user = request.user
    if user.is_authenticated and user.is_adminProject:
        import plotly.express as px
        if request.method == 'POST':
            pro = request.POST['client']
            engine = create_engine('postgresql+psycopg2://admin:admin@localhost:5432/jangga_db')
            query = """SELECT jpm.jenis_pekerjaan, jpm.fase, jmr.nomor_unit, jmr.aktual_mapping as Hari_Ini, jmr.total_mapping as Max, jmr.tanggal FROM janggadb_mapping_report as jmr CROSS JOIN janggadb_pekerjaan_mapping as jpm WHERE jmr.jenis_pekerjaan_id = jpm.id AND client_id_id = """+pro+""" AND tanggal = (SELECT MAX(tanggal) FROM janggadb_mapping_report)"""
            query2 = """SELECT jpm.jenis_pekerjaan, jpm.fase, jmr.nomor_unit, jmr.aktual_mapping as kemarin from janggadb_mapping_report as jmr CROSS JOIN janggadb_pekerjaan_mapping as jpm WHERE jmr.jenis_pekerjaan_id = jpm.id AND client_id_id = """+pro+""" AND tanggal = (SELECT MAX(tanggal) FROM janggadb_mapping_report) - INTERVAL '1 day'"""
            
            df = pd.read_sql_query(query,engine)
            df2 = pd.read_sql_query(query2,engine)
            res = pd.merge(df,df2, on=["jenis_pekerjaan","nomor_unit"])
            res['total'] = res['hari_ini'] + res['kemarin']            

            res["persentase"] = res["total"] / res["max"] * 100 

            average_persentase = round(res["persentase"].mean(), 2)
            total_count = (res['total'] == 19).sum()

            res['progres'] = np.where(res['total'] == res['max'], 1, 0)

            res_summary = (res[res["progres"] == 1]
                            .groupby(["nomor_unit", "jenis_pekerjaan"], as_index=False)
                            .size()
                            .rename(columns={"size": "count"}))

            all_units = pd.DataFrame({'nomor_unit': sorted(res['nomor_unit'].unique())})
            res_summary = (
                all_units
                .merge(res_summary, on="nomor_unit", how="left")
                .fillna({'count': 0, 'jenis_pekerjaan': 'Belum Ada Progres'})
            )

            # Convert count to int (for better display)
            res_summary["count"] = res_summary["count"].astype(int)                            

            fig = px.bar(
                res_summary,
                x="nomor_unit",
                y="count",
                color="jenis_pekerjaan",
                text="jenis_pekerjaan",
                barmode="stack",
                title="Progress per Unit"
            )

            fig.update_xaxes(
                tickmode="linear",
                dtick=1,
                categoryarray=res_summary["nomor_unit"].tolist()
            )

            fig.update_yaxes(dtick=1, tickmode="linear", tickformat="d")

            fig.update_layout(
                xaxis_title="Nomor Unit",
                yaxis_title="Progress Count",
                paper_bgcolor="lightgray"
            )

            diagram = fig.to_html()
            
            projek = Project.objects.only('client')
            context = {'user':user,'rata':average_persentase,'total':total_count,'diagram':diagram,'projek':projek}
            return render(request,'admin/dashboard.html', context)

        else:    
            projek = Project.objects.only('client')
            import plotly.express as px

            engine = create_engine('postgresql+psycopg2://admin:admin@localhost:5432/jangga_db')
            
            query = """SELECT jpm.jenis_pekerjaan, jpm.fase, jmr.nomor_unit, jmr.aktual_mapping as Hari_Ini, jmr.total_mapping as Max, jmr.tanggal FROM janggadb_mapping_report as jmr CROSS JOIN janggadb_pekerjaan_mapping as jpm WHERE jmr.jenis_pekerjaan_id = jpm.id AND tata_letak = 'XYZ CHARM 18' AND tanggal = (SELECT MAX(tanggal) FROM janggadb_mapping_report)"""
            query2 = """SELECT jpm.jenis_pekerjaan, jpm.fase, jmr.nomor_unit, jmr.aktual_mapping as kemarin FROM janggadb_mapping_report as jmr CROSS JOIN janggadb_pekerjaan_mapping as jpm WHERE jmr.jenis_pekerjaan_id = jpm.id AND tata_letak = 'XYZ CHARM 18' AND tanggal = (SELECT tanggal FROM janggadb_mapping_report ORDER BY tanggal ASC LIMIT 1 OFFSET 1)"""

            df = pd.read_sql_query(query,engine)
            df2 = pd.read_sql_query(query2,engine)
            res = pd.merge(df,df2, on=["jenis_pekerjaan","nomor_unit"])
            res['total'] = res['hari_ini'] + res['kemarin']            

            res["persentase"] = res["total"] / res["max"] * 100 

            average_persentase = round(res["persentase"].mean(), 2)
            total_count = (res['total'] == 19).sum()

            res['progres'] = np.where(res['total'] == res['max'], 1, 0)

            res_summary = (res[res["progres"] == 1]
                            .groupby(["nomor_unit", "jenis_pekerjaan"], as_index=False)
                            .size()
                            .rename(columns={"size": "count"}))

            all_units = pd.DataFrame({'nomor_unit': sorted(res['nomor_unit'].unique())})
            res_summary = (
                all_units
                .merge(res_summary, on="nomor_unit", how="left")
                .fillna({'count': 0, 'jenis_pekerjaan': 'Belum Ada Progres'})
            )

            # Convert count to int (for better display)
            res_summary["count"] = res_summary["count"].astype(int)                            

            fig = px.bar(
                res_summary,
                x="nomor_unit",
                y="count",
                color="jenis_pekerjaan",
                text="jenis_pekerjaan",
                barmode="stack",
                title="Progress per Unit"
            )

            fig.update_xaxes(
                tickmode="linear",
                dtick=1,
                categoryarray=res_summary["nomor_unit"].tolist()
            )

            fig.update_yaxes(dtick=1, tickmode="linear", tickformat="d")

            fig.update_layout(
                xaxis_title="Nomor Unit",
                yaxis_title="Progress Count",
                paper_bgcolor="lightgray"
            )

            diagram = fig.to_html()
            
            context = {'user':user,'rata':average_persentase,'total':total_count,'diagram':diagram,'projek':projek}
            return render(request,'admin/dashboard.html', context)
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')

@login_required
def Admin_PD(request):
    user = request.user
    if user.is_authenticated and user.is_adminProject:
        projek_client = Project.objects.only("client")
        if request.method == 'POST':
            projek_form = request.POST['pilih']
            projek = get_object_or_404(Project, pk=projek_form)
            invoices = projek.invoices.all()
            all_files = []
            # Add invoices to the file list
            for invoice in invoices:
                if invoice.lampiran:
                    all_files.append({
                        'file': f"Invoice: {invoice.nomor_invoice}",
                        'file_url': invoice.lampiran.url,
                        'file_name': invoice.get_filename,
                        'client': invoice.client_id,
                        'tanggal_terbit': invoice.tanggal_invoice,
                        'tanggal_jatuh_tempo': invoice.tanggal_jatuh_tempo,
                    })

            context = {'projek':projek_client, 'files':all_files}
            return render(request, 'admin/projek-db.html', context)
        else: 
            context = {'projek':projek_client}
            return render(request, 'admin/projek-db.html', context)
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')           

@login_required
def Admin_MR(request):
    user = request.user
    if user.is_authenticated and user.is_adminProject:
        if request.method == 'POST':
            form = ReportForm(request.POST)
            if form.is_valid():
                map = form.save()
                messages.success(request, 'Mapping Report telah disimpan')
                return redirect('admin-mapping-report')
        else:
            form = ReportForm()

        context = {'form':form}
        return render(request, 'admin/input-mapping.html', context) 
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')       
        
@login_required
def Admin_DR(request):
    user = request.user
    if user.is_authenticated and user.is_adminProject:
        if request.method == 'POST':
            form = dailyForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Daily Report telah disimpan')
                return redirect('admin-daily-report')
        else:
            form = dailyForm()

        context = {'form':form}
        return render(request, 'admin/daily-report.html', context) 
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')

@login_required
def Admin_P(request):
    user = request.user
    if user.is_authenticated and user.is_adminProject:
        if request.method == 'POST':
            form = penagihanForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Data Penagihan telah disimpan')
                return redirect('admin-penagihan')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
        else:
            form = penagihanForm()

        context = {'form':form}
        return render(request, 'admin/penagihan.html', context) 
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')

@login_required
def Project_Manager(request):
    user = request.user
    if user.is_authenticated and user.is_projectManager:
        import plotly.express as px
        if request.method == 'POST':
            pro = request.POST['client']
            engine = create_engine('postgresql+psycopg2://admin:admin@localhost:5432/jangga_db')
            query = """SELECT jpm.jenis_pekerjaan, jpm.fase, jmr.nomor_unit, jmr.aktual_mapping as Hari_Ini, jmr.total_mapping as Max, jmr.tanggal FROM janggadb_mapping_report as jmr CROSS JOIN janggadb_pekerjaan_mapping as jpm WHERE jmr.jenis_pekerjaan_id = jpm.id AND client_id_id = """+pro+""" AND tanggal = (SELECT MAX(tanggal) FROM janggadb_mapping_report)"""
            query2 = """SELECT jpm.jenis_pekerjaan, jpm.fase, jmr.nomor_unit, jmr.aktual_mapping as kemarin from janggadb_mapping_report as jmr CROSS JOIN janggadb_pekerjaan_mapping as jpm WHERE jmr.jenis_pekerjaan_id = jpm.id AND client_id_id = """+pro+""" AND tanggal = (SELECT MAX(tanggal) FROM janggadb_mapping_report) - INTERVAL '1 day'"""
            
            df = pd.read_sql_query(query,engine)
            df2 = pd.read_sql_query(query2,engine)
            res = pd.merge(df,df2, on=["jenis_pekerjaan","nomor_unit"])
            res['total'] = res['hari_ini'] + res['kemarin']            

            res["persentase"] = res["total"] / res["max"] * 100 

            average_persentase = round(res["persentase"].mean(), 2)
            total_count = (res['total'] == 19).sum()

            res['progres'] = np.where(res['total'] == res['max'], 1, 0)

            res_summary = (res[res["progres"] == 1]
                            .groupby(["nomor_unit", "jenis_pekerjaan"], as_index=False)
                            .size()
                            .rename(columns={"size": "count"}))

            all_units = pd.DataFrame({'nomor_unit': sorted(res['nomor_unit'].unique())})
            res_summary = (
                all_units
                .merge(res_summary, on="nomor_unit", how="left")
                .fillna({'count': 0, 'jenis_pekerjaan': 'Belum Ada Progres'})
            )

            # Convert count to int (for better display)
            res_summary["count"] = res_summary["count"].astype(int)                            

            fig = px.bar(
                res_summary,
                x="nomor_unit",
                y="count",
                color="jenis_pekerjaan",
                text="jenis_pekerjaan",
                barmode="stack",
                title="Progress per Unit"
            )

            fig.update_xaxes(
                tickmode="linear",
                dtick=1,
                categoryarray=res_summary["nomor_unit"].tolist()
            )
            fig.update_yaxes(dtick=1, tickmode="linear", tickformat="d")

            fig.update_layout(
                xaxis_title="Nomor Unit",
                yaxis_title="Progress Count",
                paper_bgcolor="lightgray"
            )

            diagram = fig.to_html()

            projek = Project.objects.only('client')
            context = {'rata':average_persentase,'total':total_count,'diagram':diagram,'projek':projek}
            return render(request,'pm/dashboard.html', context)

        else:        
            projek = Project.objects.only('client')
            import plotly.express as px

            engine = create_engine('postgresql+psycopg2://admin:admin@localhost:5432/jangga_db')
            
            query = """SELECT jpm.jenis_pekerjaan, jpm.fase, jmr.nomor_unit, jmr.aktual_mapping as Hari_Ini, jmr.total_mapping as Max, jmr.tanggal FROM janggadb_mapping_report as jmr CROSS JOIN janggadb_pekerjaan_mapping as jpm WHERE jmr.jenis_pekerjaan_id = jpm.id AND tata_letak = 'XYZ CHARM 18' AND tanggal = (SELECT MAX(tanggal) FROM janggadb_mapping_report)"""
            query2 = """SELECT jpm.jenis_pekerjaan, jpm.fase, jmr.nomor_unit, jmr.aktual_mapping as kemarin FROM janggadb_mapping_report as jmr CROSS JOIN janggadb_pekerjaan_mapping as jpm WHERE jmr.jenis_pekerjaan_id = jpm.id AND tata_letak = 'XYZ CHARM 18' AND tanggal = (SELECT tanggal FROM janggadb_mapping_report ORDER BY tanggal ASC LIMIT 1 OFFSET 1)"""

            df = pd.read_sql_query(query,engine)
            df2 = pd.read_sql_query(query2,engine)
            res = pd.merge(df,df2, on=["jenis_pekerjaan","nomor_unit"])
            res['total'] = res['hari_ini'] + res['kemarin']            

            res["persentase"] = res["total"] / res["max"] * 100 

            average_persentase = round(res["persentase"].mean(), 2)
            total_count = (res['total'] == 19).sum()

            res['progres'] = np.where(res['total'] == res['max'], 1, 0)

            res_summary = (res[res["progres"] == 1]
                            .groupby(["nomor_unit", "jenis_pekerjaan"], as_index=False)
                            .size()
                            .rename(columns={"size": "count"}))

            all_units = pd.DataFrame({'nomor_unit': sorted(res['nomor_unit'].unique())})
            res_summary = (
                all_units
                .merge(res_summary, on="nomor_unit", how="left")
                .fillna({'count': 0, 'jenis_pekerjaan': 'Belum Ada Progress'})
            )

            # Convert count to int (for better display)
            res_summary["count"] = res_summary["count"].astype(int)                            

            fig = px.bar(
                res_summary,
                x="nomor_unit",
                y="count",
                color="jenis_pekerjaan",
                text="jenis_pekerjaan",
                barmode="stack",
                title="Progress per Unit"
            )

            fig.update_xaxes(
                tickmode="linear",
                dtick=1,
                categoryarray=res_summary["nomor_unit"].tolist()
            )

            fig.update_yaxes(dtick=1, tickmode="linear", tickformat="d")

            fig.update_layout(
                xaxis_title="Nomor Unit",
                yaxis_title="Progress Count",
                paper_bgcolor="lightgray"
            )

            diagram = fig.to_html()

            context = {'rata':average_persentase,'total':total_count,'diagram':diagram,'projek':projek}
            return render(request,'pm/dashboard.html', context)
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')  
    
@login_required
def Project_Manager_PR(request):
    user = request.user
    if user.is_authenticated and user.is_projectManager:
        projek = Project.objects.only('client')
        if request.method == 'POST':
            client = request.POST['pilihan']
            client_po = PO.objects.filter(client_id=client)
            context = {'projek':projek,'client_po':client_po}
            return render(request, 'pm/po-request.html', context)
        
        context = {'projek':projek}
        return render(request, 'pm/po-request.html', context)
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')                 

def Project_Manager_updateStatus(request, id=id):
    status = request.POST['status']
    PO.objects.filter(nomor_po=id).update(status=status)
    messages.success(request, 'status telah diupdate')
    return redirect('pm-po-request')

@login_required
def Project_Manager_PD(request):
    user = request.user
    if user.is_authenticated and user.is_projectManager:
        projek = Project.objects.only("client")
        if request.method == 'POST':
            client = request.POST['pilihan']
            cdb = Project.objects.raw("SELECT * FROM janggadb_project WHERE client= %s", [client])
            context = {'projek':projek, 'client':cdb}
            return render(request, 'pm/projek-db.html', context)
        else:
            context = {'projek':projek}
            return render(request, 'pm/projek-db.html', context)
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index') 

@login_required
def Logistik(request):
    user = request.user
    if user.is_authenticated and user.is_logistik:
        projek = Project.objects.filter(pk=3).only('id')
        status = PO.objects.filter(client_id=3).exclude(status='barang sampai')

        opname = Stock_Opname.objects.filter(client_id=3).order_by('persentase')
        for o in opname:
            o.persen = round(o.persentase*100)
        paginator = Paginator(opname, 3)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context = {'page_obj':page_obj, 'status':status,'projek':projek}
        return render(request, 'logistik/dashboard.html', context)
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')

def Logistik_updateStatus(request, id=id):
    update = request.POST['status']
    client_id = request.POST['clients']
    client_obj = Project.objects.get(id=client_id)
    barang = request.POST['deskripsi']
    jumlah = request.POST['jumlah']
    sisa = request.POST['jumlah-barang']
    satuan = request.POST['satuan']
    PO.objects.filter(nomor_po=id).update(status=update)
    Stock_Opname.objects.update_or_create(nama_barang=barang, defaults={'client_id':client_obj, 'jumlah':jumlah, 'sisa_barang':sisa, 'satuan':satuan})

    return redirect('logistik-monitoring-po')                 

@login_required
def Logistik_Status(request):
    user = request.user
    if user.is_authenticated and user.is_logistik:
        projek = Project.objects.only("client")
        if request.method == 'POST':
            client = request.POST['pilihan']
            status = PO.objects.raw("SELECT * FROM janggadb_po WHERE client_id_id = %s", [client])

            context = {'status':status,'projek':projek}
            return render(request,'logistik/status-po.html', context)
        else:
            return render(request,'logistik/status-po.html',{'projek':projek})      
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')    

@login_required
def Logistik_Monitoring(request):
    user = request.user
    if user.is_authenticated and user.is_logistik:
        projek = Project.objects.only("client")
        if request.method == 'POST':
            monitor = MonitoringForm(request.POST, request.FILES)
            if monitor.is_valid():
                form = monitor.save()
                messages.success(request, 'Data monitoring berhasil disimpan')
                return redirect('logistik-monitoring-po')
            else:
                messages.error(request, 'data input salah')
        else:
            form = MonitoringForm()

            context = {'projek':projek,'form':form}
            return render(request,'logistik/monitoring-po.html', context)   
    else:             
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index') 
    
@login_required
def Logistik_PB(request):
    user = request.user
    if user.is_authenticated and user.is_logistik:
        projek = Project.objects.only("client")
        if request.method == 'POST':
            form = pengajuanForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Pengajuan berhasil')
                return redirect('logistik-pengajuan')
            else:
                messages.error(request, 'data input salah')
        else:
            form = pengajuanForm()

            context = {'projek':projek,'form':form}  
            return render(request, 'logistik/pengajuan-barang.html', context)          
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index') 

@login_required
def Logistik_SO(request):
    user = request.user 
    if user.is_authenticated and user.is_logistik:
        projek = Project.objects.only('id')
        form = barangKeluarForm()
        if request.method == 'POST':   
            if 'submitProjek' in request.POST:
                pilihan = request.POST['pilih']
                stock = Stock_Opname.objects.filter(client_id=pilihan).order_by('persentase')
                transaksi = Transaksi_SO.objects.filter(client_id=pilihan)
                for s in stock:
                    s.persen = round(s.persentase*100)

            if 'submitKeluar' in request.POST:
                form = barangKeluarForm(request.POST)
                if form.is_valid():
                    form.save()
                    nama_projek = request.POST['client_id']
                    id_opname = request.POST['stock_opname']
                    stock_obj = Stock_Opname.objects.get(client_id=nama_projek,id=id_opname)
                    stock_jml = stock_obj.sisa_barang
                    jumlah = request.POST['jumlah']
                    stock_sisa = stock_jml - int(jumlah)
                    stock_obj.sisa_barang = stock_sisa
                    stock_obj.save()
                    
                    messages.success(request, "Input data berhasil")
                    return redirect('logistik-so')
                
            context = {'projek':projek,'stock':stock,'form':form,'transaksi':transaksi}
            return render(request, 'logistik/stock-opname.html', context)
        else:
            context = {'projek':projek,'form':form}
            return render(request, 'logistik/stock-opname.html', context)             
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')       
        

@login_required
def Management(request):
    user = request.user
    if user.is_authenticated and user.is_management:
        return render(request,'finance/dashboard.html')
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index') 

@login_required        
def Management_PB(request):
    user = request.user
    if user.is_authenticated and user.is_management:
        if request.method == 'POST':
            form = ProjekForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Data projek baru berhasil disimpan')
                return redirect('management-projek-baru')
            else:
                messages.error(request, 'data input salah')
        else:
            form = ProjekForm()

            context = {'form':form,}
            return render(request,'finance/projek-baru.html', context)
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')         
    
@login_required        
def Management_A(request):
    user = request.user
    if user.is_authenticated and user.is_management:
        if request.method == 'POST':
            anggaran = AnggaranForm(request.POST)
            if anggaran.is_valid():
                form = anggaran.save()
                messages.success(request, 'Data anggaran berhasil disimpan')
                return redirect('management-anggaran')
            else:
                messages.error(request, 'data anggaran salah')
        else:
            form = AnggaranForm()

            context = {'form':form,}
            return render(request,'finance/anggaran.html', context)
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')        

@login_required
def Management_AC(request):
    user = request.user
    if user.is_authenticated and user.is_management:
        client = Project.objects.only("client")
        if request.method == 'POST':
            client_input = request.POST['client']
            expense = data_Expense.objects.select_related('anggaran_id').values(
            'anggaran_id__jenis_anggaran',
            'anggaran_id__client_id',
            'anggaran_id__deskripsi',
            'anggaran_id__sisa_anggaran',
            'anggaran_id__total_anggaran',
            'tanggal',
            'total')

            context = {'client':client,'expense':expense}
            return render(request, 'finance/cek-anggaran.html', context)
        else:
            context = {'client':client}
            return render(request,'finance/cek-anggaran.html',context)
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')  

@login_required
def Management_E(request):
    user = request.user
    if user.is_authenticated and user.is_management:
        client = Project.objects.only("client")
        if request.method == 'POST':
            if 'inputClient' in request.POST:
                data = request.POST['pilihan']
                data_anggaran = Anggaran.objects.filter(client_id=data).select_related('jenis_anggaran')
                context = {'client':client,'data_anggaran':data_anggaran,'data':data}
                return render(request,'finance/expense.html', context)
            
            if 'updateAnggaran' in request.POST:
                jenis_anggaran = request.POST['jenis_anggaran']
                tanggal = request.POST['tanggal']
                total = request.POST['total']
                client_id = request.POST['client_id']
                anggaran_id = Anggaran.objects.filter(jenis_anggaran=jenis_anggaran,client_id=client_id).values_list('id', flat=True)
                anggaran_total = Anggaran.objects.filter(jenis_anggaran=jenis_anggaran,client_id=client_id).values_list('total_anggaran', flat=True)
                anggaran_int = anggaran_total[0]
                total_int = int(total)

                sisa_anggaran = anggaran_int - total_int
                sisa_budget = sisa_anggaran
                pemakaian = 1 - ((anggaran_int - sisa_budget) / anggaran_int)
                pemakaian_persen = f"{pemakaian:.2%}"
                expense = data_Expense(jenis_anggaran_id=jenis_anggaran,tanggal=tanggal,total=total,client_id_id=client_id,anggaran_id_id=anggaran_id, sisa_budget=sisa_budget)
                expense.save()

                messages.success(request, 'Data anggaran berhasil diupdate')
                return redirect('management-expense')
        else:        
            context = {'client':client}
            return render(request,'finance/expense.html', context)
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')          

@login_required
def Management_IB(request):
    user = request.user
    if user.is_authenticated and user.is_management:
        if request.method == 'POST':
            invoiceForm = InvoiceForm(request.POST, request.FILES)        
            if invoiceForm.is_valid():
                iForm = invoiceForm.save()
                messages.success(request, 'Data Invoice berhasil disimpan')
                return redirect('management-invoice-baru')
            else:            
                messages.error(request, 'Data invoice salah')

        else:
            invoiceForm = InvoiceForm()       
            context = {'form':invoiceForm}
            return render(request, 'finance/invoice-baru.html', context)
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')  

@login_required        
def Management_DI(request):
    user = request.user
    if user.is_authenticated and user.is_management:
        projek = Project.objects.only('client')
        if request.method == 'POST':
            client = request.POST['pilihan']
            cdb = Invoice.objects.raw("SELECT * FROM janggadb_invoice WHERE client_id_id = %s", [client])
            context = {'projek':projek, 'invoice':cdb}
            return render(request,'finance/data-invoice.html',context)
        else:
            context = {'projek':projek}
            return render(request,'finance/data-invoice.html', context)
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')          

def Management_updateStatus(request, id=id):
    status = request.POST['status']
    Invoice.objects.filter(nomor_invoice=id).update(status=status)
    messages.success(request, 'status telah diupdate')
    return redirect('management-invoice')

def Management_P(request):
    user = request.user
    if user.is_authenticated and user.is_management:
        projek = Project.objects.only('client')
        if request.method == 'POST':
            client = request.POST['pilihan']
            client_obj = Pengajuan_Barang.objects.filter(client_id=client)
            context = {'projek':projek, 'pengajuan':client_obj}
            return render(request,'finance/pengajuan-barang.html', context)
        else:
            context = {'projek':projek}
            return render(request,'finance/pengajuan-barang.html', context)
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index') 

def Management_RP(request):
    engine = create_engine('postgresql+psycopg2://admin:admin@localhost:5432/jangga_db')
    user = request.user
    if user.is_authenticated and user.is_management:
        projek = Project.objects.only('id')            
        if request.method == 'POST':
            if 'inputProjek' in request.POST:
                pro = request.POST['pilih']
                anggaran = Jenis_Anggaran.objects.filter(nomor_SPK_id=pro).only('nama_jenis')
                
                context = {'projek':projek,'pro':pro,'anggaran':anggaran}
                return render(request, 'finance/breakdown-rab.html', context)
            if 'inputAnggaran' in request.POST:
                uploaded_files = request.FILES['lampiran-rab']
                fs = FileSystemStorage()                    
                fs.save(uploaded_files.name, uploaded_files)      
                # simpan file ke dalam local server
                file_name = uploaded_files.name 

                df = pd.read_excel("/srv/jcr/projek1/data/" + file_name)
                pd.set_option("display.max_rows", None)
                pd.set_option("display.max_columns", None)
                
                spk = request.POST['spk']
                df['nomor_SPK'] = spk
                df = df.rename(columns ={'URAIAN PEKERJAAN':'nama_jenis','nomor_SPK':'nomor_SPK_id'})

                df.to_sql(
                            'janggadb_jenis_anggaran', con=engine, index=False, if_exists='append'
                )
                messages.add_message(request, messages.SUCCESS, 'Data berhasil diinputkan')
            if 'inputLogistik' in request.POST:
                uploaded_files = request.FILES['lampiran-rab']
                fs = FileSystemStorage()                    
                fs.save(uploaded_files.name, uploaded_files)      
                # simpan file ke dalam local server
                file_name = uploaded_files.name 

                df = pd.read_excel("/srv/jcr/projek1/data/" + file_name)
                pd.set_option("display.max_rows", None)
                pd.set_option("display.max_columns", None)  

                client = request.POST.get('spk')
                df['client'] = client
                jenis = request.POST['kelompok']
                df['jenis_anggaran'] = jenis

                df = df.rename(columns ={'URAIAN PEKERJAAN':'nama_barang','client':'client_id_id','jenis_anggaran':'jenis_anggaran_id'})

                df.to_sql(
                            'janggadb_breakdown_rab', con=engine, index=False, if_exists='append'
                )
                messages.add_message(request, messages.SUCCESS, 'Data berhasil diinputkan')

        context = {'projek':projek}
        return render(request,'finance/breakdown-rab.html', context)    
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index') 
    
def Client(request):
    user = request.user
    if user.is_authenticated and user.is_client:
        if request.method == 'POST':
            pro = request.POST['client']
            import plotly.express as px
            engine = create_engine('postgresql+psycopg2://admin:admin@localhost:5432/jangga_db')
            query = """SELECT jpm.jenis_pekerjaan, jpm.fase, jmr.nomor_unit, jmr.aktual_mapping as Hari_Ini, jmr.total_mapping as Max, jmr.tanggal FROM janggadb_mapping_report as jmr CROSS JOIN janggadb_pekerjaan_mapping as jpm WHERE jmr.jenis_pekerjaan_id = jpm.id AND client_id_id = """+pro+""" AND tanggal = (SELECT MAX(tanggal) FROM janggadb_mapping_report)"""
            query2 = """SELECT jpm.jenis_pekerjaan, jpm.fase, jmr.nomor_unit, jmr.aktual_mapping as kemarin from janggadb_mapping_report as jmr CROSS JOIN janggadb_pekerjaan_mapping as jpm WHERE jmr.jenis_pekerjaan_id = jpm.id AND client_id_id = """+pro+""" AND tanggal = (SELECT MAX(tanggal) FROM janggadb_mapping_report) - INTERVAL '1 day'"""
            
            df = pd.read_sql_query(query,engine)
            df2 = pd.read_sql_query(query2,engine)
            res = pd.merge(df,df2, on=["jenis_pekerjaan","nomor_unit"])
            res['total'] = res['hari_ini'] + res['kemarin']            

            res["persentase"] = res["total"] / res["max"] * 100 

            average_persentase = round(res["persentase"].mean(), 2)
            total_count = (res['total'] == 19).sum()

            res['progres'] = np.where(res['total'] == res['max'], 1, 0)

            res_summary = (res[res["progres"] == 1]
                            .groupby(["nomor_unit", "jenis_pekerjaan"], as_index=False)
                            .size()
                            .rename(columns={"size": "count"}))

            all_units = pd.DataFrame({'nomor_unit': sorted(res['nomor_unit'].unique())})
            res_summary = (
                all_units
                .merge(res_summary, on="nomor_unit", how="left")
                .fillna({'count': 0, 'jenis_pekerjaan': 'Belum Ada Progres'})
            )

            # Convert count to int (for better display)
            res_summary["count"] = res_summary["count"].astype(int)                            

            fig = px.bar(
                res_summary,
                x="nomor_unit",
                y="count",
                color="jenis_pekerjaan",
                text="jenis_pekerjaan",
                barmode="stack",
                title="Progress per Unit"
            )

            fig.update_xaxes(
                tickmode="linear",
                dtick=1,
                categoryarray=res_summary["nomor_unit"].tolist()
            )

            fig.update_yaxes(dtick=1, tickmode="linear", tickformat="d")

            fig.update_layout(
                xaxis_title="Nomor Unit",
                yaxis_title="Progress Count",
                paper_bgcolor="lightgray"
            )

            diagram = fig.to_html()

            projek = Project.objects.only('client')
            context = {'user':user,'rata':average_persentase,'total':total_count,'diagram':diagram,'projek':projek}
            return render(request, 'client/dashboard.html', context)    

        else:
            projek = Project.objects.only('client')
            import plotly.express as px
            engine = create_engine('postgresql+psycopg2://admin:admin@localhost:5432/jangga_db')
            
            query = """SELECT jpm.jenis_pekerjaan, jpm.fase, jmr.nomor_unit, jmr.aktual_mapping as Hari_Ini, jmr.total_mapping as Max, jmr.tanggal FROM janggadb_mapping_report as jmr CROSS JOIN janggadb_pekerjaan_mapping as jpm WHERE jmr.jenis_pekerjaan_id = jpm.id AND tata_letak = 'XYZ CHARM 18' AND tanggal = (SELECT MAX(tanggal) FROM janggadb_mapping_report)"""
            query2 = """SELECT jpm.jenis_pekerjaan, jpm.fase, jmr.nomor_unit, jmr.aktual_mapping as kemarin FROM janggadb_mapping_report as jmr CROSS JOIN janggadb_pekerjaan_mapping as jpm WHERE jmr.jenis_pekerjaan_id = jpm.id AND tata_letak = 'XYZ CHARM 18' AND tanggal = (SELECT tanggal FROM janggadb_mapping_report ORDER BY tanggal ASC LIMIT 1 OFFSET 1)"""

            df = pd.read_sql_query(query,engine)
            df2 = pd.read_sql_query(query2,engine)
            res = pd.merge(df,df2, on=["jenis_pekerjaan","nomor_unit"])
            res['total'] = res['hari_ini'] + res['kemarin']            

            res["persentase"] = res["total"] / res["max"] * 100 

            average_persentase = round(res["persentase"].mean(), 2)
            total_count = (res['total'] == 19).sum()

            res['progres'] = np.where(res['total'] == res['max'], 1, 0)

            res_summary = (res[res["progres"] == 1]
                            .groupby(["nomor_unit", "jenis_pekerjaan"], as_index=False)
                            .size()
                            .rename(columns={"size": "count"}))

            all_units = pd.DataFrame({'nomor_unit': sorted(res['nomor_unit'].unique())})
            res_summary = (
                all_units
                .merge(res_summary, on="nomor_unit", how="left")
                .fillna({'count': 0, 'jenis_pekerjaan': 'Belum Ada Progres'})
            )

            # Convert count to int (for better display)
            res_summary["count"] = res_summary["count"].astype(int)                            

            fig = px.bar(
                res_summary,
                x="nomor_unit",
                y="count",
                color="jenis_pekerjaan",
                text="jenis_pekerjaan",
                barmode="stack",
                title="Progress per Unit"
            )

            fig.update_xaxes(
                tickmode="linear",
                dtick=1,
                categoryarray=res_summary["nomor_unit"].tolist()
            )

            fig.update_yaxes(dtick=1, tickmode="linear", tickformat="d")

            fig.update_layout(
                xaxis_title="Nomor Unit",
                yaxis_title="Progress Count",
                paper_bgcolor="lightgray"
            )

            diagram = fig.to_html()

            context = {'user':user,'rata':average_persentase,'total':total_count,'diagram':diagram,'projek':projek}
            return render(request, 'client/dashboard.html', context) 
    
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')

class VideoCamera(object):
    def __init__(self):
        # Use rtsp, not rstp
        self.video = cv2.VideoCapture("http://61.211.241.239/nphMotionJpeg?Resolution=320x240&Quality=Standard")


    def __del__(self):
        if self.video.isOpened():
            self.video.release()

    def get_frame(self):
        success, frame = self.video.read()
        if not success:
            return None

        # Encode the frame in JPEG format
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

# Generator function for streaming
def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame is None:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_feed(request):
    cam = VideoCamera()
    return StreamingHttpResponse(
        gen(cam),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )

def Client_Live(request):
    return render(request, 'client/live-stream.html')    

@login_required        
def Logout(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS,'Anda telah berhasil logout')
    return redirect('index')

  
