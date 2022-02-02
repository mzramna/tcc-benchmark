from monitorContainer import HardwareMonitor
from pprint import pprint
from os import DirEntry
import docker,json
#pprint(HardwareMonitor("./scripts/dados.json").get_data())
#HardwareMonitor("./scripts/dados.json").monitor(iterations=True,delay=0.01)

def build_message(hardwareMonitor:HardwareMonitor,logging,docker_client:docker.DockerClient):
    message=hardwareMonitor.get_data()

    logging.send_data_to_log("",level="info",extra=message)


def create_logging(file:DirEntry):
    return HardwareMonitor(file).logging
log_data="./scripts/dados.json"
h=HardwareMonitor(log_data)
dados=json.loads(open(log_data).read())
logging=h.logging
dClient = docker.DockerClient(base_url="tcp://127.0.0.1:2375",version="auto")
build_message(hardwareMonitor=h,logging=logging)