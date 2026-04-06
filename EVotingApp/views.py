from django.shortcuts import render, redirect, get_object_or_404
from EVotingApp.models import *
from django.http import JsonResponse
from django.db.models import Count
from datetime import datetime
from dateutil.relativedelta import relativedelta

import cv2
import numpy as np
import os
from PIL import Image
import time
import requests
from django.conf import settings
import random
from django.core.mail import send_mail




faceDetect = cv2.CascadeClassifier(r'''ImageProcessing/haarcascade_frontalface_alt2.xml''');
recognizer=cv2.face.LBPHFaceRecognizer_create();

#Assigning the training labels to the images in dataset using Python Method
def getImagesWithID(path):
    imagePaths=[os.path.join(path,f) for f in os.listdir(path)]
    # print(imagePaths)
    faces=[]
    IDs=[]
    #Convert the images to grayscale for processing
    for imagePath in imagePaths:
        faceImg = Image.open(imagePath).convert('L');
        faceNp = np.array(faceImg,'uint8')
    
        #Tokenization of the images splitted into pixels
        ID = int(os.path.split(imagePath)[-1].split('.')[1])
        faces.append(faceNp)
        IDs.append(ID)
        # cv2.imshow("training",faceNp)
        cv2.waitKey(10)
    return IDs, faces

# Create your views here.

def index(request):
    return render(request, 'index.html')

def aboutUs(request):
    return render(request,'about.html')

def admin(request):
    return render(request, 'admin/index.html')

def user(request):
    return render(request, 'user/index.html')

def getUsers(request):
    data = User.objects.all().select_related()
    return render(request, 'admin/users.html', {"users": data})

def userStatus(request,id):
    data = User.objects.filter(id=id).get()
    if data.status == 1:
        data.status = 0
    else:
        data.status = 1
    data.save()
    return redirect('/admin/user/')

def addEditCandidate(request, type):
    constituency_list = Constituency.objects.filter(status=1).values()
    party_list = Party.objects.filter(status=1).values()
    candidate = Candidate.objects.filter(id=type).first() if type != 'Add' else None

    context = {
        "constituency_list": constituency_list,
        "party_list": party_list,
        "type":  type,
        "action": 'Edit' if type != 'Add' else type,
        "candidate": candidate
    }

    if request.method == 'POST':
        name = request.POST['name']
        dob = request.POST['dob']
        constituency = request.POST['constituency']
        party = request.POST['party']

        if type == 'Add':
            image_file = request.FILES.get('image')
            data = Candidate(
                name=name, 
                dob=dob, 
                constituency_id=constituency, 
                party_id=party, 
                image=image_file, 
                status=1
            )
            data.save()
        else:
            print('id : ',request.POST['id'])
            candidate = get_object_or_404(Candidate, id=request.POST['id'])
            candidate.name = name
            candidate.dob = dob
            candidate.constituency_id = constituency
            candidate.party_id = party

            image_file = request.FILES.get('image')
            if image_file:
                candidate.image = image_file
            
            candidate.save()

        return redirect('candidate_list')  # Change to appropriate redirect

    return render(request, 'admin/add_candidate.html', context)

def getCandidates(request):
    data = Candidate.objects.all().select_related()
    return render(request, 'admin/candidates.html', {"candidates": data})

def candidateStatus(request,id):
    data = Candidate.objects.filter(id=id).get()
    if data.status == 1:
        data.status = 0
    else:
        data.status = 1
    data.save()
    return redirect('/admin/candidate/')

def candidateDelete(request,id):
    candidate = get_object_or_404(Candidate, id=id)
    candidate.delete()
    return redirect('/admin/candidate/')

def adminLogin(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]

        if ((username == "admin") and (password == "admin")):
            return redirect('/admin')
    return render(request, 'admin/login.html')


def sendOtp(request):
    if request.method == 'POST':
        phone=request.POST['phone']

        if User.objects.filter(phone=phone,status=1).exists():

            otp = random.randint(100000, 999999)
            print('Sent Otp : ',otp)
            url = f"https://2factor.in/API/V1/{settings.TWO_FACTOR_API_KEY}/SMS/{phone}/{otp}/OTP1"
            response = requests.get(url)
            response_data = response.json()
            #response_data = {'Status': 'Success', 'Details': '5454094c-1d5f-4867-be08-df6548196d7a'}

            if response_data.get('Status') == 'Success':
                request.session['otp'] = str(otp)
                return render(request,'user/login.html',{'phone':phone,'otp':True})
            else:
                return render(request,'user/login.html',{'error':'Failed to send OTP'})
        else:
            return render(request,'user/login.html',{'error':'Invalid Contact Number'})
    else:
       return render(request,'user/login.html',{'error':'Invalid request'})


def userLogin(request):
    if request.method == 'POST':
       
        if not request.session.has_key('otp'):
            return redirect('/user/login/')
        
        saved_otp = request.session['otp']
        print('Saved Otp : ',saved_otp)

        phone=request.POST['phone']
        otp = request.POST["otp"]

        if otp == saved_otp:
            user = User.objects.filter(phone=phone).first()

            if user:
                if user.status == 1:
                    request.session['user'] = user.id
                    return redirect('/user/')
                return render(request,'user/login.html',{'error':'Please contact admin..'})

        
        return render(request,'user/login.html',{'error':'Invalid Login Credentials'})
    return render(request, 'user/login.html')

def userRegister(request):
    data = Constituency.objects.filter(status=1)
    if request.method == 'POST':
        name=request.POST['name']
        email=request.POST['email']
        phone=request.POST['phone']
        voter_id=request.POST['voter_id']
        dob=request.POST['dob']
        constituency=request.POST['constituency']
        status=1

        if User.objects.filter(voter_id=voter_id).exists():
            return render(request, 'user/register.html', {"error":"Already registered with this voter id", "options": data})

        if User.objects.filter(phone=phone).exists():
            return render(request, 'user/register.html', {"error":"Duplicate Contact no", "options": data})
        else:
            data = User(name=name, email=email, phone=phone, dob=dob, constituency_id=constituency, status=status,voter_id=voter_id)
            data.save()

        return render(request, 'user/login.html', {"success":"Registered Successfully"})
    return render(request, 'user/register.html', {"options": data})

def userVerification(request):
    if request.method == 'POST':
        if not request.session.has_key('user'):
            return redirect('/user/login/')
        user_id=request.session['user']

        dataset_dir = 'ImageProcessing/dataset'
        rec_dir = 'ImageProcessing/recognizer'
        if not os.path.exists(dataset_dir):
            os.makedirs(dataset_dir)

        if not os.path.exists(rec_dir):
            os.makedirs(rec_dir)

        cam = cv2.VideoCapture(0)
        sampleNum=0
        while(cv2.waitKey(1)!=27):
            ret,img = cam.read()
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            faces = faceDetect.detectMultiScale(gray,1.3,5);
            for(x,y,w,h) in faces:
                sampleNum += 1
                cv2.imwrite(f"{dataset_dir}/User.{user_id}.{sampleNum}.png", gray[y:y+h, x:x+w])
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,225),2)
                cv2.waitKey(100)
            cv2.imshow("Face",img);
            cv2.waitKey(1);
            if(sampleNum>100):
                break
        cam.release()
        cv2.destroyAllWindows()

        # #Assigning the test labels to the data trained
        IDs,faces = getImagesWithID('ImageProcessing/dataset')
        recognizer.train(faces,np.array(IDs))

        recognizer.write(f"{rec_dir}/trainingData.yml")
        cv2.destroyAllWindows()

        return render(request, 'user/user_verification.html', {"success":"Verified Successfully"})

    return render(request, 'user/user_verification.html')

def verifyUser(request):
    if not request.session.has_key('user'):
        return redirect('/user/login/')
    user_id=request.session['user']
    user = User.objects.filter(id=user_id).first()
    user_age = relativedelta(datetime.today(), datetime.strptime(user.dob, '%Y-%m-%d'))
    res = {"user_age": user_age.years,"is_eligible": False if (user_age.years < 18) else True, "user_verified": True}

    if request.method == 'POST':
        cam = cv2.VideoCapture(0);
        rec = cv2.face.LBPHFaceRecognizer_create();
        rec.read("ImageProcessing/recognizer/trainingData.yml");
        id = 0
        fontface = cv2.FONT_HERSHEY_SIMPLEX
        fontsize = 1
        fontcolor = (0,511,1)
        userCount = 0
        strangerCount = 0
        userFound = False

        while(True):
            ret,img = cam.read();
            image=img
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            faces = faceDetect.detectMultiScale(gray,1.3,5);
            for(x,y,w,h) in faces:
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,180),2)
                id,conf = rec.predict(gray[y:y+h,x:x+w])
                if(id==user_id and conf<50):
                    id=user.name
                    userCount += 1
                else:
                    id="Stranger"
                    strangerCount += 1
                 
                cv2.putText(img,str(id),(x,y+h+25),fontface,fontsize,fontcolor,2);
            cv2.imshow("Face",img);

            if(userCount > 30):
                userFound = True
                break;
            if(strangerCount > 30):
                break;

            if(cv2.waitKey(1)==ord('q')):
                break;
        cam.release()
        cv2.destroyAllWindows()

        if userFound:
            request.session['verified_user'] = 1
            return redirect('/user/vote/')
        res = {"user_age": user_age.years, "is_eligible": False if (user_age.years < 18) else True, "user_verified": True, "user_found": 0}
    return render(request, 'user/user_verify.html', res)

def userVote(request):
    response = {}
    candidates_list = []
    if not request.session.has_key('verified_user'):
        return redirect('/user/verify/')
    if not request.session.has_key('user'):
        return redirect('/user/login/')
    user_id=request.session['user']
    user = User.objects.filter(id=user_id).select_related().first()

    today_date=datetime.today().strftime('%Y-%m-%d')

    # submit vote
    if request.method == 'POST':
        voted_to = request.POST['vote']
        user_vote = Vote.objects.filter(user_id=user_id, candidate_id=voted_to, vote_date=today_date).first()
        if user_vote == None:
            data = Vote(vote_date=today_date, user_id=user_id, candidate_id=voted_to)
            data.save()

            print('Send Email message to : ',user.email)
            sendEmailMessage(user)

    # vote details
    vote_info = VoteInfo.objects.first()
    vote_date = '' if vote_info == None else vote_info.vote_date
    is_vote_today = True if vote_date == today_date else False
    user_vote = Vote.objects.filter(user_id=user_id, vote_date=vote_date).first()

    candidates = Candidate.objects.filter(constituency_id=user.constituency.id).select_related()
    for candidate in candidates:
        vote = Vote.objects.filter(user_id=user_id, candidate_id=candidate.id, vote_date=vote_date).first()
        candidates_list.append({
            "vote_status": 0 if vote == None else 1,
            "details": candidate,
        })

    response = {
        "vote_date": vote_date,
        "is_vote_today": is_vote_today, 
        "is_voted": False if user_vote == None else True,
        "constituency": user.constituency.title,
        "candidates_list": candidates_list
    }
    return render(request, 'user/cast_vote.html', response)

def sendEmailMessage(user):
    subject = 'Thank You for Participating in the Election'
    message = f"""
    Dear {user.name},

    Thank you for taking the time to participate in the recent election. Your involvement is crucial in making our community stronger and ensuring that every voice is heard.

    We appreciate your commitment and support.

    Best regards,
    E Votting App
    """
    from_email = 'evottingapp@gmail.com'
    recipient_list = [user.email]
    
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

def userResult(request):
    response = {}
    candidates_list = []
    
    if not request.session.has_key('user'):
        return redirect('/user/login/')
    user_id=request.session['user']
    user = User.objects.filter(id=user_id).select_related().first()

    today_date=datetime.today().strftime('%Y-%m-%d')

    # vote details
    vote_info = VoteInfo.objects.first()
    vote_date = '' if vote_info == None else vote_info.vote_date
    show_result = 0 if vote_info == None else vote_info.result_status
    user_vote = Vote.objects.filter(user_id=user_id, vote_date=vote_date).first()

    candidates = Candidate.objects.filter(constituency_id=user.constituency.id).select_related()
    for candidate in candidates:
        vote_count = Vote.objects.filter(candidate_id=candidate.id, vote_date=vote_date).count()
        candidates_list.append({
            "vote_count": vote_count,
            "details": candidate,
        })

    candidates_list_sorted = sorted(candidates_list, key=lambda x: x['vote_count'], reverse=True)

    response = {
        "show_result": show_result,
        "vote_date": vote_date,
        "constituency": user.constituency.title,
        "candidates_list": candidates_list_sorted
    }
    return render(request, 'user/vote_result.html', response)


def adminVoteResult(request):
    response = {}
    candidates_list = []

    today_date=datetime.today().strftime('%Y-%m-%d')

    # vote details
    vote_info = VoteInfo.objects.first()
    vote_date = '' if vote_info == None else vote_info.vote_date
    show_result = 0 if vote_info == None else vote_info.result_status
    user_vote = Vote.objects.filter(vote_date=vote_date).first()

    candidates = Candidate.objects.filter().select_related().order_by('constituency_id')
    for candidate in candidates:
        vote_count = Vote.objects.filter(candidate_id=candidate.id, vote_date=vote_date).count()
        candidates_list.append({
            "vote_count": vote_count,
            "details": candidate,
            "constituency": candidate.constituency.title,
        })

    candidates_list_sorted = sorted(candidates_list, key=lambda x: x['vote_count'], reverse=True)

    response = {
        "show_result": show_result,
        "vote_date": vote_date,
        "candidates_list": candidates_list_sorted
    }
    return render(request, 'admin/voteResult.html', response)
    

def voteInfo(request):
    if request.method == 'POST':
        data = VoteInfo.objects.first()
        vote_date = request.POST['date']
        if data == None:
            data = VoteInfo(vote_date=vote_date, result_status=0)
            data.save()
        else:
            data.vote_date = vote_date
            data.save()

    info = VoteInfo.objects.first()
    res = {
        "info_id": 0 if info == None else info.id,
        "vote_date": '' if info == None else info.vote_date,
        "result_status": 0 if info == None else info.result_status
    }

    return render(request, 'admin/vote_info.html', res)

def resultStatus(request,id):
    data = VoteInfo.objects.first()
    if data.result_status == 1:
        data.result_status = 0
    else:
        data.result_status = 1
    data.save()
    return redirect('/admin/info/')

def logout(request):
    if request.session.has_key('user'):
        del request.session['user']
    if request.session.has_key('admin'):
        del request.session['admin']
    if request.session.has_key('verified_user'):
        del request.session['verified_user']
    return redirect('/')


def party(request):
    if request.method == 'POST':
        title = request.POST['title']
        logo = request.FILES['logo']
        data = Party(title = title,logo=logo)
        data.save()
        
    party_data = Party.objects.all().order_by('-id')
    return render(request, 'admin/party.html', {'parties':party_data})

def partyStatus(request,id):
    data = Party.objects.filter(id=id).get()
    if data.status == 1:
        data.status = 0
    else:
        data.status = 1
    data.save()
    return redirect('/admin/party/')

def constituency(request):
    if request.method == 'POST':
        title = request.POST['title']

        data = Constituency(title = title)
        data.save()

    constituency = Constituency.objects.all()
    return render(request, 'admin/constituency.html', {'constituency':constituency})

def constituencyStatus(request,id):
    data = Constituency.objects.filter(id=id).get()
    if data.status == 1:
        data.status = 0
    else:
        data.status = 1
    data.save()
    return redirect('/admin/constituency/')

def updateUser(request):
    if request.method == 'POST':
        id = request.POST['id']
        email = request.POST['email']
        phone = request.POST['phone']

        user = get_object_or_404(User, id=id)

        if not user:
            return JsonResponse({'success': False, 'message': 'User not found.'})

        # Check if another user already has the same email
        if email and User.objects.filter(email=email).exclude(id=id).exists():
            return JsonResponse({'success': False, 'message': 'Email is already taken by another user.'})

        # Check if another user already has the same phone number
        if phone and User.objects.filter(phone=phone).exclude(id=id).exists():
            return JsonResponse({'success': False, 'message': 'Phone number is already taken by another user.'})

        # Update user details
        user.email = email
        user.phone = phone
        user.save()

        return JsonResponse({'success': True, 'message': 'User updated successfully.'})



    return redirect('getUsers')