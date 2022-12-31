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
from blood import forms as bforms
from blood import models as bmodels
import pymysql.cursors
db = pymysql.connect(host='127.0.0.1',
                         user='root',
                         password='9515290749',
                         database='bloodbank')
cursor = db.cursor()
def patient_signup_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            patient.bloodgroup=patientForm.cleaned_data['bloodgroup']
            patient.save()
            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)
            db.commit()
        return HttpResponseRedirect('patientlogin')
    return render(request,'patient/patientsignup.html',context=mydict)


def patient_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    e1=(patient)
    #stmt="ISNULL('Select * from bloodbank.donor_blooddonate where donor_id = %s and status='Pending' group by donor_id',0);"
    stmt="select ifnull((select count(id) from bloodbank.blood_bloodrequest where request_by_patient_id = %s and status='Pending' group by request_by_patient_id),0) as res;"
    cursor.execute(stmt,e1)
    request_pending=cursor.fetchall()
    stmt2 = "select ifnull((select count(id) from bloodbank.blood_bloodrequest where request_by_patient_id = %s and status='Approved' group by request_by_patient_id),0) as res;"
    cursor.execute(stmt2, e1)
    request_approved = cursor.fetchall()
    stmt3 = "select ifnull((select count(id) from bloodbank.blood_bloodrequest where request_by_patient_id = %s and status='Rejected' group by request_by_patient_id),0) as res;"
    cursor.execute(stmt3, e1)
    request_rejected= cursor.fetchall()
    stmt4 = "select ifnull((select count(id) from bloodbank.blood_bloodrequest where request_by_patient_id = %s group by donor_id),0) as res;"
    cursor.execute(stmt4, e1)
    request_made = cursor.fetchall()
    dict={
        'requestpending': request_pending,
        'requestapproved': request_approved,
        'requestmade': request_made,
        'requestrejected': request_rejected,
    }
    return render(request, 'patient/patient_dashboard.html', context=dict)

def patient_dashboard_view(request):
    patient= models.Patient.objects.get(user_id=request.user.id)
    dict={
        'requestpending': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Pending').count(),
        'requestapproved': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Approved').count(),
        'requestmade': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).count(),
        'requestrejected': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Rejected').count(),
    }
    return render(request,'patient/patient_dashboard.html',context=dict)

def make_request_view(request):
    request_form=bforms.RequestForm()
    if request.method=='POST':
        request_form=bforms.RequestForm(request.POST)
        if request_form.is_valid():
            blood_request=request_form.save(commit=False)
            blood_request.bloodgroup=request_form.cleaned_data['bloodgroup']
            patient= models.Patient.objects.get(user_id=request.user.id)
            blood_request.request_by_patient=patient
            blood_request.save()
            return HttpResponseRedirect('my-request')
    return render(request,'patient/makerequest.html',{'request_form':request_form})


def view_bloodrequests(request):
    v=request.user.id
    e2=(v)
    patient= models.Donor.objects.raw("select first_name from auth_user where id=request.user.id;")
    cursor.execute(patient)
    p2=cursor.fetchall()
    e1=(p2)
    print(e1)
    stmt="select * from bloodbank.blood_bloodrequest where request_by_patient_id=(select id from auth_user where first_name=%s);"
    cursor.execute(stmt,e1)
    receipients=cursor.fetchall()
    return render(request, 'patient/patient_dashboard.html', {'receipients':receipients})


def my_request_view(request):
    patient= models.Patient.objects.get(user_id=request.user.id)
    blood_request=bmodels.BloodRequest.objects.all().filter(request_by_patient=patient)
    return render(request,'patient/my_request.html',{'blood_request':blood_request})

