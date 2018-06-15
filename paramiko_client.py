import paramiko
import time
import sys
import os


class ParamikoClient:

        def __init__(self, ip, user,port=22, key='/root/.ssh/id_rsa'):
            self.ip = ip
            self.user = user
            self.port = port
            self.private_key = paramiko.RSAKey.from_private_key_file(key)
            self.client = paramiko.SSHClient()
            self.client.load_system_host_keys()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
            try:
                self.client.connect(hostname=self.ip,
                                    port=self.port,
                                    username=self.user,
                                    pkey=self.private_key)
            except Exception as e:
                raise Exception('连接远程主机出现错误')
            self.transport = self.client.get_transport()
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)


        def down_app(self,local_dir,remote_dir):
            try:
                print("正在下载{}文件".format(remote_dir))
                self.sftp.get(local_dir,remote_dir)
                print("{}文件下载完成".format(remote_dir))
            except Exception as e:
                print("{}文件下载失败,请检查文件是否存在".format(remote_dir))


        def up_app(self,local_dir,remote_dir):
            try:
                print("主机{}:正在上传{}文件".format(self.ip,local_dir))
                self.sftp.put(local_dir,remote_dir)
                print("{}文件上专完成".format(local_dir))
            except Exception as e:
                print("主机{}:{}文件上传失败,请检查文件是否存在".format(self.ip,remote_dir))


        def tar_app(self,tar_cmd):
            stdin,stdout,stderr = self.client.exec_command(tar_cmd)
            error = stderr.read().decode()
            if not error:
                print("包已成功解压")


        def cp_app(self,cp_cmd):

            pass


        def backup_app(self,backup_cmd):
            try:
                print("----->>{}正在备份".format(self.ip))
                stdin,stdout,stderr = self.client.exec_command(backup_cmd)
                error = stderr.read().decode()
                success = stdout.read().decode()
                print(success)
                if not error:
                    print("主机：{}备份完成".format(self.ip) + "\n", )
                else:
                    print("主机：{}备份失败".format(self.ip) + "\n", error)
            except Exception as e:
                print("主机：{}备份失败,请检查".format(self.ip))


        def stop_app(self,stop_cmd,app):
            try:
                print("------->>>>:{}正在停应用".format(self.ip))
                stdin, stdout, stderr = self.client.exec_command(stop_cmd)
                error = stderr.read().decode()
                success = stdout.read().decode()
                print(success)
                if not error:
                    active = os.system("ps -ef | grep -v grep | grep {}".format(app))
                    if active:
                        print("{}应用停止成功".format(app))
                    else:
                        print("{}应用停止失败".format(app))
                else:
                    print(print("主机：{}应用停止失败".format(self.ip) + "\n", error))

            except Exception as e:
                print("主机：{},应用{}停止失败，请检查".format(self.ip,app))


        def start_app(self,start_cmd,app):
            try:
                print("----->>>{}正在启动应用".format(self.ip))
                stdin, stdout, stderr = self.client.exec_command(start_cmd)
                error = stderr.read().decode()
                success = stdout.read().decode()
                print(success)
                if not error:
                    #检查应用是否启动

                    active = os.system("ps -ef | grep -v grep | grep {}".format(app))
                    if active:
                        print("---->主机:{}---{}应用启动成功".format(self.ip,app))
                    else:
                        print("---->主机:{}---{}应用启动失败".format(self.ip, app))
                else:
                    print("主机：{}应用启动失败".format(self.ip) + "\n", error)
            except Exception as e:
                print("主机：{}应用启动失败,请检查".format(self.ip))



if __name__=='__main__':

    """应用部署相关信息"""
    date = time.strftime("%Y%m%d%H%M%S", time.localtime())
    count = 0
    ip = ['192.168.1.101']
    user = 'root'
    port=['8080','8081']
    source = "/app" #远程部署路径
    filename = 'apache-tomcat-7.0.88.tar.gz'  # 应用包名称
    local_dir='/root/{}'.format(filename) #应用包本地路径
    remote_dir='/app/{}'.format(filename) #应用包远程发布路径
    app_name = "apache-tomcat-7.0.88" #解压后的应用名称

    """执行命令"""
    tar_cmd = " cd {} && tar xf {} && rm -rf {}".format(source,remote_dir,remote_dir)
    backup_cmd = "mv /app/apache-tomcat-7.0.88 /opt/bak/{}_{}".format(app_name,date)
    stop_app_cmd = "ps -ef | grep /app/%s | grep -v grep | awk '{print $2}'|xargs kill -9" %app_name
    start_app_cmd = "cd {} &&  /app/apache-tomcat-7.0.88/bin/startup.sh".format(source)


    """执行应用"""
    if sys.argv[1] == 'tomcat':
        for i in ip:
            connect = ParamikoClient(i,user)
            if count ==0:
                pass
                #connect.down_app()
            connect.stop_app(stop_app_cmd,app_name)
            connect.backup_app(backup_cmd)
            connect.up_app(local_dir,remote_dir)
            connect.tar_app(tar_cmd)
            connect.start_app(start_app_cmd,app_name)
            count += 1



