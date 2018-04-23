
import datetime

import os

from ansibleAPI import settings


class Log:

    def __init__(self):
        pass

    def write_log(self,res, user_name):
        now = datetime.datetime.now()
        log_day = now.strftime("%Y-%m-%d")
        success_host_list = res["contacted"].keys()
        failed_host_list = res["dark"].keys()
        if os.path.exists(settings.ANSIBLE_LOG_ROOT + log_day): #the log directory exists or not
            for i in range(len(success_host_list)):
                os.chdir(settings.ANSIBLE_LOG_ROOT + log_day)
                if os.path.exists(success_host_list[i]):
                    self.write_success_log(res, success_host_list[i], user_name)
                else:
                    os.mkdir(success_host_list[i])
                    self.write_success_log(res, success_host_list[i], user_name)
            if len(failed_host_list) > 0: #if have the failed host's ip
                for i in range(len(failed_host_list)):
                    os.chdir(settings.ANSIBLE_LOG_ROOT + log_day)
                    if os.path.exists(failed_host_list[i]):
                        self.write_failed_log(res, failed_host_list[i], user_name)
                    else:
                        os.mkdir(failed_host_list[i])
                        self.write_failed_log(res, failed_host_list[i], user_name)
        else:
            os.mkdir(settings.ANSIBLE_LOG_ROOT + log_day)
            for i in range(len(success_host_list)):
                os.chdir(settings.ANSIBLE_LOG_ROOT + log_day)
                if os.path.exists(success_host_list[i]):
                    self.write_success_log(res, success_host_list[i], user_name)
                else:
                    os.mkdir(success_host_list[i])
                    self.write_success_log(res, success_host_list[i], user_name)
            if len(failed_host_list) > 0:
                for i in range(len(failed_host_list)):
                    os.chdir(settings.ANSIBLE_LOG_ROOT + log_day)
                    if os.path.exists(failed_host_list[i]):
                        self.write_failed_log(res, failed_host_list[i], user_name)
                    else:
                        os.mkdir(failed_host_list[i])
                        self.write_failed_log(res, failed_host_list[i], user_name)

    def write_success_log(self,res, ip, user_name):

        now = datetime.datetime.now()
        log_date = now.strftime("%H:%M:%S")
        log_day = now.strftime("%Y-%m-%d")
        log_file = open(settings.ANSIBLE_LOG_ROOT + log_day + '/' + ip + '/' + log_date + '.log', 'w')
        log_file.write('time:' + log_date + '\nuser_name:' + user_name + '\nhost:' + ip + '\nmsg:' + str(res["contacted"][ip]["invocation"]) + '\n')
        log_file.close()

    def write_failed_log(self,res, ip, user_name):
        now = datetime.datetime.now()
        log_date = now.strftime("%H:%M:%S")
        log_day = now.strftime("%Y-%m-%d")
        log_file = open(settings.ANSIBLE_LOG_ROOT + log_day + '/' + ip + '/' + log_date + '.log', 'w')
        log_file.write('time:' + log_date + '\nuser_name:' + user_name + '\nhost:' + ip + '\nmsg:' + res["dark"][ip]["msg"] + '\n')
        log_file.close()