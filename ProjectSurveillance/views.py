from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, F, Value, Case, When
from django.contrib.auth.models import User, Group
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta, datetime
from django.core import serializers
import json

from .models import *
from .forms import ProjectForm, UserForm, OrgForm, SignUpForm


def error_404(request):
    data = {}
    return render(request, 'ProjectSurveillance/404.html', data)

def error_500(request):
    data = {}
    return render(request, 'ProjectSurveillance/500.html', data)

@login_required(login_url='/login/')
def dashboard(request):
    #Serves the main dashboard to the user. Login is required.
    #gives the projects under each phase
    #params: get request only. Some calls may be an ajax (such as all active projects)
    #return: a rendered html page
    
    ip = request.META['REMOTE_ADDR']
    print(ip)
    if request.user.is_authenticated():
        days_from_today = timezone.now() - timedelta(days = 90)
        #recent_projects = Project.objects.filter(projectdetail__detailtypeid = 7, projectdetail__dateofevent__gte = days_from_today)[:8]

        projects = Project.objects.filter(archive__isnull = True)

        preproj =  projects.filter(phaseid = 1)
        newsub = projects.filter(phaseid = 2)
        newlogging = projects.filter(phaseid = 3)
        appreview = projects.filter(phaseid = 4)
        revision = projects.filter(phaseid = 5)
        duadraftrev = projects.filter(phaseid = 6)
        reqduarev = projects.filter(phaseid = 7)
        appclose = projects.filter(phaseid = 8)
        datareqproc = projects.filter(phaseid = 9)
        datasec = projects.filter(phaseid = 10)
        dataclose = projects.filter(phaseid = 11)
                    
        data = {#'recent_projects': recent_projects,
                'total_projects': Project.objects.count(),
                'total_users': VSUser.objects.count(),
                'total_open_projects': Project.objects.exclude(projectdetail__detailtypeid = 73).count(),
                'total_orgs': Organization.objects.count(),
                'preproj': preproj, 'newsub': newsub, 'newlogging': newlogging, 'appreview': appreview, 'revision': revision, 'duadraftrev': duadraftrev, 'reqduarev': reqduarev,
                'appclose': appclose, 'datareqproc': datareqproc, 'datasec': datasec, 'dataclose': dataclose}
    else:
        data = {'statement' : "Please login to see your dashboard"}

    return render(request, 'ProjectSurveillance/dashboard.html', data)

@login_required(login_url='/login/')
def update_phase(request):
    if request.method == 'POST':
        #be wary of changes to the project id in the front end, the proj_id should correspond primary key of the phase
        proj_id = request.POST.get("proj_id", None)
        new_phase = request.POST.get("new_phase", None)

        if proj_id and new_phase:
            try:
                p = Project.objects.get(projectid = proj_id)
                p.phaseid = WorkPhase.objects.get(phaseid = new_phase)
                p.save()
                success = True
            except Exception as e:
                print(e.args)
                success = False


        data = {"success": success}

        return JsonResponse(data)

def all_users(request):
    #Serves a table of all of the users, with a pagination bar, and a search option
    #params: a get request only
    #return: an html page
    
    if request.method == 'GET':
        search_query = request.GET.get('searchbox',None)

        if search_query is not None:
            #if the query seems to be one term
            if len(search_query.split()) == 1:
                    user_list = VSUser.objects.filter(
                            Q(fname__icontains=search_query) | Q(lname__icontains=search_query) | Q(useremail__icontains=search_query)
                            ).order_by("fname")
            #if the query seems to be first name and last name
            elif len(search_query.split()) > 1:
                    part_name = search_query.split()
                    user_list = VSUser.objects.filter(fname__icontains=part_name[0], lname__icontains=part_name[1])
            #if user enters spaces or other characters
            else:
                    user_list = VSUser.objects.exclude(userorganization__archive = True).order_by("fname")
        else:
            #if user does not do a search
            user_list = VSUser.objects.exclude(userorganization__archive = True).order_by("fname")

        page = 1                            
        paginator = Paginator(user_list, 50)

        try:
                users = paginator.page(page)
        except PageNotAnInteger:
                users = paginator.page(1)
        except EmptyPage:
                users = paginator.page(paginator.num_pages)

        index = users.number - 1
        max_index = len(paginator.page_range)
        if index >= 3:
            if index >= max_index - 2:
                    start_index =  max_index - 5
                    end_index = max_index
            else:
                    start_index = index - 2
                    end_index = index + 3
        else:
            start_index = 0
            end_index = 5

        page_range = paginator.page_range[start_index:end_index]
        return render(request, 'ProjectSurveillance/userview.html', {'users': users, 'page_range': page_range})

def user_details(request, pk):
    #returns info of specific user
    #params: a get request only and a primary key indicating which project we are getting specific details for
    #return: rendered html page of specific user's info
    
    user = get_object_or_404(VSUser, pk=pk)

    #get user's projects
    projects_with_user = Project.objects.filter(userproject__userid = pk).values_list('projectid', 'projname', 'archive', 'userproject__archive')
    
    #get user's organization
    orgs_with_user = Organization.objects.filter(userorganization__userid = pk).exclude(userorganization__archive = True)
    #if more than one org returned for the user, then send a note to the template
    if(orgs_with_user.count() > 1):
        many_orgs_flag = True
    else:
        many_orgs_flag = False
    org_with_user = orgs_with_user.first()

    #get user's bvs confidentiality
    dates = ProjectDetail.objects.filter(Q(detailtypeid = 72) | Q(detailtypeid = 71), userid = pk)
    #date requested
    req_obj = dates.filter(detailtypeid = 72)
    #date signed
    signed_obj = dates.filter(detailtypeid = 71)
    #get user drive access
    drive_access = DetailType.objects.filter(projectdetail__userid = pk, drive = True).order_by('detaildesc').values_list('detaildesc','projectdetail__note')

    return render(request, 'ProjectSurveillance/indivuserview.html', {'userdetail': user,
                                                                      'projects' : projects_with_user,
                                                                      'org': org_with_user,
                                                                      'signed': signed_obj,
                                                                      'requested': req_obj,
                                                                      'drive_access': drive_access,
                                                                      'many_orgs_flag': many_orgs_flag})

def all_users_ajax(request):
    #updates the table if user made a pagination request/sort request/search request
    #params: must be an ajax get request
    #returns: html code to replace a certain section of the webpage
    
    if request.method == 'GET' and request.is_ajax():
        search_query = request.GET.get('search_query',None)
        sorttype = request.GET.get('sorttype', None)
        cattype = request.GET.get('cattype', None)

        #check if user made an ajax call to sort the current page of users
        sortstring = "-" if sorttype == "dsc" else ""

        if cattype == "id-sort-icon":
            cattype = "userid"
        elif cattype == "email-sort-icon":
            cattype = "useremail"
        elif cattype == "lname-sort-icon":
            cattype = "lname"
        else:
            cattype = "fname"
        
        if search_query is not None:
            #if the query seems to be one term
            if len(search_query.split()) == 1:
                user_list = VSUser.objects.filter(
                    Q(fname__icontains=search_query) | Q(lname__icontains=search_query) | Q(useremail__icontains=search_query)
                    ).order_by(sortstring + cattype)
            #if the query seems to be first name and last name
            elif len(search_query.split()) > 1:
                part_name = search_query.split()
                user_list = VSUser.objects.filter(fname__icontains=part_name[0], lname__icontains=part_name[1]).order_by(sortstring + cattype)
            #if user enters spaces or other characters
            else:
                user_list = VSUser.objects.exclude(userorganization__archive = True).order_by(sortstring + cattype)
        else:
            #if user does not do a search
            user_list = VSUser.objects.exclude(userorganization__archive = True).order_by(sortstring + cattype)

        page = request.GET.get('desired_page',1)
                                                
        paginator = Paginator(user_list, 50)

        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)

        index = users.number - 1
        max_index = len(paginator.page_range)
        if index >= 3:
            if index >= max_index - 2:
                if max_index < 5:
                    start_index = 0
                else:
                    start_index =  max_index - 5
                end_index = max_index
            else:
                start_index = index - 2
                end_index = index + 3
        else:
            start_index = 0
            end_index = 5

        page_range = paginator.page_range[start_index:end_index]
        data = {}

        #we will just assign users to the projects key, so we can just reuse the paginationajax template
        context1 = {'projects' : users, 'page_range': page_range}
        context2 = {'users': users}
        data['html_page'] = render_to_string('ProjectSurveillance/paginationajax.html', context1, request=request)
        data['html_table'] = render_to_string('ProjectSurveillance/userviewajax.html', context2, request=request)
        return JsonResponse(data)

@login_required(login_url="/login/")
def user_details_update_modal(request):
	#this function is used by the function user_details_update
	#params: get requests will get the projects currently associated with user
	#		post requests will decide whether or not to archive each user project relationship
	#return: get requests will return an html page populating the modal html

	if request.method == 'GET' and request.is_ajax():
		user_id = request.GET.get("user_id", None)

		#get all user's projects
		projects = Project.objects.filter(userproject__userid = user_id).values_list('projectid','projname','userproject__archive')

		context = {'projects': projects}
		data = {}
		data['html_form'] = render_to_string('ProjectSurveillance/userprojarchivemodal.html', context, request=request)

		return JsonResponse(data)
	if request.method == 'POST' and request.is_ajax():
		user_id = request.POST.get("user_id", None)
		#jquery sends this dictionary of dictionary into a string, so you have to make it a json dict
		proj_archive_dict = json.loads(request.POST.get("project_archive_pair", None))

		p = Project.objects.filter(userproject__userid = user_id, userproject__archive = True).values_list('projectid', flat=True)

		list_catid = []
		for i in proj_archive_dict.keys():
			print(i, proj_archive_dict[i])
			if proj_archive_dict[i]:
				if int(i) not in p:
					list_catid.append(int(i))
			else:
				if int(i) in p:
					list_catid.append(int(i))

		print(list_catid)
		data = {}
		
		if list_catid: 
			try:
				UserProject.objects.filter(projectid__in = list_catid).update(archive = Case(
					When(archive = True, then = Value(False)),
					When(archive = False, then = Value(True)),
					When(archive__isnull = True, then = Value(True))
					)
				)

				data['success'] = True
			except Exception as e:
				print(e.args)
				data['success'] = False
		else:
			data['success'] = True
		
		return JsonResponse(data)

@login_required(login_url="/login/")
def user_details_update(request):
    #this view processes all of the requests to edit the individual user view
    #params: will always be an ajax post request because the user is editting existing database data
    #return: confirmation if the data has been saved in the database. This will send back a json response
    
    if request.method == "POST" and request.is_ajax():
        user_id = request.POST.get("user_id", None)

        new_email = request.POST.get("new_email", None)
        new_phone = request.POST.get("new_phone", None)
        new_org = request.POST.get("new_org", None)
        new_req_dates = request.POST.get("list_of_req", None)
        assoc_proj_id = request.POST.get("assoc_proj_id", None)

        #this will tell is if the passed in json data has been successfully saved into the database
        email_success = True
        phone_success = True
        org_success = True

        if new_email is not None:
            try:
                u = VSUser.objects.get(userid = user_id)
                u.useremail = new_email
                u.save()
            except Exception as e:
                email_success = False
                print(e.args)

        if new_phone is not None:
            try:
                u = VSUser.objects.get(userid = user_id)
                #check if blank string, then you have to set it to None in order for sql server to have store it as NULL
                if new_phone == "":
                        new_phone = None
                u.phone = new_phone
                u.save()
            except Exception as e:
                phone_success = False
                print(e.args)

        if new_org is not None:
            try:
                #check if the user already has a record in this table that corresponds to the organization
                q2 = UserOrganization.objects.filter(orgid__in = Organization.objects.filter(orgname = new_org), userid = user_id)

                if q2.count() == 1:
                    #if there is one matching user organization relationship that already exists, then you change that one back to active

                    #archive the old userorg
                    UserOrganization.objects.filter(userid = user_id).update(archive = True)
                    q2.update(archive = False)
                elif q2.count() > 1:
                    #tell the end user there is something wrong with the data storage, there should never be more than one user organization relationship where ...
                    #the userid and orgid is the same
                    raise Exception
                else:
                    #if there is no existing relationship for the userid and orgid, then we create a new record
                    UserOrganization.objects.filter(userid = user_id).update(archive = True)
                    try:
                        org_obj = Organization.objects.get(orgname = new_org)
                        user_obj = VSUser.objects.get(userid = user_id)
                        uo = UserOrganization(userid = user_obj, orgid = org_obj)
                        uo.save()
                    except Exception as e:
                        print(e.args)
                    
            except Exception as e:
                print(e.args)
                org_success = False

        if assoc_proj_id is not None:
            try:
                #ideally we should use get but just in case there are multiple instances
                user_proj_obj = UserProject.objects.filter(projectid = assoc_proj_id, userid = user_id).update(archive = Case(
                    When(archive = True, then = Value(False)),
                    When(archive = False, then = Value(True)),
                    When(archive__isnull = True, then = Value(True))))
            except Exception as e:
                print(e.args)

        data = {"email_success": email_success,
            "phone_success": phone_success,
            "org_success": org_success,
        }
        
        return JsonResponse(data)
    else:
        raise Http404

@login_required(login_url='/login/')
def new_user_form(request):
    #the new project page loads through an ajax call to fill in the modal
    #params: an ajax post request to submit data/ an ajax get request to get a new form (when modal is clicked)
    #return: confirmation if the data was saved properly in the database
    
    if request.is_ajax():
        errors = None
        if request.method == 'POST':
                form = UserForm(request.POST)
                if form.is_valid():
                        form = UserForm()
                else:
                        errors = form.errors
        else:
                form = UserForm()

        context = {
                'form': form,
        }
        data = {
                'html_page': render_to_string('ProjectSurveillance/newmodal.html', context, request=request)
        }                  
        return JsonResponse(data)
    else:
        raise Http404

@login_required(login_url='/login/')
def new_proj_form(request):
    #the new project page loads through an ajax call to fill in the modal
    #params: an ajax post request for submitting new info/ an ajax get request to get a new form (when modal is clicked)
    #return: confirmation if the data was successfully saved into the database
    
    if request.is_ajax():
        errors = None
        if request.method == 'POST':
            form = ProjectForm(request.POST)
            if form.is_valid():
                #commit = false if you want to save something else before putting in database
                #project = form.save(commit=True)

                #p = Project(projname=form.cleaned_data["project_name"], intext=form.clean_data["intext"])
                #p.save()
                #entered_proj = Project.objects.latest('projectid')
                form = ProjectForm()
            else:
                errors = form.errors          
        else:
            form = ProjectForm()

        context = {
            'form': form,
        }
        data = {
            'html_page': render_to_string('ProjectSurveillance/newmodal.html', context, request=request)
        }                   
        return JsonResponse(data)
    else:
        raise Http404

@login_required(login_url='/login/')
def new_org_form(request):
    #the new project page loads through an ajax call to fill in the modal
    #params: must be an ajax post request to submit new data/ an ajax get request to get a new form (when modal is clicked)
    #return: confirmation of whether or not the data was successfully entered
    
    if request.is_ajax():
        errors = None
        if request.method == 'POST':
            form = OrgForm(request.POST)
            if form.is_valid():
                form = OrgForm()
            else:
                errors = form.errors
        else:
            form = OrgForm()

        context = {
            'form': form,
        }
        data = {
            'html_page': render_to_string('ProjectSurveillance/newmodal.html', context, request=request)
        }                  
        return JsonResponse(data)
    else:
        raise Http404

def reports(request):
    #WIP
    
    if request.method == "GET":
        context =  {}
        return render(request, "ProjectSurveillance/report.html", context)

def signup(request):
    #This function is used to create another user
    #param: a standard post request
    #return: either redirects back to the dashboard if user was successfully created or it renders the same form they sent as a request
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.clean_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request,user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'ProjectSurveillance/signup.html', {'form': form})

def validate_username(request):
    #This function is called the signup html and checks if the username already exists:
    #param: GET request, AJAX?
    #return: json response
    
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)

