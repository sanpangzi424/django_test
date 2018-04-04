#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from sign.models import Event, Guset


# Create your views here.

def index(request):
    return render(request, "index.html")


def login_action(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            request.session['user'] = username
            response = HttpResponseRedirect('/event_manage')
            return response
        else:
            return render(request, 'index.html', {'error': u'账号密码错误'})


@login_required
def event_manage(request):
    event_list = Event.objects.all()
    username = request.session.get('user', '')
    return render(request, "event_manage.html", {'user': username,
                                                 'events': event_list})


@login_required
def guest_manage(request):
    guest_list = Guset.objects.all()
    username = request.session.get('user', '')
    return render(request, "guest_manage.html", {'user': username,
                                                 'guests': guest_list})


def search_name(request):
    username = request.session.get('user', '')
    search_name = request.GET.get('name', '')
    event_list = Event.objects.filter(name__contains=search_name)
    return render(request, 'search_name.html', {
        'user': username,
        'events': event_list
    })


def search_phone(request):
    username = request.session.get('user', '')
    search_phone = request.GET.get('phone', '')
    Guest_list = Guset.objects.filter(phone__contains=search_phone)
    if Guest_list.count() == 0:
        return HttpResponse('没有查询到结果')
    else:
        return render(request, 'search_phone.html', {
            'user': username,
            'guests': Guest_list
        })

