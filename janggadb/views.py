from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, RegisterForm, ProjekForm, InvoiceForm, POform
from .models import Project, Invoice, PO
from django.contrib import messages


def register(request):
    msg = None
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()
            msg = 'user created'
            return redirect('index')
        else:
            msg = 'form is not valid'
    else:
        form = RegisterForm()
    return render(request,'register.html', {'form': form, 'msg': msg})

def index(request):
    form = LoginForm(request.POST or None)
    msg = None
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_admin:
                login(request, user)
                return redirect('admin-jangga')
            elif user is not None and user.is_projectManager:
                login(request, user)
                return redirect('project-manager')
            elif user is not None and user.is_finance:
                login(request, user)
                request.session['username'] = user.username
                return redirect('finance')
            elif user is not None and user.is_logistik:            
                login(request, user)
                return redirect('logistik')
            else: 
                msg = 'username atau password anda salah'
        else:
            msg = 'error'        
    return render(request, 'login.html', {'form':form, 'msg':msg})
    # if request.method == 'POST':
    #         form = LoginForm(request.POST)
    #         if form.is_valid():
    #             username = form.cleaned_data.get('username')
    #             password = form.cleaned_data.get('password')
    #             user = authenticate(username=username, password=password)

    #             if user is not None:
    #                 login(request, user)
    #                 request.session['username'] = user.username

    #                 role_map = {
    #                     'is_admin': 'admin-jangga',
    #                     'is_projectManager': 'project-manager',
    #                     'is_finance': 'finance',
    #                     'is_logistik': 'logistik',
    #                 }

    #                 for role, url in role_map.items():
    #                     if getattr(user, role):
    #                         return redirect(reverse(url))

    #                 messages.error(request, 'Invalid user role')
    #             else:
    #                 messages.error(request, 'Invalid username or password')
    #         else:
    #             messages.error(request, 'Form validation error')
    #     else:
    #         form = LoginForm()

    # return render(request, 'login.html', {'form': form})

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
    return render(request,'finance/anggaran.html')

@login_required        
def Finance_DI(request):
    projek = Project.objects.only("client")
    if request.method == 'POST':
        client = request.POST['pilihan']
        cdb = Invoice.objects.raw("SELECT * FROM janggadb_invoice WHERE client_id_id = %s", [client])
        context = {'projek':projek, 'invoice':cdb}
        return render(request,'finance/data-invoice.html',context)

    return render(request,'finance/data-invoice.html',{'projek':projek})

@login_required        
def Logout(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS,'Anda telah berhasil logout')
    return redirect('index')



