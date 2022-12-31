from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum,Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
from donor import models as dmodels
from patient import models as pmodels
from donor import forms as dforms
from patient import forms as pforms
import pymysql
import pymysql.cursors


db = pymysql.connect(host='127.0.0.1',
                         user='root',
                         password='9515290749',
                         database='bloodbank')
cursor = db.cursor()
def home_view(request):
    prestmt="select * from bloodbank.blood_stock;"
    cursor.execute(prestmt)
    res=cursor.fetchall()
    if len(res)==0:
        stmt = "insert into bloodbank.blood_stock(id,bloodgroup,unit) values (1,'A+',0),(2,'A-',0),(3,'B+',0),(4,'B-',0),(5,'AB+',0),(6,'AB-',0),(7,'O+',0),(8,'O-',0);"
        cursor.execute(stmt)
        db.commit()
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'blood/index.html')

def is_donor(user):
    return user.groups.filter(name='DONOR').exists()

def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()


def afterlogin_view(request):
    if is_donor(request.user):      
        return redirect('donor/donor-dashboard')
                
    elif is_patient(request.user):
        return redirect('patient/patient-dashboard')
    else:
        return redirect('admin-dashboard')

@login_required(login_url='adminlogin')
def admin_dashboard_view(request):

    #totalunit = models.Stock.objects.aggregate(Sum('unit'))
    stu = "select sum(unit) from bloodbank.blood_stock;"
    cursor.execute(stu)
    stut=cursor.fetchall()
    totalunit = int(stut[0][0])
    s1 = "SELECT unit FROM bloodbank.blood_stock where bloodgroup='A+';"
    cursor.execute(s1)
    apt = cursor.fetchall()
    ap=int(apt[0][0])
    s2 = "SELECT unit FROM bloodbank.blood_stock where bloodgroup='A-';"
    cursor.execute(s2)
    ant = cursor.fetchall()
    an = int(ant[0][0])
    s3 = "SELECT unit FROM bloodbank.blood_stock where bloodgroup='B+';"
    cursor.execute(s3)
    bpt = cursor.fetchall()
    bp = int(bpt[0][0])
    s4 = "SELECT unit FROM bloodbank.blood_stock where bloodgroup='B-';"
    cursor.execute(s4)
    bnt = cursor.fetchall()
    bn = int(bnt[0][0])
    s5 = "SELECT unit FROM bloodbank.blood_stock where bloodgroup='AB+';"
    cursor.execute(s5)
    abpt = cursor.fetchall()
    abp = int(abpt[0][0])
    s6 = "SELECT unit FROM bloodbank.blood_stock where bloodgroup='AB-';"
    cursor.execute(s6)
    abnt = cursor.fetchall()
    abn = int(abnt[0][0])
    s7 = "SELECT unit FROM bloodbank.blood_stock where bloodgroup='O+';"
    cursor.execute(s7)
    opt = cursor.fetchall()
    op=int(opt[0][0])
    s8 = "SELECT unit FROM bloodbank.blood_stock where bloodgroup='O-';"
    cursor.execute(s8)
    opnt = cursor.fetchall()
    opn=int(opnt[0][0])
    tr="select count(*) from bloodbank.blood_bloodrequest;"
    cursor.execute(tr)
    trt=cursor.fetchall()
    total_request = int(trt[0][0])
    td="select count(*) from bloodbank.donor_donor;"
    cursor.execute(td)
    tdt=cursor.fetchall()
    total_donors = int(tdt[0][0])
    tar="select count(status) from bloodbank.blood_bloodrequest where status='Approved';"
    cursor.execute(tar)
    tart=cursor.fetchall()
    total_approved_requests=int(tart[0][0])

    dict={
        'A1':ap,
        'A2':an,
        'B1':bp,
        'B2':bn,
        'AB1':abp,
        'AB2':abn,
        'O1':op,
        'O2':opn,
        'totaldonors': total_donors,
        'totalbloodunit': totalunit,
        'totalrequest': total_request,
        'totalapprovedrequest': total_approved_requests
    }
    return render(request,'blood/admin_dashboard.html',context=dict)

@login_required(login_url='adminlogin')
def admin_blood_view(request):
    s1 = "SELECT unit FROM bloodbank.blood_stock where bloodgroup='A+';"
    cursor.execute(s1)
    apt = cursor.fetchall()
    ap = int(apt[0][0])
    s2 = "SELECT unit FROM bloodbank.blood_stock where bloodgroup='A-';"
    cursor.execute(s2)
    ant = cursor.fetchall()
    an = int(ant[0][0])
    s3 = "SELECT unit FROM bloodbank.blood_stock where bloodgroup='B+';"
    cursor.execute(s3)
    bpt = cursor.fetchall()
    bp = int(bpt[0][0])
    s4 = "SELECT unit FROM bloodbank.blood_stock where bloodgroup='B-';"
    cursor.execute(s4)
    bnt = cursor.fetchall()
    bn = int(bnt[0][0])
    s5 = "SELECT unit FROM bloodbank.blood_stock where bloodgroup='AB+';"
    cursor.execute(s5)
    abpt = cursor.fetchall()
    abp = int(abpt[0][0])
    s6 = "SELECT unit FROM bloodbank.blood_stock where bloodgroup='AB-';"
    cursor.execute(s6)
    abnt = cursor.fetchall()
    abn = int(abnt[0][0])
    s7 = "SELECT unit FROM bloodbank.blood_stock where bloodgroup='O+';"
    cursor.execute(s7)
    opt = cursor.fetchall()
    op = int(opt[0][0])
    s8 = "SELECT unit FROM bloodbank.blood_stock where bloodgroup='O-';"
    cursor.execute(s8)
    opnt = cursor.fetchall()
    opn = int(opnt[0][0])
    dict = {
        'A1': ap,
        'A2': an,
        'B1': bp,
        'B2': bn,
        'AB1': abp,
        'AB2': abn,
        'O1': op,
        'O2': opn
    }
    if request.method == 'POST':
        bloodForm = forms.BloodForm(request.POST)
        if bloodForm.is_valid():
            bloodgroup = bloodForm.cleaned_data['bloodgroup']
            unittoupdate = bloodForm.cleaned_data['unit']
            stm = "update blood_stock set unit = %s where bloodgroup= %s;"
            val=(unittoupdate,bloodgroup)
            cursor.execute(stm,val)
            db.commit()
        return HttpResponseRedirect('admin-blood')
    return render(request, 'blood/admin_blood.html', context=dict)


@login_required(login_url='adminlogin')
def admin_donor_view(request):
    stmt = "select donor_donor.id,concat(auth_user.first_name,' ',auth_user.last_name) as name,bloodgroup,address,mobile from donor_donor join auth_user on donor_donor.user_id=auth_user.id;"
    cursor.execute(stmt)
    donors = cursor.fetchall()
    db.commit()
    return render(request, 'blood/admin_donor.html', {'donors': donors})

@login_required(login_url='adminlogin')
def update_donor_view(request,pk):
    donor=dmodels.Donor.objects.get(id=pk)
    user=dmodels.User.objects.get(id=donor.user_id)
    userForm=dforms.DonorUserForm(instance=user)
    donorForm=dforms.DonorForm(request.FILES,instance=donor)
    mydict={'userForm':userForm,'donorForm':donorForm}
    if request.method=='POST':
        userForm=dforms.DonorUserForm(request.POST,instance=user)
        donorForm=dforms.DonorForm(request.POST,request.FILES,instance=donor)
        if userForm.is_valid() and donorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            donor=donorForm.save(commit=False)
            donor.user=user
            donor.bloodgroup=donorForm.cleaned_data['bloodgroup']
            donor.save()
            return redirect('admin-donor')
    return render(request,'blood/update_donor.html',context=mydict)


@login_required(login_url='adminlogin')
def delete_donor_view(request,pk):
    donor=dmodels.Donor.objects.get(id=pk)
    user=User.objects.get(id=donor.user_id)
    user.delete()
    donor.delete()
    return HttpResponseRedirect('/admin-donor')

@login_required(login_url='adminlogin')
def admin_patient_view(request):
    stmt = " select patient_patient.id,concat(auth_user.first_name,' ',auth_user.last_name) as name,age,bloodgroup,disease,doctorname,address,mobile from patient_patient join auth_user on patient_patient.user_id=auth_user.id;"
    cursor.execute(stmt)
    patients = cursor.fetchall()
    db.commit()
    #patients=pmodels.Patient.objects.raw("SELECT * FROM bbms.blood_bloodrequest")
    return render(request,'blood/admin_patient.html',{'patients':patients})


@login_required(login_url='adminlogin')
def update_patient_view(request,pk):
    patient=pmodels.Patient.objects.get(id=pk)
    user=pmodels.User.objects.get(id=patient.user_id)
    userForm=pforms.PatientUserForm(instance=user)
    patientForm=pforms.PatientForm(request.FILES,instance=patient)
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=pforms.PatientUserForm(request.POST,instance=user)
        patientForm=pforms.PatientForm(request.POST,request.FILES,instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            patient.bloodgroup=patientForm.cleaned_data['bloodgroup']
            patient.save()
            return redirect('admin-patient')
    return render(request,'blood/update_patient.html',context=mydict)


@login_required(login_url='adminlogin')
def delete_patient_view(request,pk):
    patient=pmodels.Patient.objects.get(id=pk)
    user=User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return HttpResponseRedirect('/admin-patient')

@login_required(login_url='adminlogin')
def admin_request_view(request):
    stmt = " select * from bloodbank.blood_bloodrequest where status='Pending';"
    cursor.execute(stmt)
    requests = cursor.fetchall()
    return render(request, 'blood/admin_request.html', {'requests': requests})


@login_required(login_url='adminlogin')
def admin_request_history_view(request):
    stmt = " select * from bloodbank.blood_bloodrequest;"
    cursor.execute(stmt)
    requests = cursor.fetchall()
    return render(request, 'blood/admin_request_history.html', {'requests': requests})


@login_required(login_url='adminlogin')
def admin_donation_view(request):
    stmt="select t2.id,t1.name,t2.age,t2.bloodgroup,t2.unit,t2.date,t2.status from donor_blooddonate as t2 join (select concat(auth_user.first_name,' ',auth_user.last_name) as name,donor_donor.id as id from donor_donor join auth_user on donor_donor.user_id=auth_user.id) as t1 on t2.donor_id=t1.id;"
    cursor.execute(stmt)
    donations=cursor.fetchall()
    return render(request, 'blood/admin_donation.html', {'donations': donations})

@login_required(login_url='adminlogin')
def update_approve_status_view(request,pk):
    message=None
    stmt="SELECT * FROM bloodbank.blood_bloodrequest where id=%s;"
    e1=(pk)
    cursor.execute(stmt,e1)
    res=cursor.fetchall()
    for i in range(len(res)):
        print(res)
        bloodgroup= res[i][4]
        unit=res[i][5]
        stmt2="select unit from bloodbank.blood_stock where bloodgroup=%s;"
        val=(bloodgroup)
        cursor.execute(stmt2,val)
        res2=cursor.fetchall()
        avalunits=res2[i][0]
        if avalunits>=unit:
            toup=avalunits-unit
            stmt3="update bloodbank.blood_stock set unit = %s where bloodgroup = %s;"
            val2=(toup,bloodgroup)
            cursor.execute(stmt3,val2)
            stmt4 = "update bloodbank.blood_bloodrequest set status = 'Approved' where id = %s;"
            cursor.execute(stmt4, e1)
            db.commit()
            requests = cursor.fetchall()
        else:
            message = "Stock Doest Not Have Enough Blood To Approve This Request, Only " + str(avalunits) + " Unit Available"
            stmt5 = "update bloodbank.blood_bloodrequest set status = 'Pending' where id = %s;"
            cursor.execute(stmt5, e1)
            db.commit()
            requests=cursor.fetchall()
    return render(request, 'blood/admin_request.html', {'requests': requests, 'message': message})


@login_required(login_url='adminlogin')
def update_reject_status_view(request,pk):
    e1=(pk)
    stmt="update bloodbank.blood_bloodrequest set status='Rejected' where id=%s;"
    cursor.execute(stmt,e1)
    db.commit()
    return HttpResponseRedirect('/admin-request')

@login_required(login_url='adminlogin')
def approve_donation_view(request,pk):
    e1=(pk)
    stmt="select bloodgroup,unit from bloodbank.donor_blooddonate where id=%s;"
    cursor.execute(stmt,e1)
    res=cursor.fetchall()
    bg,uni=res[0][0],res[0][1]
    e2=(bg)
    stmt2="select unit from bloodbank.blood_stock where bloodgroup = %s;"
    cursor.execute(stmt2,e2)
    res2=cursor.fetchall()
    resuni = res2[0][0]+uni
    stmt3="update bloodbank.blood_stock set unit = %s where bloodgroup = %s;"
    e3=(resuni,bg)
    cursor.execute(stmt3,e3)
    stmt4 ="update bloodbank.donor_blooddonate set status='Approved' where id = %s;"
    cursor.execute(stmt4,e1)
    db.commit()
    return HttpResponseRedirect('/admin-donation')

@login_required(login_url='adminlogin')
def reject_donation_view(request,pk):
    e1 = (pk)
    stmt = "update bloodbank.donor_blooddonate set status='Rejected' where id=%s;"
    cursor.execute(stmt, e1)
    db.commit()
    return HttpResponseRedirect('/admin-donation')


