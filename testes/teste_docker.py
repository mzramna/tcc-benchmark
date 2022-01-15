import docker
from datetime import datetime
client = docker.DockerClient(base_url="192.168.0.100:2375",version="auto")#usando docker sock
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
        