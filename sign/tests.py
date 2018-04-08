#!/usr/bin/env python
# -*- coding: utf-8 -*-


from django.test import TestCase
from sign.models import Event, Guest
from django.contrib.auth.models import User


class ModelTest(TestCase):
    def setUp(self):
        Event.objects.create(id=1, name="oneplus 3 event", status=True, limit=2000, address='shenzhen',
                             start_time='2016-08-31 02:18:22')
        Guest.objects.create(id=1, event_id=1, realname='alen', phone='13711001101', email='alen@mail.com', sign=False)

    def test_event_models(self):
        '''测试发布会表'''
        result = Event.objects.get(name="oneplus 3 event")
        self.assertEqual(result.address, "shenzhen")
        self.assertTrue(result.status)

    def test_guest_models(self):
        '''测试嘉宾表'''
        result = Guest.objects.get(phone='13711001101')
        self.assertEqual(result.realname, "alen")
        self.assertFalse(result.sign)


class IndexPageTest(TestCase):
    ''' 测试index登录首页'''

    def test_index_page_renders_index_template(self):
        '''测试index视图'''
        response = self.client.get('/index/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')


class LoginActionTest(TestCase):
    '''测试登录动作'''
    def setUp(self):
        User.objects.create_user('admin', 'admin@mail.com', 'admin123456')

    def test_add_admin(self):
        user = User.objects.get(username='admin')
        self.assertEqual(user.username, 'admin')
        self.assertEqual(user.email, 'admin@mail.com')

    def test_login_action_username_password_null(self):
        '''用户名密码为空'''
        test_data = {'username':'', 'password': ''}
        response = self.client.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code,200)
        self.assertIn(u'账号密码错误', response.content)

    def test_login_action_username_password_error(self):
        '''用户名密码错误'''
        test_data = {'username':'abc', 'password': '123333'}
        response = self.client.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code,200)
        self.assertIn(u'账号密码错误', response.content)


    def test_login_action_success(self):
        '''登录成功'''
        test_data = {'username':'admin', 'password': 'admin123456'}
        response = self.client.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code,302)


class EventManageTest(TestCase):
    '''发布会管理'''
    def setUp(self):
        User.objects.create_user('admin', 'admin@mail.com', 'admin123456')
        Event.objects.create(name='xiaomi5', limit=2000, address='beijing', status=1, start_time='2018-02-03 00:00:00')
        self.login_user = {'username':'admin', 'password':'admin123456'}
        self.client.post('/login_action/', data=self.login_user) #先执行登录

    def test_event_manage_success(self):
        '''测试发布会xiaomi5'''
        response = self.client.post('/event_manage/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('beijing', response.content)
        self.assertIn('xiaomi5', response.content)

    def test_event_manage_search(self):
        '''测试发布会搜索'''
        response = self.client.post('/search_name/', {'name': 'xiaomi5'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('xiaomi5', response.content)
        self.assertIn('beijing', response.content)

class GuestManageTest(TestCase):
    '''嘉宾管理'''
    def setUp(self):
        User.objects.create_user('admin', 'admin@mail.com', 'admin123456')
        Event.objects.create(id=1, name='xiaomi5', limit=2000, address='beijing', status=1, start_time='2018-02-05 00:00:00')
        Guest.objects.create(realname="alen", phone=18611001100, email='alen@mail.com', sign=0, event_id=1)
        self.login_user = {'username':'admin', 'password':'admin123456'}
        self.client.post('/login_action/', data=self.login_user)

    def test_event_manage_success(self):
        '''测试嘉宾信息alen'''
        response = self.client.post('/guest_manage/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('alen', response.content)
        self.assertIn('18611001100', response.content)

    def test_event_manage_search(self):
        '''测试嘉宾搜索'''
        response = self.client.post('/search_phone/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('alen', response.content)
        self.assertIn('18611001100', response.content)

class SignIndexAction(TestCase):
    '''发布会签到'''
    def setUp(self):
        User.objects.create_user('admin', 'admin@mail.com', 'admin123456')
        Event.objects.create(id=1, name="xiaomi5", limit=2000, address='beijing', status=1,
                             start_time='2017-8-10 12:30:00')
        Event.objects.create(id=2, name="oneplus4", limit=2000, address='shenzhen', status=1,
                             start_time='2017-6-10 12:30:00')
        Guest.objects.create(realname="alen", phone=18611001100, email='alen@mail.com', sign=0, event_id=1)
        Guest.objects.create(realname="una", phone=18611001101, email='una@mail.com', sign=1, event_id=2)
        login_user = {'username': 'admin', 'password': 'admin123456'}
        self.client.post('/login_action/', data=login_user)

    # def test_sign_phone_null(self):
    #     '''手机号为空'''
    #     response = self.client.post('/sign_index_action/1', {'phone': ''})
    #     print response
    #     # self.assertEqual(response.status_code, 301)
    #     #
    #     # self.assertIn(u'手机号错误或者不存在', response.content)

    def test_sign_index_action_phone_or_event_id_error(self):
        ''' 手机号或发布会id错误 '''
        response = self.client.post('/sign_index_action/2/', {"phone": "18611001100"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(u"您没有预约该会议", response.content)

    def test_sign_index_action_user_sign_has(self):
        ''' 用户已签到 '''
        response = self.client.post('/sign_index_action/2/', {"phone": "18611001101"})
        self.assertEqual(response.status_code, 200)
        print response.content
        self.assertIn(u"您已经签到过", response.content)

    def test_sign_index_action_sign_success(self):
        ''' 签到成功 '''
        response = self.client.post('/sign_index_action/1/', {"phone": "18611001100"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(u"签到成功", response.content)






















