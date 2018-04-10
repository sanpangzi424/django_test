#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from sign.models import Event,Guest
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.utils import IntegrityError
import datetime

# 添加发布会
def add_event(request):
    eid = request.POST.get('eid','')  # 发布会id
    name = request.POST.get('name', '')  # 发布会标题
    limit = request.POST.get('limit', '')  # 限制人数
    status = request.POST.get('status', '')  # 状态
    address = request.POST.get('address', '')  # 地址
    start_time = request.POST.get('start_time', '')  # 发布会时间


    if eid == '' or name == '' or limit == '' or status == '' or address == '' or start_time == '':

        return JsonResponse({'status':10021, 'message': u'参数错误'})
    result = Event.objects.filter(id=eid)
    if result:
        return JsonResponse({'status':10022, 'message': u'发布会id已存在'})
    result = Event.objects.filter(name=name)
    if result:
        return JsonResponse({'status':10023, 'message': u'发布会名称已存在'})
    if status == '':
        status = 1

    try:
        Event.objects.create(id=eid, name=name, limit=limit, status=int(status), address=address, start_time=start_time)

    except ValidationError:
        error = u'开始时间必须是YYYY-MM-DD HH:MM:SS格式'
        return JsonResponse({'status':10024, 'message': error})
    return JsonResponse({'status':200, 'message': u'添加成功'})

# 添加嘉宾

def add_guest(request):
    realname = request.POST.get('realname', '')
    phone = request.POST.get('phone','')
    email = request.POST.get('email', '')
    eid = request.POST.get('eid', '')
    # eid realname phone 为空提示参数错误
    if realname == '' or phone == '' or eid == '':
        return JsonResponse({'status': 10021, 'message': '参数错误'})

    # eid不存在 返回会议不存在

    result = Event.objects.filter(id=eid)
    if not result:
        return JsonResponse({'status': 10022, 'message': '会议不存在'})

    # 判断event的status 返回会议是否关闭状态

    result = Event.objects.get(id=eid).status
    if not result:
        return JsonResponse({'status': 10023, 'message': '会议已结束'})

    # 获取会议的limit人数和已经报名该会议的人数，对比返回会议是否已经满员

    event_limit = Event.objects.get(id=eid).limit
    guest_limit = Guest.objects.filter(event_id=eid)
    if len(guest_limit) >= event_limit:
        return JsonResponse({'status': 10024, 'message': '会议已满员'})

    # 判断会议时间是否晚于当前时间

    event_time = str(Event.objects.get(id=eid).start_time)
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if current_time > event_time:
        return JsonResponse({'status': 10025, 'message': '会议已结束'})

    # try 写入数据，如果失败，返回电话重复

    try:
        Guest.objects.create(realname=realname, phone=int(phone), email=email, sign=0, event_id=int(eid))
    except IntegrityError:
        return JsonResponse({'status': 10026, 'message': '嘉宾电话重复'})

    return JsonResponse({'status': 200, 'message': '添加成功'})





# 发布会查询
def get_event_list(request):

    eid = request.GET.get("eid", "")      # 发布会id
    name = request.GET.get("name", "")    # 发布会名称

    if eid == '' and name == '':
        return JsonResponse({'status':10021,'message':u'参数错误'})

    if eid != '':
        event = {}
        try:
            result = Event.objects.get(id=eid)
        except ObjectDoesNotExist:
            return JsonResponse({'status':10022, 'message':'发布会不存在'})
        else:
            event['eid'] = result.id
            event['name'] = result.name
            event['limit'] = result.limit
            event['status'] = result.status
            event['address'] = result.address
            event['start_time'] = result.start_time
            return JsonResponse({'status':200, 'message':'success', 'data':event})

    if name != '':
        datas = []
        results = Event.objects.filter(name__contains=name)
        if results:
            for r in results:
                event = {}
                event['eid'] = r.id
                event['name'] = r.name
                event['limit'] = r.limit
                event['status'] = r.status
                event['address'] = r.address
                event['start_time'] = r.start_time
                datas.append(event)
            return JsonResponse({'status':200, 'message':'success', 'data':datas})
        else:
            return JsonResponse({'status':10022, 'message':'没有查询到结果'})

# 嘉宾查询

# eid为空，返回eid不能为空。 eid不为空且电话为空，返回会议的参与嘉宾（遍历赋值）。eid、电话都不为空返回嘉宾信息

def get_guest_list(request):
    eid = request.GET.get('eid', '')
    phone = request.GET.get('phone', '')

    if eid == '':
        return JsonResponse({'status':10021, 'message':'会议id不能为空'})
    if eid != '' and phone == '':
        datas = []
        results = Guest.objects.filter(event_id=eid)
        if results:
            for r in results:
                guest = {}
                guest['realname'] = r.realname
                guest['phone'] = r.phone
                guest['email'] = r.email
                guest['sign'] = r.sign
                datas.append(guest)
            return JsonResponse({'status':200,'message':'success', 'data':datas})
        else:
            return JsonResponse({'status': 10022, 'message': '没有查询到结果'})

    if eid != '' and phone != '':
        guest = {}
        try:
            result = Guest.objects.get(event_id=eid, phone=phone)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 10022, 'message': '没有查询到结果'})

        else:
            guest['realname'] = result.realname
            guest['phone'] = result.phone
            guest['email'] = result.email
            guest['sign'] = result.sign
            return JsonResponse({'status': 10022, 'message': 'success', 'data':guest})

# 嘉宾签到

# 传入参数eid，phone。 1、eid、phone都为空，返回不能为空。2、根据eid搜索会议，如果没有结果，返回会议不存在。3、查询会议的status，
# 如果不为true，返回会议已结束。4、判断当前时间是否大于会议时间，返回会议已结束。5、判断手机号是否存在。6、根据eid和phone判断用户是否预约了该场会议
# 7、判断是否签到。8、签到成功


def user_sign(request):
    eid = request.POST.get('eid', '')
    phone = request.POST.get('phone', '')

    if eid == '' or phone == '':
        return JsonResponse({'status': 10021, 'message':'参数错误'})
    result = Event.objects.filter(id=eid)
    if not result:
        return JsonResponse({'status': 10022, 'message':'会议不存在'})

    result = Event.objects.get(id=eid).status
    if not result:
        return JsonResponse({'status': 10023, 'message':'会议已结束'})

    event_time = str(Event.objects.get(id=eid).start_time)
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if current_time > event_time:
        return JsonResponse({'status': 10024, 'message': '会议已开始'})

    result = Guest.objects.filter(phone=phone)
    if not result:
        return JsonResponse({'status': 10025, 'message':'手机号不存在'})

    result = Guest.objects.filter(phone=phone, event_id=eid)
    if not result:
        return JsonResponse({'status': 10026, 'message': '嘉宾没有预约该场会议'})

    result = Guest.objects.get(phone=phone, event_id=eid).sign
    if result:
        return JsonResponse({'status': 10027, 'message': '用户已签到'})

    else:
        Guest.objects.filter(phone=phone).update(sign=1)
        return JsonResponse({'status': 200, 'message': '签到成功！'})










