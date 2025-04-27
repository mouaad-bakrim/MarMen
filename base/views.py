from django.shortcuts import render

# Create your views here.
def dashbord(request):
    return render(request, 'dashboard.html')

from django.http import HttpResponse
from collections import defaultdict

def pdf_response(draw_funk, file_name, *args, **kwargs):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "filename=\"%s\"" % file_name
    draw_funk(response, *args, **kwargs)
    return response

