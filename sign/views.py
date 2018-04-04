#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from sign.models import Event, Guest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


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
    guest_list = Guest.objects.all()
    username = request.session.get('user', '')
    paginator = Paginator(guest_list, 2)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)

    return render(request, "guest_manage.html", {'user': username,
                                                 'guests': contacts})
# 签到页面
@login_required
def sign_index(request, eid):
    event = get_object_or_404(Event, id=eid)
    return render(request, 'sign_index.html', {'event': event})

# 签到动作
@login_required
def sign_index_action(request, eid):
    event = get_object_or_404(Event, id=eid)
    phone = request.POST.get('phone', '')
    print phone
    result = Guest.objects.filter(phone=phone)
    if not result:
        return render(request, 'sign_index.html', {'event': event,
                                                   'hint': '手机号错误或者不存在'})
    result = Guest.objects.filter(phone=phone, event_id= eid)
    if not result:
        return render(request, 'sign_index.html', {'event': event,
                                                   'hint': '您没有预约该会议'})
    result = Guest.objects.get(phone=phone, event_id=eid)
    if result.sign:
        return render(request, 'sign_index.html', {'event': event,
                                                   'hint': '您已经签到过'})
    else:
        Guest.objects.filter(phone=phone, event_id=eid).update(sign='1')
        return render(request, 'sign_index.html', {'event': event,
                                                   'hint': '签到成功',
                                                   'guest': result
                                                   })
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
    Guest_list = Guest.objects.filter(phone__contains=search_phone)
    if Guest_list.count() == 0:
        return HttpResponse('没有查询到结果')
    else:
        return render(request, 'search_phone.html', {
            'user': username,
            'guests': Guest_list
        })
