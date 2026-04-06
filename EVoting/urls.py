"""EVoting URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from EVotingApp.views import *

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('',index),
    path('about/',aboutUs,name='about'),
    path('user/login/', userLogin),
    path('user/sendOtp/', sendOtp),
    path('user/register/', userRegister),
    path('admin/login/', adminLogin),
    path('admin/', admin),
    path('user/', user),
    path('logout/', logout),

    path('admin/user/', getUsers,name='getUsers'),
    path('admin/user/status/<int:id>', userStatus),

    path('admin/candidate/<str:type>/', addEditCandidate, name='candidate_view'),
    path('admin/candidate/', getCandidates,name='candidate_list'),
    path('admin/candidate/status/<int:id>', candidateStatus),
    path('admin/candidate/delete/<int:id>', candidateDelete,name='candidate_delete'),
    path('admin/party/',party),
    path('admin/party/status/<int:id>', partyStatus),
    path('admin/user/update/', updateUser,name='update_user'),

    path('admin/constituency/',constituency),
    path('admin/voteResult/',adminVoteResult),
    path('admin/constituency/status/<int:id>', constituencyStatus),


    path('admin/info/', voteInfo),
    path('admin/result/status/<int:id>', resultStatus),

    path('user/verification/', userVerification),
    path('user/verify/', verifyUser),
    path('user/vote/', userVote),
    path('user/result/', userResult),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
