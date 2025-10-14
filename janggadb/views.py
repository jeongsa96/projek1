from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .forms import LoginForm, RegisterForm, ProjekForm, InvoiceForm, POform, AnggaranForm, MonitoringForm, ReportForm, updateProfileForm, photoProfileForm, changePasswordForm
from .models import *
from django.contrib import messages
from django.http import JsonResponse
import pandas as pd
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
                    'is_admin': 'admin-jangga',
                    'is_projectManager': 'project-manager',
                    'is_finance': 'finance',
                    'is_logistik': 'logistik',
                    'is_client': 'client-dashboard',
                }

                for role, url in role_map.items():
                    if getattr(user, role):
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
    return render(request, 'admin/ganti-password.html', context)                 
    
    

@login_required
def Admin_Profil(request, pk):
    user = User.objects.get(pk=pk)
    profile = Profile.objects.get(user__id=pk)
    user_form = updateProfileForm(request.POST or None, request.FILES or None, instance=user)
    photo_form = photoProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if user_form.is_valid() and photo_form.is_valid():
        user_form.save()
        photo_form.save()
        messages.success(request, 'Profil anda telah diupdate ')
        return redirect('admin-jangga')
    else:
        messages.error(request, 'Input anda salah')

    context = {'user_form':user_form,'photo_form':photo_form}                
    return render(request, 'admin/edit-profile.html', context)

@login_required
def Admin(request):   
    user = request.user
    if user.is_authenticated and user.is_admin:
        from django.db.models import Count
        list = Mapping_Report.objects.values("tata_letak").annotate(summed_quantity=Count('tata_letak'))
        fase = Pekerjaan_mapping.objects.values("fase").annotate(summed_quantity=Count('fase')).order_by('fase')
        pro = Project.objects.only('client')
        if request.method == 'POST':
            letak = request.POST['tata-letak']
            fases = request.POST['fase']
            projek = request.POST['client']
            import plotly.express as px
            engine = create_engine('postgresql+psycopg2://admin:admin@localhost:5432/jangga_db')
            query = """SELECT jpm.jenis_pekerjaan, jmr.aktual_mapping as Hari_Ini, jmr.total_mapping as Max, jmr.tanggal FROM janggadb_mapping_report as jmr CROSS JOIN janggadb_pekerjaan_mapping as jpm WHERE jmr.jenis_pekerjaan_id = jpm.id AND tata_letak = '"""+letak+"""' AND client_id_id = """+projek+""" AND jpm.fase = '"""+fases+"""' AND tanggal = (SELECT MAX(tanggal) FROM janggadb_mapping_report)"""
            query2 = """SELECT jpm.jenis_pekerjaan, jmr.aktual_mapping as kemarin from janggadb_mapping_report as jmr CROSS JOIN janggadb_pekerjaan_mapping as jpm WHERE jmr.jenis_pekerjaan_id = jpm.id AND tata_letak = '"""+letak+"""' AND client_id_id = """+projek+""" AND jpm.fase = '"""+fases+"""' AND tanggal = (SELECT MAX(tanggal) FROM janggadb_mapping_report) - INTERVAL '1 day'"""
            
            df = pd.read_sql_query(query,engine)
            df2 = pd.read_sql_query(query2,engine)
            res = pd.merge(df,df2, on="jenis_pekerjaan")
            res['total'] = res['hari_ini'] + res['kemarin']

            res["persentase"] = res["total"] / res["max"] * 100

            average_persentase = round(res["persentase"].mean(), 2)

            import math
            if math.isnan(average_persentase):
                average_persentase = "0"

            total_count = (res['total'] == 19).sum()

            res["label"] = res["total"].astype(str) + "/" + res["max"].astype(str) + \
                        " (" + res["persentase"].map("{:.2f}%".format) + ")"

            res = res.sort_values("persentase", ascending=True)

            fig = px.bar(
                res,
                x="persentase",
                y="jenis_pekerjaan",
                orientation="h",
                text=res["label"], 
                title="XYZ CHARM 19",
                hover_data={
                    "kemarin": True,
                    "hari_ini": True,
                    "total": True,
                    "max": True,
                    "persentase": ":.2f" 
                }
            )

            fig.update_traces(marker_color="lightblue", textposition="outside")
            fig.update_layout(
                xaxis_title="Persentase (%)",
                yaxis_title="Pekerjaan",
                xaxis=dict(range=[0, 100]),
                paper_bgcolor='pink',
            )

            diagram = fig.to_html()
            
            context = {'user':user,'rata':average_persentase,'total':total_count,'diagram':diagram,'list':list,'fase':fase,'pro':pro}
            return render(request,'admin/dashboard.html', context)


        else:    
            import plotly.express as px
            engine = create_engine('postgresql+psycopg2://admin:admin@localhost:5432/jangga_db')
            
            query = """SELECT jpm.jenis_pekerjaan, jmr.aktual_mapping as Hari_Ini, jmr.total_mapping as Max, jmr.tanggal FROM janggadb_mapping_report as jmr CROSS JOIN janggadb_pekerjaan_mapping as jpm WHERE jmr.jenis_pekerjaan_id = jpm.id AND tata_letak = 'XYZ CHARM 19' AND tanggal = (SELECT MAX(tanggal) FROM janggadb_mapping_report)"""
            query2 = """SELECT jpm.jenis_pekerjaan, jmr.aktual_mapping as kemarin from janggadb_mapping_report as jmr cross join janggadb_pekerjaan_mapping as jpm WHERE jmr.jenis_pekerjaan_id = jpm.id AND tata_letak = 'XYZ CHARM 19' AND tanggal = (SELECT MAX(tanggal) FROM janggadb_mapping_report) - INTERVAL '1 day'"""

            df = pd.read_sql_query(query,engine)
            df2 = pd.read_sql_query(query2,engine)
            res = pd.merge(df,df2, on="jenis_pekerjaan")
            res['total'] = res['hari_ini'] + res['kemarin']

            res["persentase"] = res["total"] / res["max"] * 100

            average_persentase = res["persentase"].mean().round(2)
            total_count = (res['total'] == 19).sum()

            res["label"] = res["total"].astype(str) + "/" + res["max"].astype(str) + \
                        " (" + res["persentase"].map("{:.2f}%".format) + ")"

            res = res.sort_values("persentase", ascending=True)

            fig = px.bar(
                res,
                x="persentase",
                y="jenis_pekerjaan",
                orientation="h",
                text=res["label"], 
                title="XYZ CHARM 19",
                hover_data={
                    "kemarin": True,
                    "hari_ini": True,
                    "total": True,
                    "max": True,
                    "persentase": ":.2f" 
                }
            )

            fig.update_traces(marker_color="lightblue", textposition="outside")
            fig.update_layout(
                xaxis_title="Persentase (%)",
                yaxis_title="Pekerjaan",
                xaxis=dict(range=[0, 100]),
                paper_bgcolor='pink',
            )

            diagram = fig.to_html()
            
            context = {'user':user,'rata':average_persentase,'total':total_count,'diagram':diagram,'list':list,'fase':fase,'pro':pro}
            return render(request,'admin/dashboard.html', context)
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')

@login_required
def Admin_PD(request):
    user = request.user
    if user.is_authenticated and user.is_admin:
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
def Admin_PB(request):
    user = request.user
    if user.is_authenticated and user.is_admin:
        if request.method == 'POST':
            form = ProjekForm(request.POST)
            if form.is_valid():
                projek = form.save()
                messages.success(request, 'Input data berhasil')
                return redirect('admin-projek-baru')
            else:
                messages.error(request, 'Input salah')
        else:
            form = ProjekForm()

        context = {'form':form}
        return render(request, 'admin/projek-baru.html', context)
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')            

@login_required
def Admin_DR(request):
    user = request.user
    if user.is_authenticated and user.is_admin:
        if request.method == 'POST':
            form = ReportForm(request.POST)
            if form.is_valid():
                map = form.save()
                messages.success(request, 'Daily Report telah disimpan')
                return redirect('admin-daily-report')
        else:
            form = ReportForm()

        context = {'form':form}
        return render(request, 'admin/input-daily.html', context)  
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')       
        
@login_required
def Project_Manager(request):
    from django.db.models import Count
    list_segmen = Mapping_Report.objects.values("tata_letak").annotate(summed_quantity=Count('tata_letak'))
    import plotly.express as px
    engine = create_engine('postgresql+psycopg2://admin:admin@localhost:5432/jangga_db')
    if request.method == 'POST':
        seg = request.POST['tata_letak']
        query = """SELECT jpm.jenis_pekerjaan, jmr.aktual_mapping as Hari_Ini, jmr.total_mapping as Max, jmr.tanggal FROM janggadb_mapping_report as jmr CROSS JOIN janggadb_pekerjaan_mapping as jpm WHERE jmr.jenis_pekerjaan_id = jpm.id AND tata_letak = '"""+seg+"""' AND tanggal = (SELECT MAX(tanggal) FROM janggadb_mapping_report)"""
        query2 = """SELECT jpm.jenis_pekerjaan, jmr.aktual_mapping as kemarin from janggadb_mapping_report as jmr cross join janggadb_pekerjaan_mapping as jpm WHERE jmr.jenis_pekerjaan_id = jpm.id AND tata_letak = '"""+seg+"""' AND tanggal = (SELECT MAX(tanggal) FROM janggadb_mapping_report) - INTERVAL '1 day'"""

        df = pd.read_sql_query(query,engine)
        df2 = pd.read_sql_query(query2,engine)
        res = pd.merge(df,df2, on="jenis_pekerjaan")
        res['total'] = res['hari_ini'] + res['kemarin']

        res["persentase"] = res["total"] / res["max"] * 100

        average_persentase = res["persentase"].mean().round(2)
        total_count = (res['total'] == 19).sum()

        res["label"] = res["total"].astype(str) + "/" + res["max"].astype(str) + \
                    " (" + res["persentase"].map("{:.2f}%".format) + ")"

        res = res.sort_values("persentase", ascending=True)

        fig = px.bar(
            res,
            x="persentase",
            y="jenis_pekerjaan",
            orientation="h",
            text=res["label"], 
            title=seg,
            hover_data={
                "kemarin": True,
                "hari_ini": True,
                "total": True,
                "max": True,
                "persentase": ":.2f" 
            }
        )

        fig.update_traces(marker_color="lightblue", textposition="outside")
        fig.update_layout(
            xaxis_title="Persentase (%)",
            yaxis_title="Pekerjaan",
            xaxis=dict(range=[0, 100]),
            paper_bgcolor='pink',
        )

        diagram = fig.to_html()
        context = {'rata':average_persentase,'total':total_count,'diagram':diagram,'list_segmen':list_segmen}
        return render(request,'pm/dashboard.html', context)
    
    from random import choice
    data = Mapping_Report.objects.values_list('tata_letak', flat=True)
    random = choice(data)
    query = """SELECT jpm.jenis_pekerjaan, jmr.aktual_mapping as Hari_Ini, jmr.total_mapping as Max, jmr.tanggal FROM janggadb_mapping_report as jmr CROSS JOIN janggadb_pekerjaan_mapping as jpm WHERE jmr.jenis_pekerjaan_id = jpm.id AND tata_letak = '"""+random+"""' AND tanggal = (SELECT MAX(tanggal) FROM janggadb_mapping_report)"""
    query2 = """SELECT jpm.jenis_pekerjaan, jmr.aktual_mapping as kemarin from janggadb_mapping_report as jmr cross join janggadb_pekerjaan_mapping as jpm WHERE jmr.jenis_pekerjaan_id = jpm.id AND tata_letak = '"""+random+"""' AND tanggal = (SELECT MAX(tanggal) FROM janggadb_mapping_report) - INTERVAL '1 day'"""

    df = pd.read_sql_query(query,engine)
    df2 = pd.read_sql_query(query2,engine)
    res = pd.merge(df,df2, on="jenis_pekerjaan")
    res['total'] = res['hari_ini'] + res['kemarin']

    res["persentase"] = res["total"] / res["max"] * 100

    average_persentase = res["persentase"].mean().round(2)
    total_count = (res['total'] == 19).sum()

    res["label"] = res["total"].astype(str) + "/" + res["max"].astype(str) + \
                " (" + res["persentase"].map("{:.2f}%".format) + ")"

    res = res.sort_values("persentase", ascending=True)

    fig = px.bar(
        res,
        x="persentase",
        y="jenis_pekerjaan",
        orientation="h",
        text=res["label"], 
        title=random,
        hover_data={
            "kemarin": True,
            "hari_ini": True,
            "total": True,
            "max": True,
            "persentase": ":.2f" 
        }
    )

    fig.update_traces(marker_color="lightblue", textposition="outside")
    fig.update_layout(
        xaxis_title="Persentase (%)",
        yaxis_title="Pekerjaan",
        xaxis=dict(range=[0, 100]),
        paper_bgcolor='pink',
    )

    diagram = fig.to_html()
    context = {'rata':average_persentase,'total':total_count,'diagram':diagram,'list_segmen':list_segmen}
    return render(request,'pm/dashboard.html', context)

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
        return render(request,'logistik/dashboard.html')
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index') 

@login_required
def Logistik_PO(request):
    user = request.user
    if user.is_authenticated and user.is_logistik:
        if request.method == 'POST':
            PO = POform(request.POST)
            if PO.is_valid():
                form = PO.save()
                messages.success(request, 'Data PO berhasil disimpan')
                return redirect('logistik-po')
            else: 
                messages.error(request, 'data input PO salah')
        else:
            form = POform()            

        context = {'form':form}
        return render(request,'logistik/data-po.html', context)
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')     

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
                redirect('logistik-monitoring-po')
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
def Logistik_DL(request):
    user = request.user
    if user.is_authenticated and user.is_logistik:
        projek = Project.objects.only("client")
        context = {'projek':projek}
        return render(request,'logistik/document-log.html', context)
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index') 

@login_required
def Finance(request):
    user = request.user
    if user.is_authenticated and user.is_finance:
        return render(request,'finance/dashboard.html')
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index') 
    
@login_required        
def Finance_A(request):
    user = request.user
    if user.is_authenticated and user.is_finance:
        if request.method == 'POST':
            anggaran = AnggaranForm(request.POST)
            if anggaran.is_valid():
                form = anggaran.save()
                messages.success(request, 'Data anggaran berhasil disimpan')
                return redirect('finance-anggaran')
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
def Finance_AC(request):
    user = request.user
    if user.is_authenticated and user.is_finance:
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
def Finance_E(request):
    user = request.user
    if user.is_authenticated and user.is_finance:
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
                return redirect('finance-expense')
        else:        
            context = {'client':client}
            return render(request,'finance/expense.html', context)
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')          

@login_required
def Finance_IB(request):
    user = request.user
    if user.is_authenticated and user.is_finance:
        if request.method == 'POST':
            invoiceForm = InvoiceForm(request.POST, request.FILES)        
            if invoiceForm.is_valid():
                iForm = invoiceForm.save()
                messages.success(request, 'Data Invoice berhasil disimpan')
                return redirect('finance-invoice-baru')
            else:            
                messages.error(request, 'data invoice salah')

        else:
            invoiceForm = InvoiceForm()       
            context = {'form':invoiceForm}
            return render(request, 'finance/invoice-baru.html', context)
    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')  

@login_required        
def Finance_DI(request):
    user = request.user
    if user.is_authenticated and user.is_finance:
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

def Finance_updateStatus(request, id=id):
    status = request.POST['status']
    Invoice.objects.filter(nomor_invoice=id).update(status=status)
    messages.success(request, 'status telah diupdate')
    return redirect('finance-invoice')

def Client(request):
    user = request.user
    if user.is_authenticated and user.is_client:
        from django.db.models import Count
        list = Mapping_Report.objects.values("tata_letak").annotate(summed_quantity=Count('tata_letak'))
        import plotly.express as px
        engine = create_engine('postgresql+psycopg2://admin:admin@localhost:5432/jangga_db')
        
        query = """SELECT jpm.jenis_pekerjaan, jmr.aktual_mapping as Hari_Ini, jmr.total_mapping as Max, jmr.tanggal FROM janggadb_mapping_report as jmr CROSS JOIN janggadb_pekerjaan_mapping as jpm WHERE jmr.jenis_pekerjaan_id = jpm.id AND tata_letak = 'XYZ CHARM 19' AND tanggal = (SELECT MAX(tanggal) FROM janggadb_mapping_report)"""
        query2 = """SELECT jpm.jenis_pekerjaan, jmr.aktual_mapping as kemarin from janggadb_mapping_report as jmr cross join janggadb_pekerjaan_mapping as jpm WHERE jmr.jenis_pekerjaan_id = jpm.id AND tata_letak = 'XYZ CHARM 19' AND tanggal = (SELECT MAX(tanggal) FROM janggadb_mapping_report) - INTERVAL '1 day'"""

        df = pd.read_sql_query(query,engine)
        df2 = pd.read_sql_query(query2,engine)
        res = pd.merge(df,df2, on="jenis_pekerjaan")
        res['total'] = res['hari_ini'] + res['kemarin']

        res["persentase"] = res["total"] / res["max"] * 100

        average_persentase = res["persentase"].mean().round(2)
        total_count = (res['total'] == 19).sum()

        res["label"] = res["total"].astype(str) + "/" + res["max"].astype(str) + \
                    " (" + res["persentase"].map("{:.2f}%".format) + ")"

        res = res.sort_values("persentase", ascending=True)

        fig = px.bar(
            res,
            x="persentase",
            y="jenis_pekerjaan",
            orientation="h",
            text=res["label"], 
            title="XYZ CHARM 19",
            hover_data={
                "kemarin": True,
                "hari_ini": True,
                "total": True,
                "max": True,
                "persentase": ":.2f" 
            }
        )

        fig.update_traces(marker_color="lightblue", textposition="outside")
        fig.update_layout(
            xaxis_title="Persentase (%)",
            yaxis_title="Pekerjaan",
            xaxis=dict(range=[0, 100]),
            paper_bgcolor='pink',
        )

        diagram = fig.to_html()
        
        context = {'user':user,'rata':average_persentase,'total':total_count,'diagram':diagram,'list':list}
        return render(request, 'client/dashboard.html', context)    

    else:
        messages.error(request, 'Akses gagal')
        logout(request)
        return redirect('index')

@login_required        
def Logout(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS,'Anda telah berhasil logout')
    return redirect('index')

  