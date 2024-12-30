from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required,user_passes_test
from datetime import datetime,timedelta,date
from django.conf import settings
from django.contrib.auth import logout


def home_view(request):
    return render(request, 'index.html')


def adminclick_view(request):
    return render(request, 'adminclick.html')


def doctorclick_view(request):
    return render(request, 'doctorclick.html')


def patientclick_view(request):
    return render(request, 'patientclick.html')

def receptionistclick_view(request):
    return render(request,"receptionistclick.html")



def admin_signup_view(request):
    form=forms.AdminSignupForm()
    if request.method=='POST':
        form=forms.AdminSignupForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.set_password(user.password)
            user.save()
            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)
            return HttpResponseRedirect('adminlogin')
    return render(request,'adminsignup.html',{'form':form})




def doctor_signup_view(request):
    userForm=forms.DoctorUserForm()
    doctorForm=forms.DoctorForm()
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST)
        doctorForm=forms.DoctorForm(request.POST,request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            doctor=doctorForm.save(commit=False)
            doctor.user=user
            doctor=doctor.save()
            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)
        return HttpResponseRedirect('doctorlogin')
    return render(request,'doctorsignup.html',context=mydict)


def patient_signup_view(request):
    userForm = forms.PatientUserForm()
    patientForm = forms.PatientForm()
    mydict = {'userForm': userForm, 'patientForm': patientForm}

    if request.method == 'POST':
        userForm = forms.PatientUserForm(request.POST)
        patientForm = forms.PatientForm(request.POST, request.FILES)

        if userForm.is_valid() and patientForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(userForm.cleaned_data['password'])  # Hash the password
            user.save()

            patient = patientForm.save(commit=False)
            patient.user = user
            patient.assignedDoctorId = request.POST.get('assignedDoctorId')
            patient.save()  # Save the patient instance

            my_patient_group, created = Group.objects.get_or_create(name='PATIENT')
            my_patient_group.user_set.add(user)

            return redirect('patientlogin')  # Redirect to the login page

    return render(request, 'patientsignup.html', context=mydict)


def receptionist_signup_view(request):
    userForm=forms.ReceptionistUserForm()
    receptionistForm=forms.ReceptionistForm()
    mydict={'userForm':userForm,'receptionistForm':receptionistForm}
    if request.method=='POST':
        userForm=forms.ReceptionistUserForm(request.POST)
        receptionistForm=forms.ReceptionistForm(request.POST,request.FILES)
        if userForm.is_valid() and receptionistForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            receptionist=receptionistForm.save(commit=False)
            receptionist.user=user
            receptionist=receptionist.save()
            my_receptionist_group = Group.objects.get_or_create(name='RECEPTIONIST')
            my_receptionist_group[0].user_set.add(user)
        return HttpResponseRedirect('receptionistlogin')
    return render(request,'receptionistsignup.html',context=mydict)




def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()
def is_doctor(user):
    return user.groups.filter(name='DOCTOR').exists()
def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()
def is_receptionist(user):
    return user.groups.filter(name='RECEPTIONIST').exists()


def afterlogin_view(request):
    if is_admin(request.user):
        return redirect('admin-dashboard')
    elif is_doctor(request.user):
        accountapproval=models.Doctor.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('doctor-dashboard')
        else:
            return render(request,'doctor_wait_for_approval.html')
    elif is_patient(request.user):
        accountapproval=models.Patient.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('patient-dashboard')
        else:
            return render(request,'patient_wait_for_approval.html')
    elif is_receptionist(request.user):
        accountapproval=models.Receptionist.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('receptionist-dashboard')
        else:
            return render(request,'receptionist_wait_for_approval.html')

    return render(request,'wrong_credentials.html')
    

def logout_user(request):
    logout(request)
    return redirect("home")

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    #for both table in admin dashboard
    doctors=models.Doctor.objects.all().order_by('-id')
    patients=models.Patient.objects.all().order_by('-id')
    receptionist=models.Receptionist.objects.all().order_by("-id")
    #for three cards
    doctorcount=models.Doctor.objects.all().filter(status=True).count()
    pendingdoctorcount=models.Doctor.objects.all().filter(status=False).count()

    patientcount=models.Patient.objects.all().filter(status=True).count()
    pendingpatientcount=models.Patient.objects.all().filter(status=False).count()

    receptionistcount=models.Receptionist.objects.all().filter(status=True).count()
    pendingreceptionistcount=models.Receptionist.objects.all().filter(status=False).count()
    

    appointmentcount=models.Appointment.objects.all().filter(status=True).count()
    pendingappointmentcount=models.Appointment.objects.all().filter(status=False).count()
    mydict={
    'doctors':doctors,
    'patients':patients,
    "receptionist":receptionist,
    'doctorcount':doctorcount,
    'pendingdoctorcount':pendingdoctorcount,
    'patientcount':patientcount,
    'pendingpatientcount':pendingpatientcount,
    'receptionistcount':receptionistcount,
    'pendingreceptionistcount':pendingreceptionistcount,
    'appointmentcount':appointmentcount,
    'pendingappointmentcount':pendingappointmentcount,
    }
    return render(request,'admin_dashboard.html',context=mydict)


# this view for sidebar click on admin page
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_doctor_view(request):
    return render(request,'admin_doctor.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    return render(request,'admin_view_doctor.html',{'doctors':doctors})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_doctor_from_hospital_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-view-doctor')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)

    userForm=forms.DoctorUserForm(instance=user)
    doctorForm=forms.DoctorForm(request.FILES,instance=doctor)
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST,instance=user)
        doctorForm=forms.DoctorForm(request.POST,request.FILES,instance=doctor)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            doctor=doctorForm.save(commit=False)
            doctor.status=True
            doctor.save()
            return redirect('admin-view-doctor')
    return render(request,'admin_update_doctor.html',context=mydict)




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_doctor_view(request):
    userForm=forms.DoctorUserForm()
    doctorForm=forms.DoctorForm()
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST)
        doctorForm=forms.DoctorForm(request.POST, request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            doctor=doctorForm.save(commit=False)
            doctor.user=user
            doctor.status=True
            doctor.save()

            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-doctor')
    return render(request,'admin_add_doctor.html',context=mydict)




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_doctor_view(request):
    #those whose approval are needed
    doctors=models.Doctor.objects.all().filter(status=False)
    return render(request,'admin_approve_doctor.html',{'doctors':doctors})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    doctor.status=True
    doctor.save()
    return redirect(reverse('admin-approve-doctor'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-approve-doctor')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_specialisation_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    return render(request,'admin_view_doctor_specialisation.html',{'doctors':doctors})




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_receptionist_view(request):
    return render(request,'admin_receptionist.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_receptionist_view(request):
    receptionist=models.Receptionist.objects.all().filter(status=True)
    return render(request,'admin_view_receptionist.html',{'receptionist':receptionist})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_receptionist_from_hospital_view(request,pk):
    receptionist=models.Receptionist.objects.get(id=pk)
    user=models.User.objects.get(id=receptionist.user_id)
    user.delete()
    receptionist.delete()
    return redirect('admin-view-receptionist')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_receptionist_view(request,pk):
    receptionist=models.Receptionist.objects.get(id=pk)
    user=models.User.objects.get(id=receptionist.user_id)

    userForm=forms.ReceptionistUserForm(instance=user)
    receptionistForm=forms.ReceptionistForm(request.FILES,instance=receptionist)
    mydict={'userForm':userForm,'receptionistForm':receptionistForm}
    if request.method=='POST':
        userForm=forms.ReceptionistUserForm(request.POST,instance=user)
        receptionistForm=forms.ReceptionistForm(request.POST,request.FILES,instance=receptionist)
        if userForm.is_valid() and receptionistForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            receptionist=receptionistForm.save(commit=False)
            receptionist.status=True
            receptionist.save()
            return redirect('admin-view-receptionist')
    return render(request,'admin_update_receptionist.html',context=mydict)




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_receptionist_view(request):
    userForm=forms.ReceptionistUserForm()
    ReceptionistForm=forms.ReceptionistForm()
    mydict={'userForm':userForm,'ReceptionistForm':ReceptionistForm}
    if request.method=='POST':
        userForm=forms.ReceptionistUserForm(request.POST)
        ReceptionistForm=forms.ReceptionistForm(request.POST, request.FILES)
        if userForm.is_valid() and ReceptionistForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            receptionist=ReceptionistForm.save(commit=False)
            receptionist.user=user
            receptionist.status=True
            receptionist.save()

            my_doctor_group = Group.objects.get_or_create(name='RECEPTIONIST')
            my_doctor_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-receptionist')
    return render(request,'admin_add_receptionist.html',context=mydict)




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_receptionist_view(request):
    #those whose approval are needed
    receptionist=models.Receptionist.objects.all().filter(status=False)
    return render(request,'admin_approve_receptionist.html',{'receptionist':receptionist})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_receptionist_view(request,pk):
    receptionist=models.Receptionist.objects.get(id=pk)
    receptionist.status=True
    receptionist.save()
    return redirect(reverse('admin-approve-receptionist'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_receptionist_view(request,pk):
    receptionist=models.Receptionist.objects.get(id=pk)
    user=models.User.objects.get(id=receptionist.user_id)
    user.delete()
    receptionist.delete()
    return redirect('admin-approve-receptionist')




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_patient_view(request):
    return render(request,'admin_patient.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True)
    return render(request,'admin_view_patient.html',{'patients':patients})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_patient_from_hospital_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-view-patient')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)

    userForm=forms.PatientUserForm(instance=user)
    patientForm=forms.PatientForm(request.FILES,instance=patient)
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST,instance=user)
        patientForm=forms.PatientForm(request.POST,request.FILES,instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.status=True
            patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            patient.save()
            return redirect('admin-view-patient')
    return render(request,'admin_update_patient.html',context=mydict)





@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_patient_view(request):
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
            patient.status=True
            patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            patient.save()

            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-patient')
    return render(request,'admin_add_patient.html',context=mydict)




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_patient_view(request):
    patients=models.Patient.objects.all().filter(status=False)
    return render(request,'admin_approve_patient.html',{'patients':patients})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    patient.status=True
    patient.save()
    return redirect(reverse('admin-approve-patient'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-approve-patient')


#--------------------- FOR DISCHARGING PATIENT BY ADMIN START-------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_discharge_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True)
    return render(request,'admin_discharge_patient.html',{'patients':patients})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def discharge_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    days=(date.today()-patient.admitDate)
    assignedDoctor=models.User.objects.all().filter(id=patient.assignedDoctorId)
    d=days.days 
    patientDict={
        'patientId':pk,
        'name':patient.get_name,
        'mobile':patient.mobile,
        'address':patient.address,
        'symptoms':patient.symptoms,
        'admitDate':patient.admitDate,
        'todayDate':date.today(),
        'day':d,
        'assignedDoctorName':assignedDoctor[0].first_name,
    }
    if request.method == 'POST':
        feeDict ={
            'roomCharge':int(request.POST['roomCharge'])*int(d),
            'doctorFee':request.POST['doctorFee'],
            'medicineCost' : request.POST['medicineCost'],
            'OtherCharge' : request.POST['OtherCharge'],
            'total':(int(request.POST['roomCharge'])*int(d))+int(request.POST['doctorFee'])+int(request.POST['medicineCost'])+int(request.POST['OtherCharge'])
        }
        patientDict.update(feeDict)

        pDD=models.PatientDischargeDetails()
        pDD.patientId=pk
        pDD.patientName=patient.get_name
        pDD.assignedDoctorName=assignedDoctor[0].first_name
        pDD.address=patient.address
        pDD.mobile=patient.mobile
        pDD.symptoms=patient.symptoms
        pDD.admitDate=patient.admitDate
        pDD.releaseDate=date.today()
        pDD.daySpent=int(d)
        pDD.medicineCost=int(request.POST['medicineCost'])
        pDD.roomCharge=int(request.POST['roomCharge'])*int(d)
        pDD.doctorFee=int(request.POST['doctorFee'])
        pDD.OtherCharge=int(request.POST['OtherCharge'])
        pDD.total=(int(request.POST['roomCharge'])*int(d))+int(request.POST['doctorFee'])+int(request.POST['medicineCost'])+int(request.POST['OtherCharge'])
        pDD.save()
        return render(request,'patient_final_bill.html',context=patientDict)
    return render(request,'patient_generate_bill.html',context=patientDict)






@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_appointment_view(request):
    return render(request,'admin_appointment.html')




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_appointment_view(request):
    # Fetch all appointments that are either confirmed (status=True) or emergency appointments
    appointments = models.Appointment.objects.filter(status=True) | models.Appointment.objects.filter(emergency=True)

    return render(request, 'admin_view_appointment.html', {'appointments': appointments})




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_appointment_view(request):
    appointmentForm=forms.AppointmentForm()
    mydict={'appointmentForm':appointmentForm,}
    if request.method=='POST':
        appointmentForm=forms.AppointmentForm(request.POST)
        if appointmentForm.is_valid():
            appointment=appointmentForm.save(commit=False)
            appointment.doctorId=request.POST.get('doctorId')
            appointment.patientId=request.POST.get('patientId')
            appointment.doctorName=models.User.objects.get(id=request.POST.get('doctorId')).first_name
            appointment.patientName=models.User.objects.get(id=request.POST.get('patientId')).first_name
            appointment.status=True
            appointment.save()
        return HttpResponseRedirect('admin-view-appointment')
    return render(request,'admin_add_appointment.html',context=mydict)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_appointment_view(request):
    #those whose approval are needed
    appointments=models.Appointment.objects.all().filter(status=False)
    return render(request,'admin_approve_appointment.html',{'appointments':appointments})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.status=True
    appointment.save()
    return redirect(reverse('admin-approve-appointment'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    return redirect('admin-approve-appointment')

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_dashboard_view(request):
    #for three cards
    patientcount=models.Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id).count()
    appointmentcount=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id).count()
    patientdischarged=models.PatientDischargeDetails.objects.all().distinct().filter(assignedDoctorName=request.user.first_name).count()

    #for  table in doctor dashboard
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id).order_by('-id')
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid).order_by('-id')
    appointments=zip(appointments,patients)
    mydict={
    'patientcount':patientcount,
    'appointmentcount':appointmentcount,
    'patientdischarged':patientdischarged,
    'appointments':appointments,
    'doctor':models.Doctor.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
    }
    return render(request,'doctor_dashboard.html',context=mydict)



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_patient_view(request):
    mydict={
    'doctor':models.Doctor.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
    }
    return render(request,'doctor_patient.html',context=mydict)



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id)
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'doctor_view_patient.html',{'patients':patients,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_discharge_patient_view(request):
    dischargedpatients=models.PatientDischargeDetails.objects.all().distinct().filter(assignedDoctorName=request.user.first_name)
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'doctor_view_discharge_patient.html',{'dischargedpatients':dischargedpatients,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'doctor_appointment.html',{'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'doctor_view_appointment.html',{'appointments':appointments,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_delete_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'doctor_delete_appointment.html',{'appointments':appointments,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def delete_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'doctor_delete_appointment.html',{'appointments':appointments,'doctor':doctor})



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_dashboard_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id)
    doctor=models.Doctor.objects.get(user_id=patient.assignedDoctorId)
    mydict={
    'patient':patient,
    'doctorName':doctor.get_name,
    'doctorMobile':doctor.mobile,
    'doctorAddress':doctor.address,
    'symptoms':patient.symptoms,
    'doctorDepartment':doctor.department,
    'admitDate':patient.admitDate,
    }
    return render(request,'patient_dashboard.html',context=mydict)



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_appointment_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) 
    return render(request,'patient_appointment.html',{'patient':patient})



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_book_appointment_view(request):
    appointmentForm=forms.PatientAppointmentForm()
    patient=models.Patient.objects.get(user_id=request.user.id) 
    message=None
    mydict={'appointmentForm':appointmentForm,'patient':patient,'message':message}
    if request.method=='POST':
        appointmentForm=forms.PatientAppointmentForm(request.POST)
        if appointmentForm.is_valid():
            print(request.POST.get('doctorId'))
            desc=request.POST.get('description')

            doctor=models.Doctor.objects.get(user_id=request.POST.get('doctorId'))
            
            if doctor.department == 'Cardiologist':
                if 'heart' in desc:
                    pass
                else:
                    print('else')
                    message="Please Choose Doctor According To Disease"
                    return render(request,'patient_book_appointment.html',{'appointmentForm':appointmentForm,'patient':patient,'message':message})


            if doctor.department == 'Dermatologists':
                if 'skin' in desc:
                    pass
                else:
                    print('else')
                    message="Please Choose Doctor According To Disease"
                    return render(request,'patient_book_appointment.html',{'appointmentForm':appointmentForm,'patient':patient,'message':message})

            if doctor.department == 'Emergency Medicine Specialists':
                if 'fever' in desc:
                    pass
                else:
                    print('else')
                    message="Please Choose Doctor According To Disease"
                    return render(request,'patient_book_appointment.html',{'appointmentForm':appointmentForm,'patient':patient,'message':message})

            if doctor.department == 'Allergists/Immunologists':
                if 'allergy' in desc:
                    pass
                else:
                    print('else')
                    message="Please Choose Doctor According To Disease"
                    return render(request,'patient_book_appointment.html',{'appointmentForm':appointmentForm,'patient':patient,'message':message})

            if doctor.department == 'Anesthesiologists':
                if 'surgery' in desc:
                    pass
                else:
                    print('else')
                    message="Please Choose Doctor According To Disease"
                    return render(request,'patient_book_appointment.html',{'appointmentForm':appointmentForm,'patient':patient,'message':message})

            if doctor.department == 'Colon and Rectal Surgeons':
                if 'cancer' in desc:
                    pass
                else:
                    print('else')
                    message="Please Choose Doctor According To Disease"
                    return render(request,'patient_book_appointment.html',{'appointmentForm':appointmentForm,'patient':patient,'message':message})





            appointment=appointmentForm.save(commit=False)
            appointment.doctorId=request.POST.get('doctorId')
            appointment.patientId=request.user.id 
            appointment.doctorName=models.User.objects.get(id=request.POST.get('doctorId')).first_name
            appointment.patientName=request.user.first_name
            appointment.status=False
            appointment.save()
        return HttpResponseRedirect('patient-view-appointment')
    return render(request,'patient_book_appointment.html',context=mydict)





@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_view_appointment_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    appointments=models.Appointment.objects.all().filter(patientId=request.user.id)
    return render(request,'patient_view_appointment.html',{'appointments':appointments,'patient':patient})



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_discharge_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    dischargeDetails=models.PatientDischargeDetails.objects.all().filter(patientId=patient.id).order_by('-id')[:1]
    patientDict=None
    if dischargeDetails:
        patientDict ={
        'is_discharged':True,
        'patient':patient,
        'patientId':patient.id,
        'patientName':patient.get_name,
        'assignedDoctorName':dischargeDetails[0].assignedDoctorName,
        'address':patient.address,
        'mobile':patient.mobile,
        'symptoms':patient.symptoms,
        'admitDate':patient.admitDate,
        'releaseDate':dischargeDetails[0].releaseDate,
        'daySpent':dischargeDetails[0].daySpent,
        'medicineCost':dischargeDetails[0].medicineCost,
        'roomCharge':dischargeDetails[0].roomCharge,
        'doctorFee':dischargeDetails[0].doctorFee,
        'OtherCharge':dischargeDetails[0].OtherCharge,
        'total':dischargeDetails[0].total,
        }
        print(patientDict)
    else:
        patientDict={
            'is_discharged':False,
            'patient':patient,
            'patientId':request.user.id,
        }
    return render(request,'patient_discharge.html',context=patientDict)






def aboutus_view(request):
    return render(request,'aboutus.html')

from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from . import forms
from django.contrib import messages

def contactus_view(request):
    if request.method == 'POST':
        form = forms.ContactusForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['Email']
            name = form.cleaned_data['Name']
            message = form.cleaned_data['Message']
            try:
                send_mail(
                    f'{name} || {email}',
                    message,
                    settings.EMAIL_HOST_USER,
                    [settings.EMAIL_RECEIVING_USER],  # Ensure this is a list
                    fail_silently=False,
                )
                messages.success(request, 'Your message has been sent successfully!')
                return redirect('contactussuccess')  # Use the URL name for redirection
            except Exception as e:
                messages.error(request, 'There was an error sending your message. Please try again later.')
    else:
        form = forms.ContactusForm()

    return render(request, 'contactus.html', {'form': form})






@login_required(login_url='receptionistlogin')
@user_passes_test(is_receptionist)
def receptionist_dashboard_view(request):
    doctors=models.Doctor.objects.all().order_by('-id')
    patients=models.Patient.objects.all().order_by('-id')
    receptionist=models.Receptionist.objects.all().order_by("-id")
    #for three cards
    doctorcount=models.Doctor.objects.all().filter(status=True).count()
    pendingdoctorcount=models.Doctor.objects.all().filter(status=False).count()

    patientcount=models.Patient.objects.all().filter(status=True).count()
    pendingpatientcount=models.Patient.objects.all().filter(status=False).count()

    receptionistcount=models.Receptionist.objects.all().filter(status=True).count()
    pendingreceptionistcount=models.Receptionist.objects.all().filter(status=False).count()
    

    appointmentcount=models.Appointment.objects.all().filter(status=True).count()
    pendingappointmentcount=models.Appointment.objects.all().filter(status=False).count()
    mydict={
    'doctors':doctors,
    'patients':patients,
    "receptionist":receptionist,
    'doctorcount':doctorcount,
    'pendingdoctorcount':pendingdoctorcount,
    'patientcount':patientcount,
    'pendingpatientcount':pendingpatientcount,
    'receptionistcount':receptionistcount,
    'pendingreceptionistcount':pendingreceptionistcount,
    'appointmentcount':appointmentcount,
    'pendingappointmentcount':pendingappointmentcount,
    }
    return render(request,'receptionist_dashboard.html',context=mydict)







@login_required(login_url='receptionistlogin')
@user_passes_test(is_receptionist)
def receptionist_patient_view(request):
    return render(request,'receptionist_patient.html')




@login_required(login_url='receptionistlogin')
@user_passes_test(is_receptionist)
def receptionist_view_patient_view(request):
    patients=models.Patient.objects.all().filter(status=True)
    return render(request,'receptionist_view_patient.html',{'patients':patients})



# @login_required(login_url='receptionistlogin')
# @user_passes_test(is_receptionist)
# def delete_patient_from_hospital_view(request,pk):
#     patient=models.Patient.objects.get(id=pk)
#     user=models.User.objects.get(id=patient.user_id)
#     user.delete()
#     patient.delete()
#     return redirect('receptionist-view-patient')



# @login_required(login_url='receptionistlogin')
# @user_passes_test(is_receptionist)
# def update_patient_view(request,pk):
#     patient=models.Patient.objects.get(id=pk)
#     user=models.User.objects.get(id=patient.user_id)

#     userForm=forms.PatientUserForm(instance=user)
#     patientForm=forms.PatientForm(request.FILES,instance=patient)
#     mydict={'userForm':userForm,'patientForm':patientForm}
#     if request.method=='POST':
#         userForm=forms.PatientUserForm(request.POST,instance=user)
#         patientForm=forms.PatientForm(request.POST,request.FILES,instance=patient)
#         if userForm.is_valid() and patientForm.is_valid():
#             user=userForm.save()
#             user.set_password(user.password)
#             user.save()
#             patient=patientForm.save(commit=False)
#             patient.status=True
#             patient.assignedDoctorId=request.POST.get('assignedDoctorId')
#             patient.save()
#             return redirect('receptionist-view-patient')
#     return render(request,'receptionist_update_patient.html',context=mydict)





# @login_required(login_url='receptionistlogin')
# @user_passes_test(is_receptionist)
# def receptionist_add_patient_view(request):
#     userForm=forms.PatientUserForm()
#     patientForm=forms.PatientForm()
#     mydict={'userForm':userForm,'patientForm':patientForm}
#     if request.method=='POST':
#         userForm=forms.PatientUserForm(request.POST)
#         patientForm=forms.PatientForm(request.POST,request.FILES)
#         if userForm.is_valid() and patientForm.is_valid():
#             user=userForm.save()
#             user.set_password(user.password)
#             user.save()

#             patient=patientForm.save(commit=False)
#             patient.user=user
#             patient.status=True
#             patient.assignedDoctorId=request.POST.get('assignedDoctorId')
#             patient.save()

#             my_patient_group = Group.objects.get_or_create(name='PATIENT')
#             my_patient_group[0].user_set.add(user)

#         return HttpResponseRedirect('receptionist-view-patient')
#     return render(request,'receptionist_add_patient.html',context=mydict)




# @login_required(login_url='receptionistlogin')
# @user_passes_test(is_receptionist)
# def receptionist_approve_patient_view(request):
#     #those whose approval are needed
#     patients=models.Patient.objects.all().filter(status=False)
#     return render(request,'receptionist_approve_patient.html',{'patients':patients})




# @login_required(login_url='receptionistlogin')
# @user_passes_test(is_receptionist)
# def approve_patient_view(request,pk):
#     patient=models.Patient.objects.get(id=pk)
#     patient.status=True
#     patient.save()
#     return redirect(reverse('receptionist-approve-patient'))



# @login_required(login_url='receptionistlogin')
# @user_passes_test(is_receptionist)
# def reject_patient_view(request,pk):
#     patient=models.Patient.objects.get(id=pk)
#     user=models.User.objects.get(id=patient.user_id)
#     user.delete()
#     patient.delete()
#     return redirect('receptionist-approve-patient')



# @login_required(login_url='receptionistlogin')
# @user_passes_test(is_receptionist)
# def receptionist_discharge_patient_view(request):
#     patients=models.Patient.objects.all().filter(status=True)
#     return render(request,'receptionist_discharge_patient.html',{'patients':patients})



# @login_required(login_url='receptionistlogin')
# @user_passes_test(is_receptionist)
# def discharge_patient_view(request,pk):
#     patient=models.Patient.objects.get(id=pk)
#     days=(date.today()-patient.admitDate)
#     assignedDoctor=models.User.objects.all().filter(id=patient.assignedDoctorId)
#     d=days.days 
#     patientDict={
#         'patientId':pk,
#         'name':patient.get_name,
#         'mobile':patient.mobile,
#         'address':patient.address,
#         'symptoms':patient.symptoms,
#         'admitDate':patient.admitDate,
#         'todayDate':date.today(),
#         'day':d,
#         'assignedDoctorName':assignedDoctor[0].first_name,
#     }
#     if request.method == 'POST':
#         feeDict ={
#             'roomCharge':int(request.POST['roomCharge'])*int(d),
#             'doctorFee':request.POST['doctorFee'],
#             'medicineCost' : request.POST['medicineCost'],
#             'OtherCharge' : request.POST['OtherCharge'],
#             'total':(int(request.POST['roomCharge'])*int(d))+int(request.POST['doctorFee'])+int(request.POST['medicineCost'])+int(request.POST['OtherCharge'])
#         }
#         patientDict.update(feeDict)

#         pDD=models.PatientDischargeDetails()
#         pDD.patientId=pk
#         pDD.patientName=patient.get_name
#         pDD.assignedDoctorName=assignedDoctor[0].first_name
#         pDD.address=patient.address
#         pDD.mobile=patient.mobile
#         pDD.symptoms=patient.symptoms
#         pDD.admitDate=patient.admitDate
#         pDD.releaseDate=date.today()
#         pDD.daySpent=int(d)
#         pDD.medicineCost=int(request.POST['medicineCost'])
#         pDD.roomCharge=int(request.POST['roomCharge'])*int(d)
#         pDD.doctorFee=int(request.POST['doctorFee'])
#         pDD.OtherCharge=int(request.POST['OtherCharge'])
#         pDD.total=(int(request.POST['roomCharge'])*int(d))+int(request.POST['doctorFee'])+int(request.POST['medicineCost'])+int(request.POST['OtherCharge'])
#         pDD.save()
#         return render(request,'patient_final_bill.html',context=patientDict)
#     return render(request,'patient_generate_bill.html',context=patientDict)




@login_required(login_url='receptionistlogin')
@user_passes_test(is_receptionist)
def receptionist_appointment_view(request):
    return render(request,'receptionist_appointment.html')

@login_required(login_url='receptionistlogin')
@user_passes_test(is_receptionist)
def receptionist_doctor_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    return render(request,'receptionist_doctor.html',{'doctors':doctors})


@login_required(login_url='receptionistlogin')
@user_passes_test(is_receptionist)
def receptionist_view_appointment_view(request):
    appointments=models.Appointment.objects.all().filter(status=True)
    return render(request,'receptionist_view_appointment.html',{'appointments':appointments})




# @login_required(login_url='receptionistlogin')
# @user_passes_test(is_receptionist)
# def receptionist_add_appointment_view(request):
#     appointmentForm=forms.AppointmentForm()
#     mydict={'appointmentForm':appointmentForm,}
#     if request.method=='POST':
#         appointmentForm=forms.AppointmentForm(request.POST)
#         if appointmentForm.is_valid():
#             appointment=appointmentForm.save(commit=False)
#             appointment.doctorId=request.POST.get('doctorId')
#             appointment.patientId=request.POST.get('patientId')
#             appointment.doctorName=models.User.objects.get(id=request.POST.get('doctorId')).first_name
#             appointment.patientName=models.User.objects.get(id=request.POST.get('patientId')).first_name
#             appointment.status=True
#             appointment.save()
#         return HttpResponseRedirect('receptionist-view-appointment')
#     return render(request,'receptionist_add_appointment.html',context=mydict)




# @login_required(login_url='receptionistlogin')
# @user_passes_test(is_receptionist)
# def receptionist_approve_appointment_view(request):
#     #those whose approval are needed
#     appointments=models.Appointment.objects.all().filter(status=False)
#     return render(request,'receptionist_approve_appointment.html',{'appointments':appointments})




# @login_required(login_url='receptionistlogin')
# @user_passes_test(is_receptionist)
# def approve_appointment_view(request,pk):
#     appointment=models.Appointment.objects.get(id=pk)
#     appointment.status=True
#     appointment.save()
#     return redirect(reverse('receptionist-approve-appointment'))




# @login_required(login_url='receptionistlogin')
# @user_passes_test(is_receptionist)
# def reject_appointment_view(request,pk):
#     appointment=models.Appointment.objects.get(id=pk)
#     appointment.delete()
#     return redirect('receptionist-approve-appointment')


#for billing

import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return



def download_pdf_view(request,pk):
    dischargeDetails=models.PatientDischargeDetails.objects.all().filter(patientId=pk).order_by('-id')[:1]
    dict={
        'patientName':dischargeDetails[0].patientName,
        'assignedDoctorName':dischargeDetails[0].assignedDoctorName,
        'address':dischargeDetails[0].address,
        'mobile':dischargeDetails[0].mobile,
        'symptoms':dischargeDetails[0].symptoms,
        'admitDate':dischargeDetails[0].admitDate,
        'releaseDate':dischargeDetails[0].releaseDate,
        'daySpent':dischargeDetails[0].daySpent,
        'medicineCost':dischargeDetails[0].medicineCost,
        'roomCharge':dischargeDetails[0].roomCharge,
        'doctorFee':dischargeDetails[0].doctorFee,
        'OtherCharge':dischargeDetails[0].OtherCharge,
        'total':dischargeDetails[0].total,
    }
    return render_to_pdf('download_bill.html',dict)



# #for patient updating
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required, user_passes_test
# from . import models, forms
# from django.contrib.auth.models import Group

# def is_admin(user):
#     return user.is_superuser

# def is_receptionist(user):
#     return user.groups.filter(name='RECEPTIONIST').exists()

# # Function to handle patient forms (existing)
# def handle_patient_forms(request, patient=None):
#     user = patient.user if patient else None
#     user_form = forms.PatientUserForm(instance=user)
#     patient_form = forms.PatientForm(request.FILES or None, instance=patient)
    
#     if request.method == 'POST':
#         user_form = forms.PatientUserForm(request.POST, instance=user)
#         patient_form = forms.PatientForm(request.POST, request.FILES, instance=patient)
        
#         if user_form.is_valid() and patient_form.is_valid():
#             user = user_form.save()
#             user.set_password(user.password)
#             user.save()
#             patient = patient_form.save(commit=False)
#             patient.status = True
#             patient.assignedDoctorId = request.POST.get('assignedDoctorId')
#             patient.save()
#             return True, user, patient
#     return False, user_form, patient_form

# @login_required(login_url='adminlogin')
# @user_passes_test(is_admin)
# def admin_update_patient_view(request, pk):
#     patient = models.Patient.objects.get(id=pk)
#     success, user_form, patient_form = handle_patient_forms(request, patient)
    
#     if success:
#         return redirect('admin-view-patient')
    
#     context = {'userForm': user_form, 'patientForm': patient_form}
#     return render(request, 'admin_update_patient.html', context)

# @login_required(login_url='receptionistlogin')
# @user_passes_test(is_receptionist)
# def receptionist_update_patient_view(request, pk):
#     patient = models.Patient.objects.get(id=pk)
#     success, user_form, patient_form = handle_patient_forms(request, patient)
    
#     if success:
#         return redirect('receptionist-view-patient')
    
#     context = {'userForm': user_form, 'patientForm': patient_form}
#     return render(request, 'receptionist_update_patient.html', context)

# @login_required(login_url='adminlogin')
# @user_passes_test(is_admin)
# def admin_add_patient_view(request):
#     return add_patient_view(request, 'admin')

# @login_required(login_url='receptionistlogin')
# @user_passes_test(is_receptionist)
# def receptionist_add_patient_view(request):
#     return add_patient_view(request, 'receptionist')

# def add_patient_view(request, role):
#     user_form = forms.PatientUserForm()
#     patient_form = forms.PatientForm()
    
#     if request.method == 'POST':
#         user_form = forms.PatientUserForm(request.POST)
#         patient_form = forms.PatientForm(request.POST, request.FILES)
        
#         if user_form.is_valid() and patient_form.is_valid():
#             user = user_form.save()
#             user.set_password(user.password)
#             user.save()

#             patient = patient_form.save(commit=False)
#             patient.user = user
#             patient.status = True
#             patient.assignedDoctorId = request.POST.get('assignedDoctorId')
#             patient.save()

#             my_patient_group = Group.objects.get_or_create(name='PATIENT')
#             my_patient_group[0].user_set.add(user)

#             return redirect(f'{role}-view-patient')

#     context = {'userForm': user_form, 'patientForm': patient_form}
#     return render(request, f'{role}_add_patient.html', context)

# # New delete patient view
# @login_required(login_url='adminlogin')
# @user_passes_test(is_admin)
# def admin_delete_patient_view(request, pk):
#     patient = get_object_or_404(models.Patient, id=pk)

#     if request.method == 'POST':
#         # Optionally delete the associated user
#         user = patient.user
#         patient.delete()
#         if user:
#             user.delete()
#         return redirect('admin-view-patient')

#     context = {'patient': patient}
#     return render(request, 'admin_delete_patient.html', context)

# @login_required(login_url='receptionistlogin')
# @user_passes_test(is_receptionist)
# def receptionist_delete_patient_view(request, pk):
#     patient = get_object_or_404(models.Patient, id=pk)

#     if request.method == 'POST':
#         # Optionally delete the associated user
#         user = patient.user
#         patient.delete()
#         if user:
#             user.delete()
#         return redirect('receptionist-view-patient')

#     context = {'patient': patient}
#     return render(request, 'receptionist_delete_patient.html', context)

# @login_required(login_url='adminlogin')
# @user_passes_test(is_admin)
# def admin_approve_patient_view(request, pk):
#     patient = get_object_or_404(models.Patient, id=pk)
    
#     if request.method == 'POST':
#         patient.status = True  # Approving the patient
#         patient.save()
#         return redirect('admin-view-patient')
    
#     context = {'patient': patient}
#     return render(request, 'admin_approve_patient.html', context)

# @login_required(login_url='receptionistlogin')
# @user_passes_test(is_receptionist)
# def receptionist_approve_patient_view(request, pk):
#     patient = get_object_or_404(models.Patient, id=pk)
    
#     if request.method == 'POST':
#         patient.status = True  # Approving the patient
#         patient.save()
#         return redirect('receptionist-view-patient')
    
#     context = {'patient': patient}
#     return render(request, 'receptionist_approve_patient.html', context)

# @login_required(login_url='adminlogin')
# @user_passes_test(is_admin)
# def admin_reject_patient_view(request, pk):
#     patient = get_object_or_404(models.Patient, id=pk)
    
#     if request.method == 'POST':
#         patient.status = False  # Rejecting the patient
#         patient.save()
#         return redirect('admin-view-patient')
    
#     context = {'patient': patient}
#     return render(request, 'admin_reject_patient.html', context)

# @login_required(login_url='receptionistlogin')
# @user_passes_test(is_receptionist)
# def receptionist_reject_patient_view(request, pk):
#     patient = get_object_or_404(models.Patient, id=pk)
    
#     if request.method == 'POST':
#         patient.status = False  # Rejecting the patient
#         patient.save()
#         return redirect('receptionist-view-patient')
    
#     context = {'patient': patient}
#     return render(request, 'receptionist_reject_patient.html', context)




# #for patient appointments
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required, user_passes_test
# from . import models, forms

# def is_admin(user):
#     return user.is_superuser

# def is_receptionist(user):
#     return user.groups.filter(name='RECEPTIONIST').exists()

# def handle_appointment_form(request, appointment=None):
#     appointment_form = forms.AppointmentForm(instance=appointment)
    
#     if request.method == 'POST':
#         appointment_form = forms.AppointmentForm(request.POST, instance=appointment)
        
#         if appointment_form.is_valid():
#             appointment = appointment_form.save(commit=False)
#             appointment.doctorId = request.POST.get('doctorId')
#             appointment.patientId = request.POST.get('patientId')
#             appointment.doctorName = models.User.objects.get(id=request.POST.get('doctorId')).first_name
#             appointment.patientName = models.User.objects.get(id=request.POST.get('patientId')).first_name
#             appointment.status = True
#             appointment.save()
#             return True, appointment_form
#     return False, appointment_form

# @login_required(login_url='adminlogin')
# @user_passes_test(is_admin)
# def admin_add_appointment_view(request):
#     return add_appointment_view(request, 'admin')

# @login_required(login_url='receptionistlogin')
# @user_passes_test(is_receptionist)
# def receptionist_add_appointment_view(request):
#     return add_appointment_view(request, 'receptionist')

# def add_appointment_view(request, role):
#     appointment_form = forms.AppointmentForm()
    
#     if request.method == 'POST':
#         success, appointment_form = handle_appointment_form(request)
        
#         if success:
#             return redirect(f'{role}-view-appointment')

#     context = {'appointmentForm': appointment_form}
#     return render(request, f'{role}_add_appointment.html', context)

# @login_required(login_url='adminlogin')
# @user_passes_test(is_admin)
# def admin_view_appointment_view(request):
#     appointments = models.Appointment.objects.filter(status=True)
#     return render(request, 'admin_view_appointment.html', {'appointments': appointments})

# @login_required(login_url='receptionistlogin')
# @user_passes_test(is_receptionist)
# def receptionist_view_appointment_view(request):
#     appointments = models.Appointment.objects.filter(status=True)
#     return render(request, 'receptionist_view_appointment.html', {'appointments': appointments})

# @login_required(login_url='adminlogin')
# @user_passes_test(is_admin)
# def admin_approve_appointment_view(request):
#     appointments = models.Appointment.objects.filter(status=False)
#     return render(request, 'admin_approve_appointment.html', {'appointments': appointments})

# @login_required(login_url='receptionistlogin')
# @user_passes_test(is_receptionist)
# def receptionist_approve_appointment_view(request):
#     appointments = models.Appointment.objects.filter(status=False)
#     return render(request, 'receptionist_approve_appointment.html', {'appointments': appointments})

# @login_required(login_url='adminlogin')
# @user_passes_test(is_admin)
# def approve_appointment_view(request, pk):
#     appointment = models.Appointment.objects.get(id=pk)
#     appointment.status = True
#     appointment.save()
#     return redirect('admin-approve-appointment')

# @login_required(login_url='receptionistlogin')
# @user_passes_test(is_receptionist)
# def approve_receptionist_appointment_view(request, pk):
#     appointment = models.Appointment.objects.get(id=pk)
#     appointment.status = True
#     appointment.save()
#     return redirect('receptionist-approve-appointment')

# @login_required(login_url='adminlogin')
# @user_passes_test(is_admin)
# def reject_appointment_view(request, pk):
#     appointment = models.Appointment.objects.get(id=pk)
#     appointment.delete()
#     return redirect('admin-approve-appointment')

# @login_required(login_url='receptionistlogin')
# @user_passes_test(is_receptionist)
# def reject_receptionist_appointment_view(request, pk):
#     appointment = models.Appointment.objects.get(id=pk)
#     appointment.delete()
#     return redirect('receptionist-approve-appointment')




# #for patient billing
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required, user_passes_test
# from . import models
# from datetime import date

# def is_admin(user):
#     return user.is_superuser

# def is_receptionist(user):
#     return user.groups.filter(name='RECEPTIONIST').exists()

# def calculate_billing(patient, days, request):
#     fee_dict = {
#         'roomCharge': int(request.POST['roomCharge']) * days,
#         'doctorFee': int(request.POST['doctorFee']),
#         'medicineCost': int(request.POST['medicineCost']),
#         'OtherCharge': int(request.POST['OtherCharge']),
#     }
#     fee_dict['total'] = sum(fee_dict.values())
#     return fee_dict

# @login_required(login_url='adminlogin')
# @user_passes_test(is_admin)
# def admin_discharge_patient_view(request):
#     return discharge_patient_view(request, 'admin')

# @login_required(login_url='receptionistlogin')
# @user_passes_test(is_receptionist)
# def receptionist_discharge_patient_view(request):
#     return discharge_patient_view(request, 'receptionist')

# def discharge_patient_view(request, role):
#     patients = models.Patient.objects.filter(status=True)
#     if request.method == 'POST':
#         pk = request.POST.get('patientId')
#         return discharge_process(request, pk, role)
    
#     return render(request, f'{role}_discharge_patient.html', {'patients': patients})

# def discharge_process(request, pk, role):
#     patient = models.Patient.objects.get(id=pk)
#     days = (date.today() - patient.admitDate).days
#     assigned_doctor = models.User.objects.get(id=patient.assignedDoctorId)

#     patient_dict = {
#         'patientId': pk,
#         'name': patient.get_name,
#         'mobile': patient.mobile,
#         'address': patient.address,
#         'symptoms': patient.symptoms,
#         'admitDate': patient.admitDate,
#         'todayDate': date.today(),
#         'day': days,
#         'assignedDoctorName': assigned_doctor.first_name,
#     }

#     if request.method == 'POST':
#         fee_dict = calculate_billing(patient, days, request)
#         patient_dict.update(fee_dict)

#         # Save discharge details
#         pDD = models.PatientDischargeDetails(
#             patientId=pk,
#             patientName=patient.get_name,
#             assignedDoctorName=assigned_doctor.first_name,
#             address=patient.address,
#             mobile=patient.mobile,
#             symptoms=patient.symptoms,
#             admitDate=patient.admitDate,
#             releaseDate=date.today(),
#             daySpent=days,
#             **fee_dict
#         )
#         pDD.save()

#         return render(request, 'patient_final_bill.html', context=patient_dict)

#     return render(request, 'patient_generate_bill.html', context=patient_dict)




from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from . import models, forms

def is_receptionist(user):
    return hasattr(user, 'receptionist')

@login_required(login_url='adminlogin')
@user_passes_test(lambda u: is_admin(u) or is_receptionist(u))
def medicine_inventory_view(request):
    medicines = models.Medicine.objects.all()
    return render(request, 'view_medicine.html', {'medicines': medicines})

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from . import forms

@login_required(login_url='adminlogin')
@user_passes_test(lambda u: is_admin(u) or is_receptionist(u))
def add_medicine_view(request):
    if request.method == 'POST':
        medicineForm = forms.MedicineForm(request.POST)
        if medicineForm.is_valid(): 
            medicineForm.save()
            return redirect('medicine-inventory')
    else:
        medicineForm = forms.MedicineForm() 

    return render(request, 'add_medicine.html', {'medicineForm': medicineForm})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from . import models, forms

@login_required(login_url='adminlogin')
@user_passes_test(lambda u: is_admin(u) or is_receptionist(u))
def update_medicine_view(request, pk):
    medicine = get_object_or_404(models.Medicine, id=pk)
    
    if request.method == 'POST':
        medicineForm = forms.MedicineForm(request.POST, instance=medicine)
        if medicineForm.is_valid():
            medicineForm.save()
            return HttpResponseRedirect(reverse('medicine-inventory'))  # Redirect to view medicines
    else:
        medicineForm = forms.MedicineForm(instance=medicine)
        
    return render(request, 'update_medicine.html', {'medicineForm': medicineForm})


@login_required(login_url='adminlogin')
@user_passes_test(lambda u: is_admin(u) or is_receptionist(u))
def delete_medicine_view(request, pk):
    medicine = get_object_or_404(models.Medicine, id=pk)
    medicine.delete()
    return redirect('medicine-inventory')





from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from . import forms, models
import uuid

def emergency_patient_book_appointment_view(request):
    appointmentForm = forms.PatientAppointmentForm()
    message = None

    if request.method == 'POST':
        appointmentForm = forms.PatientAppointmentForm(request.POST)

        if appointmentForm.is_valid():
            desc = request.POST.get('description')
            doctor_id = request.POST.get('doctorId')
            doctor = models.Doctor.objects.get(user_id=doctor_id)

            # Generate a sequential ID for the emergency patient
            existing_appointments = models.Appointment.objects.filter(emergency=True)
            if existing_appointments.exists():
                last_id = max(app.patientId for app in existing_appointments)  # Ensure patientId is numeric
                emergency_patient_id = last_id + 1
            else:
                emergency_patient_id = 1

            # Create and save the appointment
            appointment = appointmentForm.save(commit=False)
            appointment.doctorId = doctor_id
            appointment.patientId = emergency_patient_id  # Use the generated ID
            appointment.doctorName = models.User.objects.get(id=doctor_id).first_name
            appointment.patientName = "Emergency Patient"  # Default name for emergency patients
            appointment.status = True  # Automatically approve the appointment
            appointment.emergency = True  # Mark this appointment as emergency
            appointment.save()

            # Automatically log in the emergency patient
            user = User.objects.create_user(
                username=str(emergency_patient_id),  # Ensure the username is a string
                password=uuid.uuid4().hex,
                # profile = models.Profile.objects.create(user=user)  # Generate a random password
            )
            login(request, user)


            # Redirect to the success page after booking the appointment
            return render(request,'emergency_appointment_success.html')  # Use 'redirect' to go to the success view

    return render(request, 'emergency_book_appointment.html', {
        'appointmentForm': appointmentForm,
        'message': message,
    })



# from django.contrib.auth import login
# from django.contrib.auth.models import User
# from django.shortcuts import render, redirect
# from . import forms, models
# import uuid

# def emergency_patient_book_appointment_view(request):
#     appointmentForm = forms.PatientAppointmentForm()
#     message = None

#     if request.method == 'POST':
#         appointmentForm = forms.PatientAppointmentForm(request.POST)

#         if appointmentForm.is_valid():
#             desc = request.POST.get('description')
#             doctor_id = request.POST.get('doctorId')
#             doctor = models.Doctor.objects.get(user_id=doctor_id)

#             # Access the doctor's full name using the property
#             doctor_name = doctor.get_name  # Use the get_name property

#             # Generate a sequential numeric ID for the emergency patient
#             existing_appointments = models.Appointment.objects.filter(emergency=True)
#             if existing_appointments.exists():
#                 last_id = max(app.patientId for app in existing_appointments)  # Ensure patientId is numeric
#                 emergency_patient_id = last_id + 1
#             else:
#                 emergency_patient_id = 1

#             # Generate a unique username for the emergency patient
#             base_username = f"emergency_patient_{emergency_patient_id}"
#             username = base_username
#             counter = 1
            
#             # Check for existing user and modify username if necessary
#             while User.objects.filter(username=username).exists():
#                 username = f"{base_username}_{counter}"
#                 counter += 1

#             # Create the User
#             user = User.objects.create_user(
#                 username=username,  # Unique username for the patient
#                 password=uuid.uuid4().hex  # Generate a random password
#             )
#             patient = models.Patient.objects.create(
#                 user=user,
#                 address="Unknown",  # Set default or gather input if needed
#                 mobile="Unknown",
#                 symptoms=desc,  # Use the description as symptoms for emergency patients
#                 assignedDoctorId=doctor_id,
#                 is_emergency=True  # Mark this patient as an emergency
#             )

#             # Create and save the appointment
#             appointment = appointmentForm.save(commit=False)
#             appointment.doctorId = doctor_id
#             appointment.patientId = patient.get_id  # Access the property correctly
#             appointment.doctorName = doctor_name  # Use the doctor's full name
#             appointment.patientName = patient.get_name  # Use the patient's name
#             appointment.status = False  # Adjust based on your logic
#             appointment.emergency = True  # Mark this appointment as emergency
#             appointment.save()

#             # Automatically log in the emergency patient
#             login(request, user)

#             return redirect('patient-view-appointment')  # Redirect to the appointments view

#     return render(request, 'patient_book_appointment.html', {
#         'appointmentForm': appointmentForm,
#         'message': message,
#     })


