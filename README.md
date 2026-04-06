# E-Voting System — Face Recognition Based Online Voting

A secure online voting web application built with Django that uses face recognition and OTP authentication to verify voters before allowing them to cast their vote.

---

## Features

- **OTP Login** — Voter logs in via phone number with OTP sent through 2Factor SMS API
- **Face Enrollment** — Voter's face is captured and trained using OpenCV LBPH face recognizer
- **Face Verification** — Identity is confirmed via live face recognition before voting
- **Age Eligibility Check** — Automatically blocks voters under 18 years old
- **Duplicate Vote Prevention** — A voter can only vote once per election date
- **Constituency-wise Voting** — Voters only see candidates from their own constituency
- **Email Confirmation** — Voter receives a confirmation email after successfully casting vote
- **Admin Panel** — Manage users, candidates, parties, constituencies, vote dates and results

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django |
| Face Recognition | OpenCV, LBPH Face Recognizer |
| Database | MySQL |
| Frontend | HTML, CSS, Bootstrap |
| OTP Service | 2Factor SMS API |
| Email | Gmail SMTP |

---

## Setup Instructions

### 1. Clone the repository
git clone https://github.com/Jewelglory/evoting-face-recognition.git
cd evoting-face-recognition

### 2. Install dependencies
pip install -r req.txt

### 3. Create the database
Open MySQL and run:
CREATE DATABASE smart_voting_app;

### 4. Update credentials in EVoting/settings.py
DEBUG = True
DATABASES = {
'default': {
'ENGINE': 'django.db.backends.mysql',
'NAME': 'smart_voting_app',
'USER': 'root',
'PASSWORD': 'your-mysql-password',
'HOST': 'localhost',
'PORT': '3306',
}
}
SECRET_KEY = 'your-secret-key-here'
TWO_FACTOR_API_KEY = 'your-2factor-api-key'
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'

### 5. Run migrations
python manage.py migrate

### 6. Start the server
python manage.py runserver

### 7. Open in browser
http://127.0.0.1:8000/

---

## How It Works

1. Voter registers with name, email, phone, voter ID and constituency
2. Voter logs in using phone number — OTP is sent via SMS
3. Voter enrolls their face (100 face samples captured via webcam)
4. On voting day, face is verified live against enrolled data
5. If verified and age ≥ 18, voter can cast their vote
6. Confirmation email is sent after voting
7. Admin controls result visibility

---

## Admin Login

URL:      /admin/login/
Username: admin
Password: admin

---

## Screenshots

![E-Voting App](Evoting-images.jpg)

---

## Author

Jewel Christanand Pisse
Alliance University, Bengaluru
