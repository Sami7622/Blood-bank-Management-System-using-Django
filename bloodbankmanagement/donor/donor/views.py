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

def donor_signup_view(request):
    userForm=forms.DonorUserForm()
    donorForm=forms.DonorForm()
    mydict={'userForm':userForm,'donorForm':donorForm}
    if request.method=='POST':
        userForm=forms.DonorUserForm(request.POST)
        donorForm=forms.DonorForm(request.POST,request.FILES)
        if userForm.is_valid() and donorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            donor=donorForm.save(commit=False)
            donor.user=user
            donor.bloodgroup=donorForm.cleaned_data['bloodgroup']
            donor.save()
            my_donor_group = Group.objects.get_or_create(name='DONOR')
            my_donor_group[0].user_set.add(user)
            db.commit()
        return HttpResponseRedirect('donorlogin')
    return render(request,'donor/donorsignup.html',context=mydict)


def donor_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    e1=(donor)
    #stmt="ISNULL('Select * from bloodbank.donor_blooddonate where donor_id = %s and status='Pending' group by donor_id',0);"
    stmt="select ifnull((select count(id) from bloodbank.donor_blooddonate where donor_id = %s and status='Pending' group by donor_id),0) as res;"
    cursor.execute(stmt,e1)
    request_pending=cursor.fetchall()
    stmt2 = "select ifnull((select count(id) from bloodbank.donor_blooddonate where donor_id = %s and status='Approved' group by donor_id),0) as res;"
    cursor.execute(stmt2, e1)
    request_approved = cursor.fetchall()
    stmt3 = "select ifnull((select count(id) from bloodbank.donor_blooddonate where donor_id = %s and status='Rejected' group by donor_id),0) as res;"
    cursor.execute(stmt3, e1)
    request_rejected= cursor.fetchall()
    stmt4 = "select ifnull((select count(id) from bloodbank.donor_blooddonate where donor_id = %s group by donor_id),0) as res;"
    cursor.execute(stmt4, e1)
    request_made = cursor.fetchall()
    dict={
        'requestpending': request_pending,
        'requestapproved': request_approved,
        'requestmade': request_made,
        'requestrejected': request_rejected,
    }
    return render(request,'donor/donor_dashboard.html',context=dict)

def donor_dashboard_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    dict={
        'requestpending': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).filter(status='Pending').count(),
        'requestapproved': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).filter(status='Approved').count(),
        'requestmade': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).count(),
        'requestrejected': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).filter(status='Rejected').count(),
    }
    return render(request,'donor/donor_dashboard.html',context=dict)


def donate_blood_view(request):
    donation_form=forms.DonationForm()
    if request.method=='POST':
        donation_form=forms.DonationForm(request.POST)
        if donation_form.is_valid():
            blood_donate=donation_form.save(commit=False)
            blood_donate.bloodgroup=donation_form.cleaned_data['bloodgroup']
            donor= models.Donor.objects.get(user_id=request.user.id)
            blood_donate.donor=donor
            blood_donate.save()
            return HttpResponseRedirect('donation-history')  
    return render(request,'donor/donate_blood.html',{'donation_form':donation_form})


def view_donation(request):
    v=request.user.id
    e2=(v)
    donor= models.Donor.objects.raw("select first_name from auth_user where id=request.user.id;")
    cursor.execute(donor)
    donor2=cursor.fetchall()
    #donor = models.Donor.objects.get(user_id=request.user.id)
    print(donor2)
    e1=(donor2)
    print(e1)
    stmt="select * from bloodbank.donor_blooddonate where donor_id=(select id from auth_user where first_name=%s);"
    cursor.execute(stmt,e1)
    donations=cursor.fetchall()
    return render(request, 'donor/donation_history.html', {'donations': donations})

def donation_history_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    donations=models.BloodDonate.objects.all().filter(donor=donor)
    return render(request,'donor/donation_history.html',{'donations':donations})

def make_request_view(request):
    request_form=bforms.RequestForm()
    if request.method=='POST':
        request_form=bforms.RequestForm(request.POST)
        if request_form.is_valid():
            blood_request=request_form.save(commit=False)
            blood_request.bloodgroup=request_form.cleaned_data['bloodgroup']
            donor= models.Donor.objects.get(user_id=request.user.id)
            blood_request.request_by_donor=donor
            blood_request.save()
            return HttpResponseRedirect('request-history')  
    return render(request,'donor/makerequest.html',{'request_form':request_form})

def request_history_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    blood_request=bmodels.BloodRequest.objects.all().filter(request_by_donor=donor)
    return render(request,'donor/request_history.html',{'blood_request':blood_request})
