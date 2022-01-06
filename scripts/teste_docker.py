import docker
from datetime import datetime
# ssh = paramiko.SSHClient()
# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# ssh.connect("192.168.0.100",22, "root", "lzxb398211")
#client = docker.DockerClient(base_url="192.168.0.246:2375",version="auto")#usando docker sock
#client = docker.DockerClient(base_url="ssh://192.168.0.100:22",version="auto",use_ssh_client=True,user_agent="root")#usando ssh
show_log=False
for i in client.containers.list():
    print(i.name)
    print(i.id)
    print(i.status)
    if show_log:
        last="2022-01-01T00:00:00"
        for loop in range(20):
            array=str(i.logs(timestamps=True,since=datetime.fromisoformat(last))).split("\\n")#pegar iso format do timestamp e processar ele
            for j in array:
                print(j)
            last=array[-2][:19]
            #last=array[-2][:24]
        