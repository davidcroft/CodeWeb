from django.conf.urls import patterns, url, static
from django.conf import settings

from core import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^home$', views.index, name='index'),
    url(r'^getTweets$', views.getTweets, name='getTweets'),
    url(r'^team$', views.team, name='team'),
    url(r'^research$', views.research, name='research'),
    url(r'^sample$', views.sample, name='sample'),

    # Route for built-in authentication with our own custom login page
    url(r'^login$', 'django.contrib.auth.views.login', {'template_name':'login.html'}, name='login'),
    # Route to logout a user and send them back to the login page
    url(r'^logout$', 'django.contrib.auth.views.logout', {'next_page':'/'}, name='logout'),
    url(r'^register$', views.register, name='register'),
    url(r'^myAccount$', views.myAccount, name='myAccount'),

    # Admin news
    url(r'^publicSeeNewsPost/(?P<id>\d+)$', views.publicSeeNewsPost, name='publicSeeNewsPost'),
    url(r'^seeNewsPost/(?P<id>\d+)$', views.seeNewsPost, name='seeNewsPost'),

    url(r'^addNewsPost$', views.addNewsPost, name='addNewsPost'),
    url(r'^addNewsPost/(?P<id>\d+)$', views.addNewsPost, name='addNewsPost'),

    url(r'^editNewsPost$', views.editNewsPost, name='editNewsPost'),
    url(r'^editNewsPost/(?P<id>\d+)$', views.editNewsPost, name='editNewsPost'),
    
    url(r'^getNewsPostPicture/(?P<id>\d+)$', views.getNewsPostPicture, name='getNewsPostPicture'),
    url(r'^deleteNewsPost/(?P<id>\d+)$', views.deleteNewsPost, name='deleteNewsPost'),

    # Admin slides
    url(r'^mySlides$', views.mySlides, name='mySlides'),
    url(r'^addSlide/(?P<id>\d+)$', views.addSlide, name='addSlide'),

    url(r'^editSlide$', views.editSlide, name='editSlide'),
    url(r'^editSlide/(?P<id>\d+)$', views.editSlide, name='editSlide'),
    
    url(r'^getSlidePicture/(?P<id>\d+)$', views.getSlidePicture, name='getSlidePicture'),
    url(r'^deleteSlide/(?P<id>\d+)$', views.deleteSlide, name='deleteSlide'),

    url(r'^editProfile$', views.editProfile, name='editProfile'),
    url(r'^editAdminProfile$', views.editAdminProfile, name='editAdminProfile'),
    url(r'^updateProfile$', views.updateProfile, name='updateProfile'),
    url(r'^getProfilePicture/(?P<email>[\w.-_]+@[\w.-]+)$', views.getProfilePicture, name='getProfilePicture'),

    url(r'^about$', views.about, name='about'),
    url(r'^myAbout$', views.myAbout, name='myAbout'),
    url(r'^editAbout$', views.editAbout, name='editAbout'),
    url(r'^getAboutPicture/(?P<id>\d+)$', views.getAboutPicture, name='getAboutPicture'),
    url(r'^deleteAbout/(?P<id>\d+)$', views.deleteAbout, name='deleteAbout'),

    url(r'^admission$', views.admission, name='admission'),
    url(r'^myAdmission$', views.myAdmission, name='myAdmission'),
    url(r'^editAdmission$', views.editAdmission, name='editAdmission'),
    url(r'^getAdmissionPicture/(?P<id>\d+)$', views.getAdmissionPicture, name='getAdmissionPicture'),
    url(r'^deleteAdmission/(?P<id>\d+)$', views.deleteAdmission, name='deleteAdmission'),

    # User info
    url(r'^myInformation$', views.myInformation, name='myInformation'),
    url(r'^myProjects$', views.myProjects, name='myProjects'),
    url(r'^myPapers$', views.myPapers, name='myPapers'),
    url(r'^myPosts$', views.myPosts, name='myPosts'),
    url(r'^getProfilePicture/(?P<id>\d+)$', views.getProfilePicture, name='getProfilePicture'),

    # Papers
    url(r'^addPaper$', views.addPaper, name='addPaper'),
    url(r'^getPaperFile/(?P<id>\d+)$', views.getPaperFile, name='getPaperFile'),
    url(r'^deletePaper/(?P<id>\d+)$', views.deletePaper, name='deletePaper'),
    url(r'^viewPaper/(?P<id>\d+)$', views.viewPaper, name='viewPaper'),


    # Project
    url(r'^addProject$', views.addProject, name='addProject'),
    url(r'^addImgProject/(?P<id>\d+)$', views.addImgProject, name='addImgProject'),
    url(r'^getProjectPicture/(?P<id>\d+)$', views.getProjectPicture, name='getProjectPicture'),
    url(r'^seeProject/(?P<id>\d+)$', views.seeProject, name='seeProject'),
    url(r'^project/(?P<id>\d+)$', views.publicSeeProject, name='publicSeeProject'),
    url(r'^editProject/(?P<id>\d+)$', views.editProject, name='editProject'),
    url(r'^deleteProject/(?P<id>\d+)$', views.deleteProject, name='deleteProject'),
    url(r'^getItemPicture/(?P<id>\d+)$', views.getItemPicture, name='getItemPicture'),
    url(r'^addItems/(?P<id>\d+)$', views.addItems, name='addItems'),

    # Posts
    url(r'^addPost$', views.addPost, name='addPost'),
    url(r'^getPostPicture/(?P<id>\d+)$', views.getPostPicture, name='getPostPicture'),
    url(r'^deletePost/(?P<id>\d+)$', views.deletePost, name='deletePost'),
    url(r'^viewPost/(?P<id>\d+)$', views.viewPost, name='viewPost'),

    # Ideas_forum
    url(r'^ideaforum$', views.ideaforum, name='ideaforum'),
    url(r'^likepost/(?P<id>\d+)/$', views.likepost, name='likepost'),
    url(r'^addcomment/(?P<id>\d+)/$',  views.addcomment, name='addcomment'),
    url(r'^deleteComment/(?P<comment_id>\d+)/(?P<idea_id>\d+)/$',  views.deleteComment, name='deleteComment'),
    url(r'^deleteForumComment/(?P<comment_id>\d+)/$',  views.deleteForumComment, name='deleteForumComment'),
)
urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
