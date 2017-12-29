from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import NewAnalysisForm
from .models import *

from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.resources import CDN

#@login_required(login_url='/login/')
def new_analysis_proj(request):
        if request.method == 'POST':
                form = NewAnalysisForm(request.POST)
                if form.is_valid():
                        form.save()
        else:
                form = NewAnalysisForm()
        return render(request, 'Analysis/newanalysis.html', {'form':form})

def analysis_proj_view(request):
        analysisproj = DatapullId.objects.all()
        
        return render(request, 'Analysis/allanalysisproj.html', {'analysisproj':analysisproj})

def indiv_analysis_proj_view(request,pk):
        ana_project = DatapullId.objects.get(pk=pk)

        num_of_articles = DatapullDetail.objects.filter(pullid = pk).count()

        return render(request, 'Analysis/indivanalysisproj.html', {'ana_project':ana_project, 'numarticles':num_of_articles})

def visual(request):

        x = [1,3,5,7,9,11,13]
        y = [1,2,3,4,5,6,7]

        title = 'y = f(x)'

        plot = figure(title= title,
                      x_axis_label = 'X-axis',
                      y_axis_label = 'Y-axis',
                      plot_width = 400,
                      plot_height = 400)

        plot.line(x, y, legend = 'f(x)', line_width = 2)

        script, div = components(plot, CDN)
        
        return render(request, 'Analysis/visuals.html', {'script':script, 'div':div})

