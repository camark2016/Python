#coding=utf-8
#!/usr/bin/python
import os
import paramiko
#import pexpect
import socket
import time
import linecache
import datetime
import platform
import threading

def valid_ip(address):
    try: 
        socket.inet_aton(address)
        return True
    except:
        return False

def ssh2(ip,username,passwd,cmd):  
    try:  
        ssh = paramiko.SSHClient()  
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
        ssh.connect(ip,22,username,passwd,timeout=5)  
        for m in cmd:  
 #           print m
            stdin, stdout, stderr = ssh.exec_command(m) 
   #        stdin.write("Y")   #简单交互，输入 ‘Y’   
            out = stdout.readlines() 
            #屏幕输出  
   #         for o in out:  
   #            print o,  
   #    print '%s\tOK\n'%(ip)  
        ssh.close()  
    except :  
        print '%s\tError\n'%(ip)  

#if __name__=='__main__':  
#    cmd = ['cal','echo hello!']#你要执行的命令列表  
#    username = ""  #用户名  
#    passwd = ""    #密码  
#    threads = []   #多线程  

def getfile(ip,par_user,par_passwd,par_source_flie,par_dest_file):
    try:
       t = paramiko.Transport((ip,22))                                                                      
       t.connect(username = par_user, password = par_passwd)                                                                 
       sftp = paramiko.SFTPClient.from_transport(t)                                                                          
       localpath = par_source_flie
       remotepath = par_dest_file                                                                             
       sftp.get(localpath,remotepath)
       #print "get file is OK!"
    except:
       print "get file is faild!"
    finally:                                                                                 
       t.close() 

def putfile(ip,par_user,par_passwd,par_source_flie,par_dest_file):
    try:
       t = paramiko.Transport((ip,22))
       t.connect(username = par_user, password = par_passwd)
       sftp = paramiko.SFTPClient.from_transport(t)
       localpath = par_source_flie
       remotepath = par_dest_file
       sftp.put(localpath,remotepath)
       #print "put file is OK!"
    except:
       print "put file is faild!"
    finally:
       t.close()

class Netperf:
   def __init__(self,ip_list):
      self.ip_list = ip_list
   def get(self): 
      if (len(self.ip_list)%2) == 1:                                                                                       
         self.ip_list.insert(0,'0') 
      ip_count = len(self.ip_list)
      self.move(self.ip_list,ip_count/2,ip_count) 

   def move(self,a1,t,n):
      length = n
      fo = open(os.getcwd() + '/log/ip_vs.txt', "ab+")
      fo.truncate()
      fo.close()
      
      for i in range(0, len(self.ip_list) - 1):
         test1 = t
         test2 = 0
         ll = 0 
         a12 = ['']
         for ll in range(0,len(self.ip_list) -1 ):
            a12.insert(ll,'')
            ll = ll+1

         a12[0]=a1[0]
       #  print '第' + str(i+1) + '轮：'
         fo = open(os.getcwd() + '/log/ip_vs.txt', 'ab+')
         fo.write( '第' + str(i+1) + '轮比赛：\n');
         fo.close()

         while (test1 <= length - 1 ):
            fo = open(os.getcwd() + '/log/ip_vs.txt', "ab+")
            if (a1[test2] != '0' and test2 == 0) :

             #交换IP使之输出成T字型
               if int(a1[test2].replace('.','')) < int( a1[test1].replace('.','')) :
          #        print a1[test1] + " $ 11VS $ " + a1[test2]
                  fo.write( a1[test1] + ',' + a1[test2]+ '\n');
               else:
          #        print a1[test2] + " $ 22VS $ " + a1[test1]
                  fo.write( a1[test2] + ',' + a1[test1]+ '\n');
 
            elif (test2 != 0):
               if int(a1[t + test2].replace('.','')) < int( a1[t - test2].replace('.','')) :
          #        print a1[t - test2] + ' * 33VS * ' + a1[t + test2]                                                
                  fo.write( a1[t - test2] + ',' + a1[t + test2]+ '\n');
               else:
          #        print a1[t + test2] + ' * 44VS * ' + a1[t - test2] 
                  fo.write( a1[t + test2] + ',' + a1[t - test2]+ '\n');

            fo.close()
 
            if (test1 == length -1) :
               a12[1] = a1[test1]
               a12[test2 + 1] = a1[test2]
            else:
               #print 'a1[3]:  '+ a1[3]
               a12[test1 + 1] = a1[test1]
               if (test2 != 0):
                  a12[test2 + 1] = a1[test2]

            test1 = test1 + 1
            test2 = test2 + 1
         a1 = a12
         del a12
         i = i +1  

def check_ip(ip_list):
   i = 0
   result =''
   while i < len(ip_list):
      result = valid_ip(ip_list[i])
      if (result == False):
         print 'IP address: ' + ip_list[i] + ' is wrong, Please check ip_list'
         exit()
      i = i + 1


def start_netperf(ip_list):
   emp1 = Netperf(ip_list)
   emp1.get()
   if (ip_list[0] =='0'): 
      del ip_list[0];   


def vs_ip(host_user,host_passwd,times):
   f = open(os.getcwd() + '/log/ip_vs.txt','r')
   for line in open(os.getcwd() + '/log/ip_vs.txt'):
      line = f.readline()  
      line = line.strip()
      strip = str(line)
      i = 0
      if ( strip =='第1轮比赛：'):
         continue
 
      if ('轮比赛：' in strip) :
         time.sleep(times)
         continue

      ping_ip_from = strip[0:strip.find(',')]
      ping_ip_to   = strip[strip.find(',')+1:]


     # print line
     # print 'ping_ip_from: ' +ping_ip_from
     # print 'ping_ip_to: '+ ping_ip_to
     # print '***********time*******= ' + str(datetime.datetime.now())
      ospath = os.getcwd()
      
      cmdstr =['killall -9 netserver','rm -rf /opt/auto_netperf/netperf','rm -rf /opt/auto_netperf/netserver','mkdir -p /opt/auto_netperf/']
      ssh2(ping_ip_from,host_user,host_passwd,cmdstr)
      
      
      ssh2(ping_ip_to,host_user,host_passwd,cmdstr)      
      
  
      putfile(ping_ip_from,host_user,host_passwd,ospath + '/netperf','/opt/auto_netperf/netperf') 
      cmdstr =['chmod +x /opt/auto_netperf/netperf']
      ssh2(ping_ip_from,host_user,host_passwd,cmdstr)

      putfile(ping_ip_to,host_user,host_passwd,ospath + '/netserver','/opt/auto_netperf/netserver')
      cmdstr =['chmod +x /opt/auto_netperf/netserver','/opt/auto_netperf/netserver &']
      ssh2(ping_ip_to,host_user,host_passwd,cmdstr) 

      netperf_cmd='/opt/auto_netperf/netperf -f M -H ' + ping_ip_to + ' -l ' + str(times) +' '
      netperf_cmd_log='/opt/auto_netperf/' + ping_ip_from + '-vs-' + ping_ip_to + '_' +str(times)+'sec.txt'
      netperf_result_cmd= netperf_cmd + '>' + netperf_cmd_log + ' &'
      fw = open(os.getcwd() + '/log/files.txt', "ab+")
      fw.write(ping_ip_from +'###' +netperf_cmd_log + '\n')

      fw.close()

      cmdstr=[netperf_result_cmd]
      #ssh2(ping_ip_from,host_user,host_passwd,cmdstr)
      a=threading.Thread(target=ssh2,args=(ping_ip_from,host_user,host_passwd,cmdstr))
      a.start()
      
 
   f.close() 


def result(ip_list,times_list):
   
   column_width = 15
   fo = open(os.getcwd() + '/result_log.txt', "ab+")
   fo.truncate()

   for for_times in range(0,len(times_list) ):
      fo = open(os.getcwd() + '/result_log.txt', "ab+")
      if for_times > 0 :
         fo.write('\n')
      for for_ip in range(0,len(ip_list)  ):
         host_ip = ip_list[for_ip].rjust(column_width,' ')
         if (for_ip == 0):
            host_ip= ('持续: '+times_list[for_times] +'s (MB)   ').ljust(column_width,' ')  + host_ip
         fo.write(host_ip);
      fo.write('\n')
      fo.close()

      for i in range(0,len(ip_list) ):
         test_values = '' 
         host_ip = ip_list[i].ljust(column_width,' ')
          
         for for_ip in range(len(ip_list) ):
           
            seed = ''
            fw = open(os.getcwd() + '/log/files.txt','r') 
            for filename in open(os.getcwd() + '/log/files.txt'): 
               seed = '' 
               last_record = ''   
               filename = fw.readline()                                                                                     
               filename = filename.strip()
               filename = filename[filename.find('###/opt/auto_netperf/') + 21:]
               filename = os.getcwd() + "/log/"+ filename
               
               if ((ip_list[i] + '-vs-' ) in filename) and ( ip_list[for_ip] + '_' + times_list[for_times] +'sec.txt' in filename) :
                  f_log = open(filename,'r')
                  linecount = len(f_log.readlines());
                  last_record = linecache.getline(filename,linecount)
                  f_log.close()
                  last_record=str(last_record).rstrip()
            
                  seed= str(last_record[last_record.rfind(' ') +1:])
                # seed = str( round(float(seed)/8/1024/1024,00))+'MB'
                # print 'seeed>>>'+ seed
                  break
            seed = seed.rjust(column_width,' ')
            test_values = test_values + seed
         test_values = ip_list[i].ljust(column_width,' ') + test_values 
         
         fo = open(os.getcwd() + '/result_log.txt', "ab+")
         fo.write(test_values + '\n')
         fo.close()

def scp_log(host_user,host_passwd,ip_list):
   
   for i in range(0,len(ip_list)  ):
      host_ip = ip_list[i]
      fw = open(os.getcwd() + '/log/files.txt','r')
      for line in open(os.getcwd() + '/log/files.txt'):
         line = fw.readline()
         line = line.strip()
         if (( ip_list[i] + '###' ) in line) :
            filename = line[line.find('###') + 3:]
            save_filename = line[line.find('###/opt/auto_netperf/') + 21:]
            getfile(host_ip,host_user,host_passwd,filename,os.getcwd() + '/log/' + save_filename )
      fw.close()


def get_option(option_key):
   fw = open(os.getcwd() + '/ndty.options','r')                                                                   
   for line in open(os.getcwd() + '/ndty.options'):                                                               
      line = fw.readline() 
      line = line.strip()              
      if ((option_key + '=' ) in line) :
         result=line[line.find('=') + 1 :]
         return result  


def get_vs_times(times_list):
   vs_count = 0
   fw = open(os.getcwd() + '/log/ip_vs.txt','r')                                                         
   for filename in open(os.getcwd() + '/log/ip_vs.txt'):                                                 
      filename = fw.readline()                                                                                         
      filename = filename.strip()
      if ('轮比赛' in filename ):
         vs_count = vs_count + 1
      else:
        continue
   #print 'vs_count: '+ str(vs_count)                                                                                                          
   times = 0
   t = 0
   rtn_time = 0
   for i in range(0,len(times_list)):                                                                                
      if i > 0 : 
         t = int(times_list[i - 1] )                                                                             
      times = int( times_list[i] ) * vs_count  +int( times_list[i] ) + int(t)
      times = times + int( times_list[i] )
      rtn_time = rtn_time + times
   #rtn_time = rtn_time + int( times_list[i] )                                                                           
   return rtn_time



def drop_script(host_user,host_passwd,ip_list):
   for i in range(0,len(ip_list)):
      cmdstr =['killall -9 netserver','rm -rf /opt/auto_netperf/']
      ssh2(ip_list[i],host_user,host_passwd,cmdstr)

def view_result():
   print '\n\n*********************************执行结果：*************************************\n'
   fo = open(os.getcwd() + '/result_log.txt', 'r+')
   for line in open(os.getcwd() + '/result_log.txt'):   
      str = fo.readline().strip()
      print str
   fo.close()

host_user = get_option('host_user')                                                                               
host_passwd = get_option('host_passwd') 

#获取主机的IP列表      
ip_list = list()
ip_list = get_option('hosts')
ip_list = ip_list.rstrip().split(',')
#ip_list.sort()

#获取测试个数：比如 分别 测试5秒、10秒的netperf性能
times_list = list()
times_list = get_option('times')
times_list = times_list.split(',')
times_list.sort()


fo = open(os.getcwd() + '/log/files.txt','ab+')                                                                      
fo.truncate()                                                                                                 
fo.close()

#检查IP地址是否标准
check_ip(ip_list)

#获取主机间的vs
start_netperf(ip_list)

#估计此次脚本执行的总时间
vs_times = 0
vs_times = get_vs_times(times_list)
d1 = datetime.datetime.now() + datetime.timedelta(seconds=int(vs_times) )  
print '\n------此次脚本执行的总时间约为：'+str(vs_times ) +' 秒'
print '\n------脚本执行截止时间约为：'+str(d1)[0:19]

tmp_time_list =list()

for i in range(0,len(times_list)):
   if i > 0 :
      time.sleep(int(times_list[i - 1] ) )
   
   tmp_time_list.insert(0,times_list[i])
   exec_sec=get_vs_times(tmp_time_list)   
   print '\n         当前正在测试 netperf - '+ times_list[i] + '秒的测试，需要' + str(exec_sec) +'秒，请耐心等待'

  # print '第' + str(i) + '次'
   vs_ip(host_user,host_passwd,int(times_list[i]))
   del tmp_time_list[0]

time.sleep(int(times_list[i]))

#整合各个机器上测试结果的文件
scp_log(host_user,host_passwd,ip_list)

#返回最终的测试结果
result(ip_list,times_list)
view_result()

drop_script(host_user,host_passwd,ip_list)



