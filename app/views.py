from django.http import HttpResponse
from django.shortcuts import render


def home(request):
    style = 'font-family:sans-serif'
    return HttpResponse('<h1 style={}>Under construction</h1>'.format(style))
