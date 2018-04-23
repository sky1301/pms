import os
import sys
import commands

import commands
from multiprocessing import Process
import signal
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework.permissions import AllowAny
import logging

logger = logging.getLogger('pmsd')
class PmsdView(viewsets.ViewSet):

    permission_classes = (AllowAny,)
    KEY_F = '/etc/ansible/pmskey.gpg'

    @list_route(url_path='help',methods=['get'])
    def usage(self,request):
        log_content = "%s" % ( "success")
        logger.info(log_content)
        return Response({"CommonAPI": [{'add': 'http://server/pms/add/host1.example.com/192.168.0.1,192.168.0.2,192.157.0.3/root/linux'},
            {'delete': 'http://server/pms/delete/ip/user'},
            {'reset': 'http://server/pms/reset/uid/ip/user'},
            {'query': 'http://server/pms/query/uid/ip/user'}
             ]})

    @list_route(url_path='query/(.+)/(.+)/(.+)', methods=['get'])
    def get_password(self, request,userid,qiplist,quser):
        uid = userid
        ip = qiplist
        user = quser
        os.environ['id'] = uid
        os.environ['host'] = qiplist
        os.environ['user'] = quser
        getrc, getout = commands.getstatusoutput('pmscmd query --ip=["%s"]  --user="%s" -k="%s" ' % (ip, user, self.KEY_F))
        ous = None
        if getrc == 0:
            ous = getout.split('===>')[1].strip('\0').strip(']').strip('[').strip("'")
            log_content = "%s - %s"%(ip,"success")
            logger.info(log_content)
            return Response({"ip": ip, "user": user, "password": ous})
        else:
            log_content = "%s - %s"%(ip,"fail")
            logger.error(log_content)
            return Response({"result": "fail", "msg": getout})

    @list_route(url_path='delete/(.+)/(.+)',methods=['GET'])
    def delete_entry(self,request,dip, duser):
        # task = filter(lambda t: t['id'] == task_id, tasks)
        # if len(task) == 0:
        # abort(404)
        IP = dip
        USER = duser
        getrc, getout = commands.getstatusoutput('pmscmd  delete --ip="%s"  --user="%s" ' % (IP, USER))
        if getrc == 0:
            log_content = "%s - %s"%(IP,"success")
            logger.info(log_content)
            return Response({"result": "success"})
        else:
            log_content = "%s - %s"%(IP,"fail")
            logger.error(log_content)
            return Response({"result": "fail", "msg": getout})


    @list_route(url_path='reset/(.+)/(.+)/(.+)',methods=['GET'])
    def get_reset(self,request,userid, qiplist, quser):
        uid = userid
        ip = qiplist
        user = quser
        os.environ['id'] = uid
        os.environ['host'] = ip
        os.environ['user'] = user
        getrc, getout = commands.getstatusoutput('pmscmd reset --ip="%s"  --user="%s" -k="%s"' % (ip, user, self.KEY_F))
        if getrc == 0:
            log_content = "%s - %s"%(ip,"success")
            logger.info(log_content)
            return Response({"result": "success"})
        else:
            log_content = "%s - %s"%(ip,"fail")
            logger.error(log_content)
            return Response({"result": "fail", "msg": getout})

    @list_route(url_path='add/(.+)/(.+)/(.+)/(.+)', methods=['GET'])
    def add_entry(self,request,qhname, qips, quser, qos):
        hostname = qhname
        ips = qips
        user = quser
        ost = qos
        getrc, getout = commands.getstatusoutput('pmscmd add --ips="%s"  --user="%s" --ostype="%s"' % (ips, user, ost))
        if getrc == 0:
            ips = ips.split(',')
            ips.sort(lambda x, y: cmp(''.join([i.rjust(3, '0')
                                               for i in x.split('.')]),''.join([i.rjust(3, '0') for i in y.split('.')])))
            log_content = "%s - %s"%(ips,"success")
            logger.info(log_content)
            return Response({"hostname": hostname, "main_ip": ips[0]})
        else:
            log_content = "%s - %s"%(ips,"success")
            logger.error(log_content)
            return Response({"result": "fail", "msg": getout})