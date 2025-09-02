from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, RegisterForm, ProjekForm, InvoiceForm, POform, AnggaranForm
from .models import Project, Invoice, PO, Anggaran, data_Expense, Jenis_Anggaran
from django.contrib import messages


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
            msg = 'form is not valid'
    else:
        form = RegisterForm()
    return render(request,'register.html', {'form': form})

def index(request):
    form = LoginForm(request.POST or None)
    msg = None
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

    return render(request, 'login.html', {'form': form})

@login_required
def Admin(request):
    user = request.session.get('username')
    return render(request,'admin/dashboard.html',{'user':user})

@login_required
def Admin_PD(request):
    projek = Project.objects.only("client")

    return render(request, 'admin/projek-db.html',{'projek':projek})

@login_required
def Admin_PB(request):
    msg = None
    if request.method == 'POST':
        form = ProjekForm(request.POST)
        if form.is_valid():
            projek = form.save()
            return redirect('admin-projek-baru')
        else:
            msg = 'input salah'
    else:
        form = ProjekForm()

    return render(request, 'admin/projek-baru.html',{'form':form,'msg':msg})

@login_required
def Admin_IB(request):
    msg = None
    if request.method == 'POST':
        invoiceForm = InvoiceForm(request.POST, request.FILES)        
        if invoiceForm.is_valid():
            iForm = invoiceForm.save()
            return redirect('admin-invoice-baru')
        else:            
            msg = 'data invoice salah'

    else:
        invoiceForm = InvoiceForm()       
    
    return render(request, 'admin/invoice-baru.html',{'msg':msg,'form':invoiceForm })

@login_required
def Admin_PR(request):
    projek = Project.objects.only('client')
    if request.method == 'POST':
        client = request.POST['pilihan']
        client_po = PO.objects.filter(client_id=client)
        context = {'projek':projek,'client_po':client_po}
        return render(request, 'admin/po-request.html', context)

    return render(request, 'admin/po-request.html',{'projek':projek})

def Admin_updateStatus(request, id=id):
    status = request.POST['status']
    PO.objects.filter(nomor_po=id).update(status=status)
    messages.success(request, 'status telah diupdate')
    return redirect('admin-po-request')
        
@login_required
def Project_Manager(request):
    return render(request,'pm/dashboard.html')

@login_required
def Project_Manager_PD(request):
    projek = Project.objects.only("client")
    if request.method == 'POST':
        client = request.POST['pilihan']
        cdb = Project.objects.raw("SELECT * FROM janggadb_project WHERE client= %s", [client])
        context = {'projek':projek, 'client':cdb}

        return render(request,'pm/projek-db.html', context)

    return render(request,'pm/projek-db.html',{'projek':projek})

@login_required
def Logistik(request):
    return render(request,'logistik/dashboard.html')

@login_required
def Logistik_PO(request):
    msg = None
    if request.method == 'POST':
        PO = POform(request.POST)
        if PO.is_valid():
            form = PO.save()
            return redirect('logistik-po')
        else: 
            msg = 'data input PO salah'
    else:
        form = POform()            

    return render(request,'logistik/data-po.html',{'form':form})

@login_required
def Logistik_DL(request):
    projek = Project.objects.only("client")
    context = {'projek':projek}
    return render(request,'logistik/document-log.html', context)

@login_required
def Finance(request):
    return render(request,'finance/dashboard.html')

@login_required        
def Finance_A(request):
    msg = None
    if request.method == 'POST':
        anggaran = AnggaranForm(request.POST)
        if anggaran.is_valid():
            form = anggaran.save()
            return redirect('finance-anggaran')
        else:
            msg = 'data anggaran salah'
    else:
        form = AnggaranForm

    context = {'form':form}
    return render(request,'finance/anggaran.html', context)

@login_required
def Finance_AC(request):
    client = Project.objects.only("client")
    anggaran = Jenis_Anggaran.objects.all()
    if request.method == 'POST':
        client_input = request.POST['client']
        anggaran_input = request.POST['jenis']
        data_anggaran = Anggaran.objects.filter(client_id=client_input, jenis_anggaran=anggaran_input)
        
        context = {'client':client,'anggaran':anggaran,'data_anggaran':data_anggaran}
        return render(request, 'finance/cek-anggaran.html', context)


    context = {'client':client,'anggaran':anggaran}
    return render(request,'finance/cek-anggaran.html',context)


@login_required
def Finance_E(request):
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
            anggaran_id = Anggaran.objects.filter(jenis_anggaran=jenis_anggaran,client_id=client_id).values_list('id')
            anggaran_total = Anggaran.objects.filter(jenis_anggaran=jenis_anggaran,client_id=client_id).values_list('total_anggaran', flat=True)
            anggaran_int = anggaran_total[0]
            total_int = int(total)

            expense = data_Expense(jenis_anggaran_id=jenis_anggaran,tanggal=tanggal,total=total,client_id_id=client_id,anggaran_id_id=anggaran_id)
            expense.save()

            sisa_anggaran = anggaran_int - total_int

            Anggaran.objects.filter(id=anggaran_id[0][0]).update(total_anggaran=sisa_anggaran)
            return redirect('finance-expense')
        
    context = {'client':client}
    return render(request,'finance/expense.html', context)

@login_required        
def Finance_DI(request):
    projek = Project.objects.only('client')
    if request.method == 'POST':
        client = request.POST['pilihan']
        cdb = Invoice.objects.raw("SELECT * FROM janggadb_invoice WHERE client_id_id = %s", [client])
        context = {'projek':projek, 'invoice':cdb}
        return render(request,'finance/data-invoice.html',context)

    return render(request,'finance/data-invoice.html',{'projek':projek})

def Finance_updateStatus(request, id=id):
    status = request.POST['status']
    Invoice.objects.filter(nomor_invoice=id).update(status=status)
    messages.success(request, 'status telah diupdate')
    return redirect('finance-invoice')

@login_required        
def Logout(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS,'Anda telah berhasil logout')
    return redirect('index')



