from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, F, Value, Case, When
from django.core.exceptions import ObjectDoesNotExist
from datetime import timedelta, datetime

from .models import *

def proj_type_helper(projtype):
    #helper function to that is used by all_projects function and all_projects_ajax
    #params: a string indicating the type of project (Internal, External, Collab)
    #return: a queryset of projects
    project_list = None
    
    if projtype == "Internal" or projtype == "External":
        project_list = Project.objects.filter(userproject__userid__in =
                                        VSUser.objects.filter(userorganization__orgid__in = 
                                            Organization.objects.filter(orgtypeid__in = 
                                                OrganizationType.objects.filter(typename__icontains = projtype)))).distinct()

    elif projtype == "Collaboration":   #collab
            project_list = Project.objects.filter(userproject__userid__in =
                                                VSUser.objects.filter(userorganization__orgid__in =
                                                    Organization.objects.filter(orgtypeid__in =
                                                        OrganizationType.objects.filter(typename__icontains = "Internal")))).filter(
                                                            userproject__userid__in =
                                                                VSUser.objects.filter(userorganization__orgid__in =
                                                                    Organization.objects.filter(orgtypeid__in =
                                                                        OrganizationType.objects.filter(typename__icontains = "External"))))
    else:
        project_list = Project.objects.all().order_by("projname")
            
    return project_list

def all_projects_ajax(request):
    #This function is used to update the list of all projects, either when a sorting/pagination/search/filter button is pressed.
    #param: must be a GET request and an ajax call
    #returns: json response of rendered html we are going to change (the table of all projects and the pagination bar)
    
    if request.is_ajax() and request.method == 'GET':
        query = request.GET.get('query', None)
        query_type = request.GET.get('query_type', None)
        sorttype = request.GET.get('sorttype', None)
        print(query_type)
        print(query)
        print(sorttype)

        #check if user made an ajax call to sort the current page of projects
        #else instead of elif "asc" because there might be times when user didn't specific sort type
        sortstring = "-" if sorttype == "dsc" else ""
        
        if query_type == "search":
            if query == "":
                project_list = Project.objects.all().order_by(sortstring + "projname")
            else:
                project_list = Project.objects.filter(
                    Q(projectid__icontains=query) | Q(projname__icontains=query)
                    ).order_by(sortstring + "projname")
                        
        elif query_type == "org":
            #get orgid of the search_query
            if query == "":
                project_list = Project.objects.all().order_by(sortstring + "projname")
            else:
                org_object = get_object_or_404(Organization, orgname = query)
                org_id = org_object.orgid

                users_with_organization = VSUser.objects.filter(userorganization__orgid = org_id)

                project_list = Project.objects.none()
                for u in users_with_organization:
                    proj_objects = Organization.objects.filter(userorganization__userid = u.userid).exclude(userorganization__archive = True)
                    project_list = project_list | proj_objects

                project_list = project_list.order_by(sortstring + "projname").distinct()

        elif query_type == "type":
            project_list = proj_type_helper(query)
                    
            project_list = project_list.order_by(sortstring + "projname")
                
        elif query_type == "open":
            if query == "Open":
                project_list = Project.objects.filter(Q(archive__isnull = True)|Q(archive = False)).order_by(sortstring + "projname")
            elif query == "Close":
                project_list = Project.objects.filter(archive = True).order_by(sortstring + "projname")
            else:
                project_list = Project.objects.all().order_by(sortstring + "projname")
        else:
            project_list = Project.objects.all().order_by(sortstring + "projname")

        print(project_list.count())

        page = request.GET.get('desired_page',1)                  
        paginator = Paginator(project_list, 50)

        try:
            projects = paginator.page(page)
        except PageNotAnInteger:
            projects = paginator.page(1)
        except EmptyPage:
            projects = paginator.page(paginator.num_pages)

        #subtract 1 because we will be taking a slice, starting at index 0
        #index indicates current page that we are on minus 1
        index = projects.number - 1
        #max index indicates total number of pages
        max_index = len(paginator.page_range)

        if index >= 3:
            if index >= max_index - 2:
                #if there are less than 5 indexes in total
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
        context = {'projects' : projects, 'page_range': page_range}
        data['html_page'] = render_to_string('ProjectSurveillance/paginationajax.html', context, request=request)
        data['html_table'] = render_to_string('ProjectSurveillance/projectviewajax.html', context, request=request)
        return JsonResponse(data)

    else:
        response.status_code = 404
        return response


def filter_change(request):
    #This changes the filter options
    #param: must be an ajax call and a get request (from all projects view or the individual user view)
    #returns: rendered html serialized to a json response of the new options for the filter section
    
    if request.is_ajax():
        option = request.GET.get('option', None)

        orglist = None
        return_list = None

        if option == "org":
            return_list = list(Organization.objects.all().order_by("orgname").distinct().values_list("orgname",flat=True))
        elif option == 'type':
            return_list = ["Internal", "External", "Collaboration"]
        elif option == 'open':
            return_list = ["Open", "Close", "Not Specified"]
        else:
            return_list = list(Organization.objects.all().order_by('orgname').distinct().values_list('orgname',flat=True))

        context = {
            'returnlist' : return_list
        }
        return JsonResponse(context)
    else:
        raise Http404

def all_projects(request):
    #Serves all of the projects, a pagination bar, a filter option, and a search option
    #params: get request only
    #return: rendered html page with all of the projects
    
    if request.method == 'GET':

        #each if statement tells you which filter button the user pressed
        #else indicates that it was the initial page load when user pressed projects tab

        if 'searchbox' in request.GET:
            search_query = request.GET.get('searchbox', None)
            if search_query is None:
                project_list = Project.objects.all().order_by("projname")
            else:
                project_list = Project.objects.filter(
                    Q(projectid__icontains=search_query) | Q(projname__icontains=search_query)
                    ).order_by("projname")

            optionlist = Organization.objects.all().order_by('orgname').distinct().values_list('orgname',flat=True) #if this changes, you need to change filter_change function also
            filtername = "Organization"
            filtertype = "org"
            chosen = ""
        
        elif 'org' in request.GET:
            search_query = request.GET.get('org', None)
            chosen = search_query
                          
            #get orgid of the search_query
            if search_query == "":
                project_list = Project.objects.all().order_by("projname")
            else:
                org_object = get_object_or_404(Organization, orgname = search_query)
                org_id = org_object.orgid

                users_with_organization = VSUser.objects.filter(userorganization__orgid = org_id)

                project_list = Project.objects.none()
                for u in users_with_organization:
                        proj_objects = Project.objects.filter(userproject__userid = u.userid)
                        project_list = project_list | proj_objects

                project_list = project_list.distinct().order_by("projname")

            optionlist = Organization.objects.all().order_by('orgname').distinct().values_list('orgname',flat=True) #if this changes, you need to change filter_change function also
            filtername = "Organization"
            filtertype = "org"

        elif 'type' in request.GET:
            search_query = request.GET.get("type", None)
            chosen = search_query

            project_list = proj_type_helper(search_query)
                                                          
            optionlist = ["Internal", "External", "Collaboration"] #if this changes, you need to change filter_change function also
            filtername = "Project Type"
            filtertype = "type"
                
        elif 'open' in request.GET:
            search_query = request.GET.get('open', None)
            chosen = search_query

            if search_query == "Open":
                    project_list = Project.objects.filter(Q(archive__isnull = True)|Q(archive = False)).order_by("projname")
            elif search_query == "Close":
                    project_list = Project.objects.filter(archive = True).order_by("projname")
            else:
                    project_list = Project.objects.all().order_by("projname")

            optionlist = ['Open','Close','Not Specified'] #if this changes, you need to change filter_change function also
            filtername = "Open/Close"
            filtertype = "open"
                        
        else:
            project_list = Project.objects.all().order_by("projname")
            optionlist = Organization.objects.all().order_by('orgname').distinct().values_list('orgname',flat=True) #if this changes, you need to change filter_change function also
            filtername = "Organization"
            filtertype = "org"
            chosen = ""
                
        #initial pagination stuff, from here on out, when pagination is called, all_projects_ajax function handles different page loads                                
        paginator = Paginator(project_list, 50)

        try:
            projects = paginator.page(1)
        except PageNotAnInteger:
            projects = paginator.page(1)
        except EmptyPage:
            projects = paginator.page(paginator.num_pages)

        start_index = projects.number - 1
        end_index = len(paginator.page_range)

        if end_index >= 5:
            end_index = 5

        page_range = paginator.page_range[start_index:end_index]

        #need to pass: filtername: the literal label for the filtering button (default should be organization when we first visit project tab)
        #filtertype: data-id and name (used for pagination ajax calls)
        #optionlist: the list of options that will be displayed in the dropdown
        #chosen: will be used to prepopulate the last option chosen in the dropdown
        return render(request, 'ProjectSurveillance/projectview.html', {'projects' : projects, 'page_range': page_range, 'optionlist': optionlist,
                                                                        'filtername': filtername, 'filtertype': filtertype, 'chosen': chosen})


def project_details(request, pk):
    #gets the individual details of a specific project
    #params: the primary key of the project and a get request
    #return: rendered page of each individual project's details
    
    project = get_object_or_404(Project, pk=pk)

    phases = WorkPhase.objects.all()

    #spans down to projectdatasetrequest and get those that have projectid = pk (returns all datasets requested by project)
    datasets_with_project = Dataset.objects.filter(projectdatasetrequest__projectid = pk)

    #spans down to usersprojects, keeping only those that have projectid = pk
    users_with_project = VSUser.objects.filter(userproject__projectid = pk)

    #spans down to userorganization to get which organization the project is part of
    orgs_with_proj = Organization.objects.none()
    for u in users_with_project:
        org_objects = Organization.objects.filter(Q(userorganization__archive__isnull = True) | Q(userorganization__archive = False), userorganization__userid = u.userid)
        orgs_with_proj = orgs_with_proj | org_objects

    orgs_with_proj = orgs_with_proj.distinct()

    #now we use the organizations and check what are the different types of organizations they are. For example: if there is an internal and external organization, that means it is a collab
    org_types = OrganizationType.objects.filter(orgtypeid__in = orgs_with_proj.values_list('orgtypeid', flat=True)).values_list('typename', flat=True)
            
    #get project descrip
    try:
        descrip = ProjectDetail.objects.get(projectid = pk, detailtypeid = 2)
    except ObjectDoesNotExist:
        descrip = None

    #project start date
    try:
        startdate = ProjectDetail.objects.get(projectid = pk, detailtypeid = 7)
    except ObjectDoesNotExist:
        startdate = None
    
    return render(request, 'ProjectSurveillance/indivprojview.html', {'project' : project,
                                                                      'orgtypes' : org_types,
                                                                      'datasets' : datasets_with_project,
                                                                      'orgs' : orgs_with_proj,
                                                                      'descrip' : descrip,
                                                                      'start' : startdate,
                                                                      'phases' : phases
                                                                      })

def project_details_ajax(request):
    #updates the pane to show the correct section of project
    #params: a request update, the tab chosen via ajax call
    #return: rendered html

    if request.is_ajax() and request.method == 'GET':
        proj_id = request.GET.get("proj_id", None)
        tab = request.GET.get("type", None)

        data = {}
        context = {}
        project = get_object_or_404(Project, pk=proj_id)

        if tab == "desc":
            #spans down to userorganization to get which organization the project is part of
            orgs_with_proj = Organization.objects.none()

            #spans down to usersprojects, keeping only those that have projectid = pk
            users_with_project = VSUser.objects.filter(userproject__projectid = proj_id)
            for u in users_with_project:
                org_objects = Organization.objects.filter(Q(userorganization__archive__isnull = True) | Q(userorganization__archive = False), userorganization__userid = u.userid)
                orgs_with_proj = orgs_with_proj | org_objects

            orgs_with_proj = orgs_with_proj.distinct()

            #now we use the organizations and check what are the different types of organizations they are. For example: if there is an internal and external organization, that means it is a collab
            org_types = OrganizationType.objects.filter(orgtypeid__in = orgs_with_proj.values_list('orgtypeid', flat=True)).values_list('typename', flat=True)
        
            #get project aims
            try:
                descrip = ProjectDetail.objects.get(projectid = proj_id, detailtypeid = 2)
            except ObjectDoesNotExist:
                descrip = None

            #project start date
            try:
                startdate = ProjectDetail.objects.get(projectid = proj_id, detailtypeid = 7)
            except ObjectDoesNotExist:
                startdate = None

            context = {
                'project': project, 'orgtypes' : org_types, 'orgs' : orgs_with_proj, 'descrip' : descrip, 'start' : startdate,
            }
            data['html'] = render_to_string('ProjectSurveillance/indivprojview-description.html', context, request=request)

        elif tab == "users":
            #spans down to usersprojects, keeping only those that have projectid = pk
            users_with_project = VSUser.objects.filter(userproject__projectid = proj_id)

            context = {
                'userprojs' : users_with_project,
            }
            data['html'] = render_to_string('ProjectSurveillance/indivprojview-users.html', context, request=request)

        elif tab == "activity":
            #project activities
            proj_activity = ProjectActivity.objects.filter(projectid = proj_id).order_by('-datelogged')

            context = {
                'proj_activity': proj_activity
            }
            data['html'] = render_to_string('ProjectSurveillance/indivprojview-activity.html', context, request=request)

        elif tab == "requests":

            context = {

            }
            data['html'] = render_to_string('ProjectSurveillance/indivprojview-requests.html', context, request=request)
        else:
            #documents
            components = Component.objects.filter(projectid = proj_id)

            context = {
                'components' : components
            }
            data['html'] = render_to_string('ProjectSurveillance/indivprojview-documents.html', context, request=request)

        data['tab'] = tab
        return JsonResponse(data)

@login_required(login_url='/login/')
def project_details_update(request):
    #Updates the individual project view (DESCRIPTION/ GENERAL HEADER)
    #param: request must be a POST and ajax request
    #returns: either a 404 if it is not a POST & ajax request OR a json response
    
    if request.method == "POST" and request.is_ajax():
        proj_id = request.POST.get("proj_id", None)
        alternate_id = request.POST.get("alternate_id", None)
        start_date = request.POST.get("start_date", None)
        end_date = request.POST.get("end_date", None)
        description = request.POST.get("new_des", None)
        variable_des = request.POST.get("new_var", None)
        archive_choice = request.POST.get("archive", None)

        #decide if the specific input (ajax edit for any field on the html page) is valid
        flag = 0
        start_success= True
        end_success = True
        description_success = True
        alternate_success = True

        #tries to parse different start date formats
        if start_date is not None:
            try:
                date_obj = datetime.strptime(start_date, "%B %d, %Y").date()
            except:
                try:
                    date_obj = datetime.strptime(start_date, "%m-%d-%Y").date()
                except:
                    try:
                        date_obj = datetime.strptime(start_date, "%B %d %Y").date()
                    except:
                        try:
                            date_obj = datetime.strptime(start_date, "%b. %d, %Y").date()
                        except:
                            try:
                                date_obj = datetime.strptime(start_date, "%b %d, %Y").date()
                            except:
                                try:
                                    date_obj = datetime.strptime(start_date, "%b %d %Y").date()
                                except:
                                    try:
                                        date_obj = datetime.strptime(start_date, "%b. %d %Y").date()
                                    except:
                                        flag = 1

            if flag == 0:
                try:
                    #if there is already a start date
                    p = ProjectDetail.objects.get(projectid = proj_id, detailtypeid = 7)
                    p.dateofevent = date_obj
                    p.save()
                except:
                    try:
                        #if there is no start date
                        p = ProjectDetail(projectid = proj_id, detailtypeid = 7, dateofevent = date_obj)
                        p.save()
                    except:
                        start_success = False
            else:
                start_success = False
                        
        #try to parse different end date formats
        if end_date is not None:
            try:
                end_date_obj = datetime.strptime(end_date, "%B %d, %Y").date()
            except:
                try:
                    end_date_obj = datetime.strptime(end_date, "%m-%d-%Y").date()
                except:
                    try:
                        end_date_obj = datetime.strptime(end_date, "%B %d %Y").date()
                    except:
                        try:
                            end_date_obj = datetime.strptime(end_date, "%b. %d, %Y").date()
                        except:
                            try:
                                end_date_obj = datetime.strptime(end_date, "%b %d, %Y").date()
                            except:
                                try:
                                    end_date_obj = datetime.strptime(end_date, "%b %d %Y").date()
                                except:
                                    try:
                                        end_date_obj = datetime.strptime(end_date, "%b. %d %Y").date()
                                    except:
                                        flag = 1

            if flag == 0:
                try:
                    #if there is already an end date
                    p = ProjectDetail.objects.get(projectid = proj_id, detailtypeid = 73)
                    p.dateofevent = end_date_obj
                    p.save()
                except:
                    try:
                        #if there is no end date
                        p = ProjectDetail(projectid = proj_id, detailtypeid = 73, dateofevent = end_date_obj)
                        p.save()
                    except:
                        end_success = False
            else:
                end_success = False

        #description
        if description is not None:
            #check if the description is too long, >4000 chars
            if len(description) > 4000:
                description_success = False
            else:
                try:
                    p = ProjectDetail.objects.get(projectid = proj_id, detailtypeid = 2)
                    p.note = description
                    p.save()
                except:
                    try:
                        #if there is no description in the database
                        p = ProjectDetail(projectid = proj_id, detailtypeid = 2, note = description)
                        p.save()
                    except:
                        description_success = False

        if alternate_id is not None:
            try:
                p = Project.objects.get(pk = proj_id)
                p.alternateid = alternate_id
                p.save()
            except:
                alternate_success = False

        archive_success = None
        if archive_choice:
            try:
                proj = Project.objects.get(projectid = proj_id)
                proj.archive ^= True
                proj.save()
                archive_success = True
            except:
                archive_success = False

        data = {"start_success": start_success,
                "end_success": end_success,
                "description_success": description_success,
                "archive_success": archive_success, 
                "alternate_success": alternate_success, }
        return JsonResponse(data)
    else:
        raise Http404


def project_details_update_activity(request):
    #Updates the individual project activity
    #param: request must be a POST and ajax request
    #returns: either a 404 if it is not a POST & ajax request OR a json response

    if request.method == "POST" and request.is_ajax():
        proj_id = request.POST.get("proj_id", None)
        act_id = request.POST.get("act_id", None)
        new_note = request.POST.get("new_note", None)
        new_date = request.POST.get("new_date", None)

        success = True
        data = {}

        if new_note is not None:
            try:
                p = ProjectActivity.objects.get(pk = act_id, projectid = proj_id)
                p.note = new_note
                p.save()
            except:
                success = False

        if new_date is not None:
            try:
                p = ProjectActivity.objects.get(pk = act_id, projectid = proj_id)
                p.datelogged = datetime.strptime(new_date, "%m/%d/%y").date()
                p.save()
            except:
                success = False

        data['success'] = success
        return JsonResponse(data)