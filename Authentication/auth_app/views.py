from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile
import uuid
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='/')
def home(request):
    return render(request,'home.html')

def register(request):
    
    if request.method=='POST':
        username=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')
        
        
        try:
            if User.objects.filter(username=username).first():
                messages.success(request,'Username is already taken')
                return redirect('/register')
        
        
            if User.objects.filter(email=email).first():
                messages.success(request,'email is already taken')
                return redirect('/register')
        
            user_obj=User.objects.create(username=username,email=email)
            user_obj.set_password(password)
            user_obj.save()
            auth_token=str(uuid.uuid4())
            profile_obj=Profile.objects.create(user=user_obj,auth_token=str(uuid.uuid4()))
            profile_obj.save()
            send_mail_after_registration(email,auth_token)
            return redirect('/token_send')
        
        except Exception as e:
            print(e)
            
        
    return render(request,'register.html')

def login(request):
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        
        user_obj=User.objects.filter(username=username).first()
        if user_obj is None:
            messages.success(request,'user not found')
            return redirect('/login')
        
        pro_obj=Profile.objects.filter(user=user_obj).first()
        
        if not pro_obj.is_verified:
             messages.success(request,'user not verified check your mail')
             return redirect('/login')
         
        user=authenticate(username=username,password=password)
        if user is None:
            messages.success(request,'wrong credentials')
            return redirect('/login')
        
             
        login(request,user)
        return redirect(request,'/')
        
            
        
    return render(request,'login.html')

def success(request):
    return render(request,'success.html')

def token_send(request):
    return render(request,'token_send.html')


def send_mail_after_registration(email,token):
    subject='Your Account need to be verified'
    message=f'to verify your account http://127.0.0.1/verify/{token}'
    email_from=settings.EMAIL_HOST_USER
    recipient_list=[email]
    send_mail(subject,message,email_from,recipient_list)
    
    
    
def verify(request,auth_token):
    try:
        pro_obj=Profile.objects.filter(auth_token=auth_token).first()
        if pro_obj:
            if pro_obj.is_verified==True:
                messages.success(request,'your account has been already registered')
                return redirect('/login')
                
            pro_obj.is_verified=True
            pro_obj.save()
            messages.success(request,'your account has been verified')
            return redirect('/login')
        
        else:
            return redirect('/error')
    
    
    except Exception as e:
        print(e)
        return redirect('/')
        
        
def error(request):
    return render(request,'error.html')