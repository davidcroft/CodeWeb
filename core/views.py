# Create your views here.
from django.http import HttpResponse, Http404
from core.models import *
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

from django import forms
from datetime import datetime
from random import randrange

from django.contrib.auth.tokens import default_token_generator
from mimetypes import guess_type

from django.forms.models import inlineformset_factory
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from twython import Twython
import random

#################
##### FORMS #####
#################

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        exclude = ('project',)
        widgets = {
                'itemType' : forms.Select(attrs={'class' : 'form-control'}),
                'text' : forms.Textarea(attrs={'class' : 'form-control', 'rows' : '5', 'cols' : '100', 'placeholder' : 'Type text here'}),
                'video' : forms.Textarea(attrs={'class' : 'form-control', 'rows' : '5', 'cols' : '100', 'placeholder' : 'Put Video Embedding Code here'}),
                }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ('dateTime', 'author',)

class PaperForm(forms.ModelForm):
    class Meta:
        model = Paper
        exclude = ('dateTime', 'author',)

class InfoForm(forms.Form):
    firstName = forms.CharField(max_length=75, label="First Name")
    lastName = forms.CharField(max_length=75, label="Last Name")
    picture = forms.ImageField(label="Profile Picture")

class NewsPostForm(forms.ModelForm):
    class Meta:
        model = NewsPost
        exclude = ('dateTime',)
        widgets = {
                'description' : forms.Textarea(attrs={'class' : 'form-control', 'rows' : '5', 'cols' : '100', 'placeholder' : 'Type news here'}),
                }

class SlideForm(forms.ModelForm):
    class Meta:
        model = Slide

class AboutForm(forms.Form):
    description = forms.CharField(widget = forms.Textarea, required=False)
    picture = forms.ImageField(required=False)

class AdmissionForm(forms.Form):
    description = forms.CharField(widget = forms.Textarea, required=False)
    picture = forms.ImageField(required=False)

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=75,
                             label="Email")
    firstName = forms.CharField(max_length=20)
    lastName = forms.CharField(max_length=20)
    password1 = forms.CharField(max_length=20,
                                label="Password",
                                widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=20,
                                label="Confirm password",
                                widget=forms.PasswordInput())

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(RegistrationForm, self).clean()

        # Confirms that the two password fields match
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data

    # Customizes form validation for the username field.
    def clean_email(self):
        # Confirms that the email is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Email is already registered.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user',)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('dateTime', 'userProfile',)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('dateTime', 'userProfile','userid','post',)



#################
##### VIEWS #####
#################
@transaction.atomic
def sample(request):
    data = {'projectName': 'team7',
            'successMessage': "Great success!"}
    return render_to_response("sample.html", data, context_instance=RequestContext(request))

@transaction.atomic
def index(request):
    data = {}
    data['user'] = request.user
    data['news'] = NewsPost.objects.all()
    data['slides'] = Slide.objects.all()
    print "len of slides is " + str(len(Slide.objects.all()))
    return render_to_response("index.html", data, context_instance=RequestContext(request))

@transaction.atomic
def team(request):
    data = {}
    faculty = UserProfile.objects.filter(degree="Faculty").all()
    phd = UserProfile.objects.filter(degree="Phd").all()
    master = UserProfile.objects.filter(degree="Master").all()
    visitor = UserProfile.objects.filter(degree="Visitor").all()
    alumni = UserProfile.objects.filter(degree="Alumni").all()
    data['faculty'] = faculty
    data['phd'] = phd
    data['master'] = master
    data['visitor'] = visitor
    data['alumni'] = alumni
    return render_to_response("team.html", data, context_instance=RequestContext(request))

@transaction.atomic
def research(request):
    data = {}
    projects = Project.objects.order_by('-dateTime').all()
    papers = Paper.objects.order_by('-dateTime').all()
    data['projects'] = projects
    data['papers'] = papers
    return render_to_response("research.html", data, context_instance=RequestContext(request))

@transaction.atomic
def register(request):
    data = {}
    errors = []

    # Just display the registration form if this is a GET request
    if request.method == 'GET':
        data['form'] = RegistrationForm()
        return render_to_response("register.html", data, context_instance=RequestContext(request))

    form = RegistrationForm(request.POST)
    data['form'] = form

    if not '@' in request.POST['username']:
        errors.append('Invalid email address.')
        data['emailError'] = '* Invalid email address.'
    elif len(User.objects.filter(username = request.POST['username'])) > 0:
        errors.append('Email is already taken.')
        data['emailError'] = '* Email is already taken.'
        print "case2"
    else:
        data['emailError'] = None

    if request.POST['password1'] != request.POST['password2']:
        errors.append('password error')
        data['passwordError'] = '* Passwords did not match.'
    else:
        data['passwordError'] = None


    data['username'] = request.POST['username']
    data['firstName'] = request.POST['firstName']
    data['lastName'] = request.POST['lastName']


    if errors:
        return render_to_response("register.html", data, context_instance=RequestContext(request))

    if not form.is_valid():
        return render_to_response("register.html", data, context_instance=RequestContext(request))

    # Creates the new user from the valid form data
    new_user = User.objects.create_user(username=request.POST['username'],
                                        password=request.POST['password1'],
                                        first_name=request.POST['firstName'],
                                        last_name=request.POST['lastName'])
    new_user.save()
    new_user_profile = UserProfile(user=new_user)
    new_user_profile.token = default_token_generator.make_token(new_user)
    new_user_profile.save()

    return redirect('/myAccount')

@login_required()
@transaction.atomic
def myAccount(request):
    data = {}
    user = request.user
    data['user'] = user
    if user.is_superuser:
        data['slides'] = Slide.objects.all()
        data['news'] = NewsPost.objects.all()
        if len(About.objects.all()) > 0:
            about = About.objects.all()[0]
        else:
            about = None
        data['about'] = about
        if len(Admission.objects.all()) > 0:
            admission = Admission.objects.all()[0]
        else:
            admission = None
        data['admission'] = admission
    else:
        profile = UserProfile.objects.get(user=request.user)
        data['profile'] = profile
        data['projects'] = Project.objects.filter(author=user)
        data['papers'] = Paper.objects.filter(author=user)
        data['posts'] = Post.objects.filter(userProfile=profile)
    return render_to_response("myAccount.html", data, context_instance=RequestContext(request))

@login_required()
@transaction.atomic
def mySlides(request):
    data = {}
    slide_form = SlideForm()
    data['slide_form'] = slide_form
    return render_to_response("mySlides.html", data, context_instance=RequestContext(request))

@login_required()
@transaction.atomic
def addSlide(request, id):
    data = {}
    slide = Slide.objects.get(id=id)
    if request.method == 'POST':
        form = SlideForm(request.POST, request.FILES, instance=slide)
        if not form.is_valid():
            print form
            print "Slide show form is invalid"
            data['slide_form'] = form
            return render_to_response("mySlides.html", data, context_instance=RequestContext(request))
        slide = form.save(commit=False)
        slide.id = id
        slide.save()
        return redirect('/myAccount')
    # GET request
    slide = None
    if len(Slide.objects.all()) > 0:
        slide = Slide.objects.all()[0]
    form = SlideForm(instance = slide)
    data['slide'] = slide
    data['slide_form'] = form
    return render_to_response("mySlides.html", data, context_instance=RequestContext(request))

@login_required()
@transaction.atomic
def editSlide(request, id=None):
    data = {}
    if request.method == 'POST':
        form = SlideForm(request.POST, request.FILES)
        if not form.is_valid():
            print "Slide show form is invalid"
            data['slide_form'] = form
            return render_to_response("editSlides.html", data, context_instance=RequestContext(request))
        slide = form.save()
        return HttpResponseRedirect(reverse('editSlide', args=(slide.id,)))
    # GET request
    slide = None
    if id:
        slide = Slide.objects.get(id=id)
    form = SlideForm(instance = slide)
    data['slide'] = slide
    data['slide_form'] = form
    return render_to_response("editSlides.html", data, context_instance=RequestContext(request))


@login_required()
@transaction.atomic
def deleteSlide(request, id):
    data = {}
    form = SlideForm()
    slide = Slide.objects.get(id=id)
    slide.delete()
    return redirect('/myAccount')


@login_required()
@transaction.atomic
def addNewsPost(request, id=None):
    data = {}
    if request.method == 'GET':
        news_form = NewsPostForm()
        data['news_form'] = news_form
        return render_to_response("myNews.html", data, context_instance=RequestContext(request))
    else:
        # POST
        news = NewsPost.objects.get(id=id)
        if 'upload' in request.POST:
            print "PRESSED UPLOAD"
            news_form = NewsPostForm(request.POST, request.FILES, instance = news)
            new_news = news_form.save(commit=False)
            new_news.dateTime = datetime.now()
            new_news.id = id
            new_news.save()
            return redirect('/editNewsPost/' + str(new_news.id))
        news_form = NewsPostForm(request.POST, request.FILES, instance = news)
        if not news_form.is_valid():
            print "Invalid Form"
            return render_to_response("myNews.html", data, context_instance=RequestContext(request))
        new_news = news_form.save(commit=False)
        new_news.dateTime = datetime.now()
        new_news.id = id
        new_news.save()
        return redirect('/myAccount')

@login_required()
@transaction.atomic
def editNewsPost(request, id=None):
    data = {}
    if request.method == 'POST':
        news_form = NewsPostForm(request.POST, request.FILES)
        new_news = news_form.save(commit=False)
        new_news.dateTime = datetime.now()
        new_news.save()
        return HttpResponseRedirect(reverse('editNewsPost', args=(new_news.id,)))
    # GET
    print "editNewsPost GET"
    news = NewsPost.objects.get(id=id)
    news_form = NewsPostForm(instance = news)
    data['news_form'] = news_form
    print news_form
    data['news'] = news
    return render_to_response("editMyNews.html", data, context_instance=RequestContext(request))

@login_required()
@transaction.atomic
def deleteNewsPost(request, id):
    newsPost = NewsPost.objects.get(id=id)
    newsPost.delete()
    return redirect('/myAccount')

@transaction.atomic
def publicSeeNewsPost(request, id):
    data = {}
    newsPost = NewsPost.objects.get(id=id)
    data['newsPost'] = newsPost
    return render_to_response("newsPost.html", data, context_instance=RequestContext(request))

@transaction.atomic
def seeNewsPost(request, id):
    data = {}
    newsPost = NewsPost.objects.get(id=id)
    data['newsPost'] = newsPost
    return render_to_response("seePost.html", data, context_instance=RequestContext(request))

@transaction.atomic
def getNewsPostPicture(request, id):
    newsPost = get_object_or_404(NewsPost, id=id)
    if not newsPost.picture:
        raise Http404
    content_type = guess_type(newsPost.picture.name)
    return HttpResponse(newsPost.picture, mimetype=content_type)


@transaction.atomic
def getSlidePicture(request, id):
    slide = get_object_or_404(Slide, id=id)
    if not slide.picture:
        raise Http404
    content_type = guess_type(slide.picture.name)
    return HttpResponse(slide.picture, mimetype=content_type)

@login_required()
@transaction.atomic
def editAdminProfile(request):
    data = {}
    data['user'] = request.user
    data['profile'] = UserProfile.objects.get(user=request.user)
    #return render_to_response("myProfile.html", data, context_instance=RequestContext(request))
    return HttpResponse("myProfile.html")

@login_required()
@transaction.atomic
def editProfile(request):
    data = {}
    data['user'] = request.user
    profile = UserProfile.objects.get(user=request.user)
    data['profile'] = profile
    #print "test", profile.picture 
    if request.method == 'GET':
        print "GET"
        profileForm = ProfileUpdateForm(instance=profile)
        data['profileForm'] = profileForm
        return render_to_response("myProfile.html", data, context_instance=RequestContext(request))

    # POST
    if 'upload' in request.POST:
        profileForm = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        data['profileForm'] = profileForm
        if profileForm.is_valid():
            print "POST valid"
            profile = profileForm.save()
            profile.save()
            return HttpResponseRedirect(reverse('editProfile', args=()))
        return render_to_response("myProfile.html", data, context_instance=RequestContext(request))
    return updateProfile(request)

@login_required()
@transaction.atomic
def updateProfile(request):
    data = {}
    data['user'] = request.user
    # update the info of user
    editUser = UserProfile.objects.get(user=request.user)
    user = User.objects.get(username=request.user.username)
    data['profile'] = editUser

    if request.method == 'GET':
        profileForm = ProfileUpdateForm(instance=profile)
        #print profileForm
        data['profileForm'] = profileForm
        return render_to_response("myAccount.html", data, context_instance=RequestContext(request))
        
    ####### POST ####################
    if 'firstName' in request.POST and request.POST['firstName']:
        user.first_name = request.POST['firstName']
        #print "update firstName"
    if 'lastName' in request.POST and request.POST['lastName']:
        user.last_name = request.POST['lastName']

    user.save()
    profile = UserProfile.objects.get(user=request.user)
    data['profile'] = profile

    ##############
    profileForm = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
    if profileForm.is_valid():
        profile = profileForm.save()
        profile.save()
    data['profileForm'] = profileForm
    #############

    #print "testEditUser", editUser.user.first_name
    #print "testUser", user.first_name
    ##### password update ####
    if 'passwordOld' in request.POST and 'passwordNew' in request.POST and 'passwordNewConfirm' in request.POST:
        if request.POST['passwordOld'] and user.check_password(request.POST['passwordOld']):
            if not request.POST['passwordNew'] or request.POST['passwordNew'] != request.POST['passwordNewConfirm']:
                data['passwordOldError'] = ''
                data['passwordNewError'] = '* Please input the same non-empty new password'
                return render_to_response("myProfile.html", data, context_instance=RequestContext(request))
            elif request.POST['passwordNew'] == request.POST['passwordOld']:
                data['passwordOldError'] = ''
                data['passwordNewError'] = '* Please input the a different new password.'
                return render_to_response("myProfile.html", data, context_instance=RequestContext(request))
            else:
                data['passwordOldError'] = ''
                data['passwordNewError'] = ''
                user.set_password(request.POST['passwordNew'])
                user.save()
        elif request.POST['passwordOld'] and not user.check_password(request.POST['passwordOld']):
            data['passwordNewError'] = ''
            data['passwordOldError'] = '* Please input the correct old password.'
            return render_to_response("myProfile.html", data, context_instance=RequestContext(request))
        elif not request.POST['passwordOld'] and (request.POST['passwordNew'] or request.POST['passwordNewConfirm']):
            data['passwordNewError'] = ''
            data['passwordOldError'] = '* Please input the correct old password first.'
            return render_to_response("myProfile.html", data, context_instance=RequestContext(request))
    ##########################
    #return render_to_response("myAccount.html", data, context_instance=RequestContext(request))
    return redirect('/myAccount')

@transaction.atomic
def getProfilePicture(request, email):
    user = User.objects.get(username=email)
    profile = UserProfile.objects.get(user=user)
    #print profile.website
    #print "test", profile.cropPicture
    if profile.picture:
        content_type = guess_type(profile.picture.name)
        print "have image"
        return HttpResponse(profile.picture, mimetype=content_type)
    else:
        print "have no image"
        return HttpResponse("No imagefile")


@transaction.atomic    
def getProjectPicture(request, id):
    project = get_object_or_404(Project, id=id)
    if not project.picture:
        raise Http404
    content_type = guess_type(project.picture.name)
    return HttpResponse(project.picture, mimetype=content_type)

@transaction.atomic
def getItemPicture(request, id):
    print "testGetImage"
    item = get_object_or_404(Item, id=id)
    if not item.image:
        raise Http404
    content_type = guess_type(item.image.name)
    return HttpResponse(item.image, mimetype=content_type)

@login_required()
@transaction.atomic
def myInformation(request):
    data = {}
    user = request.user
    data['user'] = user

    # Just display the Info form if this is a GET request
    if request.method == 'GET':
        data['form'] = InfoForm()
        return render_to_response("myInformation.html", data, context_instance=RequestContext(request))

    form = InfoForm(request.POST, request.FILES)
    data['form'] = form
    if not form.is_valid():
        return render_to_response("myInformation.html", data, context_instance=RequestContext(request))

    # Change user fields
    user.first_name = form.cleaned_data['firstName']
    user.last_name = form.cleaned_data['lastName']
    user.save()
    user_profile = UserProfile.objects.get(user=user)
    user_profile.picture = form.cleaned_data['picture']
    user_profile.save()

    return redirect('/myAccount')

@login_required()
@transaction.atomic
def myProjects(request):
    data = {}
    user = request.user
    data['user'] = user
    data['projects'] = Project.objects.filter(author=user)
    return render_to_response("myProjects.html", data, context_instance=RequestContext(request))

@login_required()
@transaction.atomic
def addProject(request):
    data = {}
    user = request.user
    data['user'] = user
    data['profile'] = UserProfile.objects.get(user=user)
    ItemFormSet = formset_factory(ItemForm)

    # Just display the Project form if this is a GET request
    if request.method == 'GET':
        data['form_project'] = ProjectForm()
        data['formset'] = ItemFormSet()
        return render_to_response("addProject.html", data, context_instance=RequestContext(request))

    print "POST"
    form_project = ProjectForm(request.POST, request.FILES)
    data['form_project'] = form_project
    item_forms = ItemFormSet(request.POST, request.FILES)
    data['formset'] = item_forms

    if not form_project.is_valid() or not item_forms.is_valid():
        print "not valid forms"
        print form_project
        return render_to_response("addProject.html", data, context_instance=RequestContext(request))

    # Save the project
    project = form_project.save(commit=False)
    project.dateTime = datetime.now()
    project.author = user
    project.save()

    # Save the items
    for itemForm in item_forms:
        item = itemForm.save(commit=False)
        item.project = project
        item.save()
    #return redirect('/editProject/' + str(project.id))
    if project.picture:
        return redirect('/addImgProject/' + str(project.id))
    else:
        return redirect('/myAccount')

@login_required
@transaction.atomic
def addImgProject(request, id):
    data = {}
    project = Project.objects.get(id=id)
    user = request.user
    data['user'] = user
    data['profile'] = UserProfile.objects.get(user=request.user)
    data['project'] = project
    items = Item.objects.filter(project=project)
    data['items'] = items
    ItemFormSet = formset_factory(ItemForm)

    # Just display the Project form if this is a GET request
    if request.method == 'GET':
        print ProjectForm(instance=project) 
        data['form_project'] = ProjectForm(instance=project)
        initialValues = []
        for item in items:
            form = {}
            form['itemType'] = item.itemType
            form['text'] = item.text
            form['image'] = item.image
            form['video'] = item.video
            initialValues.append(form)
        formset = ItemFormSet(initial=initialValues)
        data['formset'] = formset[:len(formset)-1]
        return render_to_response("addImgProject.html", data, context_instance=RequestContext(request))

    print "POST"
    form_project = ProjectForm(request.POST, request.FILES, instance=project)
    data['form_project'] = form_project
    item_forms = ItemFormSet(request.POST, request.FILES)
    data['formset'] = item_forms

    if not form_project.is_valid() or not item_forms.is_valid():
        return render_to_response("addImgProject.html", data, context_instance=RequestContext(request))

    # Save the project
    project = form_project.save(commit=False)
    project.dateTime = datetime.now()
    project.author = user
    project.save()

    i = 0
    for itemForm in item_forms:
        if i < len(items):
            old_item = Item.objects.filter(project=project)[i]
            item = itemForm.save(commit=False)
            item.project = project
            item.id = old_item.id
            key = 'form-' + str(i) + '-image'
            if request.FILES and key in request.FILES:
                item.image = request.FILES[key]
            else:
                if item.itemType == 'image' and old_item.image:
                    item.image = old_item.image
            item.save()
        else:
            item = itemForm.save(commit=False)
            item.project = project
            item.save()
        i += 1

    return redirect('/myAccount')

@login_required()
@transaction.atomic
def deleteProject(request, id):
    data = {}
    user = request.user
    data['user'] = user
    data['profile'] = UserProfile.objects.get(user=user)
    project_to_delete = Project.objects.get(id=id)
    if project_to_delete:
        items = Item.objects.filter(project=project_to_delete)
        for item in items:
            item.delete()
        project_to_delete.delete()
    data['projects'] = Project.objects.filter(author=user)
    return redirect('/myAccount')

@login_required()
@transaction.atomic
def addItems(request, id):
    data = {}
    user = request.user
    data['user'] = user
    data['project_id'] = id
    project = Project.objects.get(id=id)
    ItemFormSet = formset_factory(ItemForm)

    if request.method == 'GET':
        data['formset'] = ItemFormSet()
        return render_to_response("addItems.html", data, context_instance=RequestContext(request))

    item_forms = ItemFormSet(request.POST, request.FILES)
    data['formset'] = item_forms
    if not item_forms.is_valid():
        return render_to_response("addItems.html", data, context_instance=RequestContext(request))

    for itemForm in item_forms:
        item = itemForm.save(commit=False)
        item.project = project
        item.save()

    return redirect('/myAccount')

@login_required
@transaction.atomic
def seeProject(request, id):
    data = {}
    project = Project.objects.get(id=id)
    data['profile'] = UserProfile.objects.get(user=request.user)
    data['project'] = project
    items = Item.objects.filter(project=project)
    data['items'] = items
    return render_to_response("seeProject.html", data, context_instance=RequestContext(request))

@transaction.atomic
def publicSeeProject(request, id):
    data = {}
    project = Project.objects.get(id=id)
    data['project'] = project
    items = Item.objects.filter(project=project)
    data['items'] = items
    return render_to_response("publicSeeProject.html", data, context_instance=RequestContext(request))

@login_required
@transaction.atomic
def editProject(request, id):
    data = {}
    project = Project.objects.get(id=id)
    user = request.user
    data['user'] = user
    data['profile'] = UserProfile.objects.get(user=request.user)
    data['project'] = project
    items = Item.objects.filter(project=project)
    data['items'] = items
    ItemFormSet = formset_factory(ItemForm)

    # Just display the Project form if this is a GET request
    if request.method == 'GET':
        print ProjectForm(instance=project) 
        data['form_project'] = ProjectForm(instance=project)
        initialValues = []
        for item in items:
            form = {}
            form['itemType'] = item.itemType
            form['text'] = item.text
            form['image'] = item.image
            form['video'] = item.video
            initialValues.append(form)
        formset = ItemFormSet(initial=initialValues)
        data['formset'] = formset[:len(formset)-1]
        return render_to_response("editProject.html", data, context_instance=RequestContext(request))

    print "POST"
    form_project = ProjectForm(request.POST, request.FILES, instance=project)
    data['form_project'] = form_project
    item_forms = ItemFormSet(request.POST, request.FILES)
    data['formset'] = item_forms

    if not form_project.is_valid() or not item_forms.is_valid():
        return render_to_response("editProject.html", data, context_instance=RequestContext(request))

    # Save the project
    project = form_project.save(commit=False)
    project.dateTime = datetime.now()
    project.author = user
    project.save()


    i = 0
    for itemForm in item_forms:
        if i < len(items):
            old_item = Item.objects.filter(project=project)[i]
            item = itemForm.save(commit=False)
            item.project = project
            item.id = old_item.id
            key = 'form-' + str(i) + '-image'
            if request.FILES and key in request.FILES:
                item.image = request.FILES[key]
            else:
                if item.itemType == 'image' and old_item.image:
                    item.image = old_item.image
            item.save()
        else:
            item = itemForm.save(commit=False)
            item.project = project
            item.save()
        i += 1

    return redirect('/seeProject/' + str(id))

@login_required()
@transaction.atomic
def myPapers(request):
    data = {}
    user = request.user
    data['user'] = user
    data['papers'] = Paper.objects.filter(author=user)
    return render_to_response("myPapers.html", data, context_instance=RequestContext(request))

@login_required()
@transaction.atomic
def addPaper(request):
    data = {}
    data['user'] = request.user
    data['profile'] =UserProfile.objects.get(user=request.user)

    if request.method == 'GET':
        data['form'] = PaperForm()
        return render_to_response("addPaper.html", data, context_instance=RequestContext(request))

    form = PaperForm(request.POST, request.FILES)
    data['form'] = form

    if not form.is_valid():
        return render_to_response("addPaper.html", data, context_instance=RequestContext(request))

    # Creates a new paper if it is present as a parameter in the request
    new_paper = form.save(commit=False)
    new_paper.dateTime = datetime.now()
    new_paper.author = request.user
    new_paper.save()
    return redirect('/myAccount')



@login_required()
@transaction.atomic
def deletePaper(request, id):
    data = {}
    form = PaperForm()
    data['user'] = request.user
    data['form'] = form
    paper = Paper.objects.get(id=id)
    if paper.fileDoc:
            paper.fileDoc.delete(save=False)
    paper.delete()
    #data['papers'] = Paper.objects.all()
    #return render_to_response("myPapers.html", data, context_instance=RequestContext(request))
    return redirect('/myAccount')


@transaction.atomic
def getPaperFile(request, id):
    paper = get_object_or_404(Paper, id=id)
    if not paper.file:
        raise Http404
    content_type = guess_type(paper.file.name)
    return HttpResponse(paper.picture, mimetype=content_type)

@login_required
@transaction.atomic
def viewPaper(request, id):
    data = {}
    paper = Paper.objects.get(id=id)
    data['paper'] = paper
    pdf = paper.fileDoc
    response = HttpResponse(pdf, "application/pdf")
    response['Content-Disposition'] = 'attachment; filename=%s.pdf' %paper.topic
    return response
    #return HttpResponse(paper.read(), mimetype='application/pdf')
    #return render_to_response("viewPaper.html", data, context_instance=RequestContext(request))


###################
##### HELPERS #####
###################

@transaction.atomic
def about(request):
    data = {}
    data['user'] = request.user
    data['about'] = About.objects.all()
    return render_to_response("about.html", data, context_instance=RequestContext(request))

@login_required()
@transaction.atomic
def myAbout(request):
    data = {}
    user = request.user
    data['user'] = user
    about = None
    if len(About.objects.all()) > 0:
        about = About.objects.all()[0]
    data['about'] = about
    return render_to_response("myAbout.html", data, context_instance=RequestContext(request))

@login_required()
@transaction.atomic
def editAbout(request):
    data = {}
    form = AboutForm(request.POST, request.FILES)
    data['user'] = request.user
    if len(About.objects.all()) > 0:
        data['about'] = About.objects.all()[0]
    else:
        data['about'] = About.objects.all()
    data['form'] = form
    if not form.is_valid():
        print "form is invalid"
        return render_to_response("myAbout.html", data, context_instance=RequestContext(request))
    # Creates a new post if it is present as a parameter in the request

    if len(About.objects.all()) <= 0:
        about = About(description=form.cleaned_data['description'],
                        picture=form.cleaned_data['picture'],
                        dateTime = datetime.now())
    else:
        about = About.objects.all()[0]
        about.description = form.cleaned_data['description']
        about.picture = form.cleaned_data['picture']
        about.dateTime = datetime.now()
    about.save()
    #return render_to_response("myAbout.html", data, context_instance=RequestContext(request))
    return redirect('/myAccount')

@transaction.atomic
def getAboutPicture(request, id):
    about = get_object_or_404(About, id=id)
    if not about.picture:
        raise Http404
    content_type = guess_type(about.picture.name)
    return HttpResponse(about.picture, mimetype=content_type)

@login_required()
@transaction.atomic
def deleteAbout(request, id):
    data = {}
    form = AboutForm()
    data['user'] = request.user
    data['form'] = form
    old_about = About.objects.get(id=id)
    old_about.delete()
    data['about'] = About.objects.all()
    return render_to_response("myAbout.html", data, context_instance=RequestContext(request))

@transaction.atomic
def admission(request):
    data = {}
    data['user'] = request.user
    data['admission'] = Admission.objects.all()
    return render_to_response("admission.html", data, context_instance=RequestContext(request))

@login_required()
@transaction.atomic
def myAdmission(request):
    data = {}
    user = request.user
    data['user'] = user
    admission = None
    if len(Admission.objects.all()) > 0:
        admission = Admission.objects.all()[0]
    data['admission'] = admission
    return render_to_response("myAdmission.html", data, context_instance=RequestContext(request))

@login_required()
@transaction.atomic
def editAdmission(request):
    data = {}
    form = AdmissionForm(request.POST, request.FILES)
    data['user'] = request.user
    if len(Admission.objects.all()) > 0:
        data['admission'] = Admission.objects.all()[0]
    else:
        data['admission'] = Admission.objects.all()
    data['form'] = form
    if not form.is_valid():
        return render_to_response("myAdmission.html", data, context_instance=RequestContext(request))
    # Creates a new post if it is present as a parameter in the request

    if len(Admission.objects.all()) <= 0:
        admission = Admission(description=form.cleaned_data['description'],
                              picture=form.cleaned_data['picture'],
                              dateTime = datetime.now())
    else:
        admission = Admission.objects.all()[0]
        admission.description = form.cleaned_data['description']
        admission.picture = form.cleaned_data['picture']
        admission.dateTime = datetime.now()

    admission.save()
    #return render_to_response("myAdmission.html", data, context_instance=RequestContext(request))
    return redirect('/myAccount')


@transaction.atomic
def getAdmissionPicture(request, id):
    admission = get_object_or_404(Admission, id=id)
    if not admission.picture:
        raise Http404
    content_type = guess_type(admission.picture.name)
    return HttpResponse(admission.picture, mimetype=content_type)

@login_required()
@transaction.atomic
def deleteAdmission(request, id):
    data = {}
    form = AdmissionForm()
    data['user'] = request.user
    data['form'] = form
    old_admission = Admission.objects.get(id=id)
    old_admission.delete()
    data['admission'] = Admission.objects.all()
    return render_to_response("myAdmission.html", data, context_instance=RequestContext(request))

# Forum Posts
@login_required()
@transaction.atomic
def myPosts(request):
    data = {}
    user = request.user
    data['user'] = user
    data['posts'] = Post.objects.filter(user=user)
    return render_to_response("myPosts.html", data, context_instance=RequestContext(request))

@login_required()
@transaction.atomic
def addPost(request):
    data = {}
    data['user'] = request.user
    data['profile'] =UserProfile.objects.get(user=request.user)

    if request.method == 'GET':
        data['form'] = PostForm()
        return render_to_response("addPost.html", data, context_instance=RequestContext(request))
    form = PostForm(request.POST, request.FILES)
    data['form'] = form

    if not form.is_valid():
        return render_to_response("addPost.html", data, context_instance=RequestContext(request))

    # Creates a new paper if it is present as a parameter in the request
    new__forum_post = form.save(commit=False)
    new__forum_post.dateTime = datetime.now()
    new__forum_post.userProfile = UserProfile.objects.get(user=request.user)
    new__forum_post.likes = 0
    new__forum_post.save()
    # data['posts'] = Post.objects.filter(user=request.user)
    # return render_to_response("myAccount.html", data, context_instance=RequestContext(request))
    return redirect('/myAccount')


@login_required()
@transaction.atomic
def deletePost(request, id):
    data = {}
    form = PostForm()
    data['user'] = request.user
    data['form'] = form
    post = Post.objects.get(id=id)
    post.delete()
    # data['posts'] = Post.objects.all()
    # return render_to_response("myAccount.html", data, context_instance=RequestContext(request))
    return redirect('/myAccount')


@transaction.atomic
def getPostPicture(request, id):
    post = get_object_or_404(Post, id=id)
    if not post.picture:
        raise Http404
    content_type = guess_type(post.picture.name)
    return HttpResponse(post.picture, mimetype=content_type)

@login_required()
@transaction.atomic
def viewPost(request, id):
    data = {}
    post = Post.objects.get(id=id)
    data['post'] = post
    data['comments'] = Comment.objects.all()
    data['user'] = request.user
    data['profile'] = UserProfile.objects.get(user=request.user)
    return render_to_response("viewPost.html", data, context_instance=RequestContext(request))


# Idea Forum
@login_required
@transaction.atomic
def ideaforum(request):
    data = {}
    data['posts'] = Post.objects.all()
    data['comments'] = Comment.objects.all()
    data['user'] = request.user
    return render_to_response("ideaforum.html", data, context_instance=RequestContext(request))

@login_required
@transaction.atomic
def likepost(request, id):
    post=Post.objects.get(id=id)
    number_likes = post.likes
    number_likes = number_likes + 1
    post.likes = number_likes
    post.save()
    return redirect(reverse('ideaforum'))

@login_required()
@transaction.atomic
def addcomment(request, id):
    data = {}
    data['user'] = request.user
    data['profile'] =UserProfile.objects.get(user=request.user)
    the_post = Post.objects.get(id=id)

    if request.method == 'GET':
        data['form'] = CommentForm()
        return render_to_response("ideaforum.html", data, context_instance=RequestContext(request))

    form = CommentForm(request.POST, request.FILES)
    data['form'] = form

    if not form.is_valid():
        print(form)
        return render_to_response("ideaforum.html", data, context_instance=RequestContext(request))

    # Creates a new paper if it is present as a parameter in the request
    new_comment = form.save(commit=False)
    new_comment.dateTime = datetime.now()
    new_comment.userProfile = UserProfile.objects.get(user=request.user)
    new_comment.post = the_post
    new_comment.save()
    # data['posts'] = Post.objects.filter(user=request.user)
    # return render_to_response("myAccount.html", data, context_instance=RequestContext(request))
    if 'ideaForumSubmit' in request.POST:
        return redirect('/ideaforum')
    return redirect('/viewPost/'+str(id))

@login_required()
@transaction.atomic
def deleteComment(request, comment_id, idea_id):
    data = {}
    comment = Comment.objects.get(id=comment_id)
    comment.delete()
    return redirect('/viewPost/'+str(idea_id))

@login_required()
@transaction.atomic
def deleteForumComment(request, comment_id):
    data = {}
    comment = Comment.objects.get(id=comment_id)
    comment.delete()
    return redirect('/ideaforum')

###################
##### HELPERS #####

@transaction.atomic
def getTweets(request):
    APP_KEY = '1SnZ9QQYXD4Y0KVFY3QUXVvnS'
    APP_SECRET = 'wXRDKSZzcbAzpx5cNf2vuAuWxWO9sxDxKtyruFyPLyPLwUuXJ9'
    twitter = Twython(APP_KEY, APP_SECRET)

    arch = twitter.get_user_timeline(screen_name='CMUsoarch', count=10)
    design = twitter.get_user_timeline(screen_name='cmudesign', count=10)
    art = twitter.get_user_timeline(screen_name='SOA_CMU', count=10)

    tweets = []
    for item in arch:
        tweets.append({'text' : item['text'], 'id' : int(item['id']), 'department' : 'arch'})
    for item in design:
        tweets.append({'text' : item['text'], 'id' : int(item['id']), 'department' : 'design'})
    for item in art:
        tweets.append({'text' : item['text'], 'id' : int(item['id']), 'department' : 'art'})

    data = {}
    data['user'] = request.user
    ori_tweets = Tweet.objects.all()
    for tweet in ori_tweets:
        tweet.delete()
    random.shuffle(tweets)
    for tweet in tweets:
        new_tweet = Tweet(text=tweet['text'], url="www.twitter.com/statuses/" + str(tweet['id']), department=tweet['department'])
        new_tweet.save()
    data['tweets'] = Tweet.objects.all()
    #data['tweets'] = Tweet.objects.order_by('?')

    return render_to_response("getTweets.html", data, context_instance=RequestContext(request))
