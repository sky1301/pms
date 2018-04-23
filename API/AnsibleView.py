#-*-coding:utf-8-*-
import hashlib
import time
import logging
import ansible.runner
import datetime

import os
from django.core.cache import caches
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework import status

from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from ansibleAPI import settings
from Log import Log
logger = logging.getLogger('ansibleAPI')

class AnsibleViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    def __init__(self):
        self.token_cache = caches['token']
        self.record_cache = caches['default']
    @list_route(url_path='auth',methods=['post', 'get'])
    def auth(self,request):

        if request.method == 'POST':

            user_name = request.data['user_name']
            passwd = request.data['password']
            user = authenticate(username=user_name, password=passwd)#check the username and password
            if user is not None:
                time_stamp = str(int(time.time()))
                token = hashlib.md5(time_stamp).hexdigest() #generated the token
                try:
                    ctoken = self.token_cache.get(user_name) #get token from cache
                    if ctoken is None:
                        self.token_cache.set(user_name, token) #set token cache
                        self.token_cache.set(token, user_name)
                        cuser_name = self.token_cache.get(token) #get user_name from cache
                        content = {'user_name': cuser_name, 'Token': token, 'retcode': 200}
                        return Response(content,status=status.HTTP_200_OK)
                    else:
                        cuser_name = self.token_cache.get(ctoken)
                        content = {'user_name': cuser_name, 'Token': ctoken, 'retcode': 200}
                        return Response(content,status=status.HTTP_200_OK)
                except Exception, e:
                    logger.error(e.message)
                    content = {'msg': e.message, 'retcode': 500}
                    return Response(content,status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                logger.info('Invalid username or password.')
                content = {'msg': 'Invalid username or password.', 'retcode': 500}
                return Response(content,status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif request.method == 'GET':
            logger.info('Method GET not allowed.')
            content = {'msg': 'Method GET not allowed.', 'retcode': 500}
            return Response(content,status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @list_route(url_path='batch',methods=['post', 'get'])
    def batch(self,request):

        if request.method == 'POST':
            token = request.META['HTTP_TOKEN']
            user_name = self.token_cache.get(token) #get user_name from cache
            record_key = token+'batch'
            record = self.record_cache.get(record_key)
            if user_name is not None and record is None: #someone had called auth function but never call batch in one minute
                ip_list = request.data["ip_list"]
                cmd = request.data['command']
                ip_list = ','.join(ip_list) + ','
                if cmd.find(".sh") != -1 or cmd.find(".py") != -1:
                    runner = ansible.runner.Runner(module_name='script',remote_user='root', host_list=ip_list, timeout=10,pattern='all', module_args=os.path.join(settings.UPLOAD_ROOT+ '/' + cmd), forks=100)
                else:
                    runner = ansible.runner.Runner(module_name='shell', remote_user='root', host_list=ip_list,pattern='all', module_args=cmd,forks=100)
                result = runner.run()
                logger.info(result)
                log = Log()
                log.write_log(result, user_name)
                self.record_cache.set(record_key, 'batch')
                content = {'msg': result, 'retcode': 200}
                return Response(content,status=status.HTTP_200_OK)
            elif user_name is None:
                logger.info('your token had expired')
                content = {'msg': 'your token had expired', 'retcode': 500}
                return Response(content,status.HTTP_500_INTERNAL_SERVER_ERROR)
            elif record is not None:
                logger.info('Request asked only once per minute')
                content = {'msg': 'Request asked only once per minute,please try again after one minute.', 'retcode': 500}
                return Response(content,status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif request.method == 'GET':
            logger.info('Method GET not allowed.')
            content = {'msg': 'Method GET not allowed.', 'retcode': 500}
            return Response(content,status.HTTP_500_INTERNAL_SERVER_ERROR)

    @list_route(url_path='upload_script',methods=['post', 'get'])
    def upload(self,request):
        if request.method == 'POST':
            token = request.META['HTTP_TOKEN']
            user_name = self.token_cache.get(token)
            redord_key = token+'upload'
            record = self.record_cache.get(redord_key)
            if user_name is not None and record is None: #someone had called auth function but never call upload function in one minute
                f = request.FILES.get('file')
                now = datetime.datetime.now()
                file_dir = os.path.join(settings.UPLOAD_ROOT, user_name)
                bak_date = now.strftime("%Y-%m-%d_%H%M%S")
                try:
                    fname = f.name #get file name
                    if os.path.exists(os.path.join(file_dir, fname)):
                        file_name = fname.split('.')[0] + '_'
                        extension = '.' + fname.split('.')[1]
                        os.rename(os.path.join(file_dir, fname),
                                  os.path.join(file_dir, file_name + bak_date + extension))
                    default_storage.save(os.path.join(file_dir, fname),
                                         ContentFile(f.read()))  # save the file under the /path/to/project/static/upload/[user_name]
                    logger.info('upload success.')
                    self.record_cache.set(redord_key, 'upload')
                    content = {"retcode": 200, 'msg': 'success'}
                    return Response(content,status.HTTP_200_OK)
                except Exception, e:
                    logger.error(e.message)
                    content = {"retcode": 500, "msg": e.message}
                    return Response(content,status.HTTP_500_INTERNAL_SERVER_ERROR)
            elif user_name is None:
                logger.info('your token had expired')
                content = {'msg': 'your token had expired', 'retcode': 500}
                return Response(content,status.HTTP_500_INTERNAL_SERVER_ERROR)
            elif record is not None:
                logger.info('Request asked only once per minute')
                content = {'msg': 'Request asked only once per minute,please try again after one minute.', 'retcode': 500}
                return Response(content,status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif request.method == 'GET':
            logger.info('Method GET not allowed.')
            content = {'msg': 'Method GET not allowed.', 'retcode': 500}
            return Response(content,status.HTTP_500_INTERNAL_SERVER_ERROR)

    @list_route(url_path='copy_file', methods=['post', 'get'])
    def copy(self,request):
        if request.method == 'POST':
            token = request.META['HTTP_TOKEN']
            user_name = self.token_cache.get(token)
            record_key = token+'copy'
            record = self.record_cache.get(record_key)
            if user_name is not None and record is None:
                f = request.FILES.get('file')
                fname = f.name
                file_dir = os.path.join(settings.UPLOAD_ROOT, user_name)
                ip_list = request.data["ip_list"] + ','
                path = request.data['path']
                now = datetime.datetime.now()
                bak_date = now.strftime("%Y-%m-%d_%H%M%S")
                try:
                    if os.path.exists(os.path.join(file_dir, fname)):
                        file_name = fname.split('.')[0] + '_'
                        extension = '.' + fname.split('.')[1]
                        os.rename(os.path.join(file_dir, fname),
                                  os.path.join(file_dir, file_name + bak_date + extension)) #backed up the file which have the same file name
                    default_storage.save(os.path.join(file_dir, fname),
                                         ContentFile(f.read()))  # save the file under the /path/to/project/static/upload/[user_name]
                    cmd = 'src=' + os.path.join(file_dir, fname + ' dest=' + path)
                    runner = ansible.runner.Runner(module_name='copy', remote_user='root', host_list=ip_list,
                                                   pattern='all',
                                                   module_args=cmd,
                                                   forks=100)
                    result = runner.run()
                    logger.info(result)
                    log = Log()
                    log.write_log(result,user_name)
                    self.record_cache.set(record_key, 'copy')
                    content = {'msg': result, 'retcode': 200}
                    return Response(content,status.HTTP_200_OK)
                except Exception, e:
                    logger.error(e.message)
                    raise
                    content = {'retcode': 500, 'msg': e.message}
                    return Response(content,status.HTTP_500_INTERNAL_SERVER_ERROR)
            elif user_name is None:
                logger.info('your token had expired')
                content = {'msg': 'your token had expired', 'retcode': 500}
                return Response(content,status.HTTP_500_INTERNAL_SERVER_ERROR)
            elif record is not None:
                logger.info('Request asked only once per minute')
                content = {'msg': 'Request asked only once per minute,please try again after one minute.', 'retcode': 500}
                return Response(content,status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif request.method == 'GET':
            logger.info('Method GET not allowed.')
            content = {'msg': 'Method GET not allowed.', 'retcode': 500}
            return Response(content,status.HTTP_500_INTERNAL_SERVER_ERROR)


    @list_route(url_path='run',methods=['post', 'get'])
    def run(self,request):

        if request.method == 'POST':
            token = request.META['HTTP_TOKEN']
            user_name = self.token_cache.get(token)
            ip = request.data["ip"]
            record_key = token+'run'
            record = self.record_cache.get(record_key)
            if user_name is not None and ip.find(',') == -1 and record is None:
                cmd = request.data['command']
                #ip_str = ','.join(ip) + ','
                ip_str = ip+','
                if cmd.find(".sh") != -1 or cmd.find(".py") != -1:
                    runner = ansible.runner.Runner(module_name='script',remote_user='root', host_list=ip_str, timeout=10,pattern='all', module_args=os.path.join(settings.UPLOAD_ROOT+ '/' + cmd), forks=100)
                else:
                    runner = ansible.runner.Runner(module_name='shell', remote_user='root', host_list=ip_str,pattern='all', module_args=cmd,forks=100)
                result = runner.run()
                logger.info(result)
                log = Log()
                log.write_log(result, user_name)
                self.record_cache.set(record_key, 'run')
                content = {'msg': result, 'retcode': 200}
                return Response(content,status.HTTP_200_OK)

            elif user_name is None:
                logger.info('your token had expired')
                content = {'msg': 'your token had expired.', 'retcode': 500}
                return Response(content,status.HTTP_500_INTERNAL_SERVER_ERROR)
            elif record is not None:
                logger.info('Request asked only once per minute')
                content = {'msg': 'Request asked only once per minute,please try again after one minute.', 'retcode': 500}
                return Response(content,status.HTTP_500_INTERNAL_SERVER_ERROR)
            elif len(ip) != 1:
                logger.info('Only operated one machine for each request')
                content = {'msg': 'Only operated one machine for each request.','retcode': 500}
                return Response(content,status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif request.method == 'GET':
            logger.info('Method GET not allowed.')
            content = {'msg': 'Method GET not allowed.', 'retcode': 500}
            return Response(content,status.HTTP_500_INTERNAL_SERVER_ERROR)

