from monitor_container import HardwareMonitor
from pprint import pprint
#pprint(HardwareMonitor("./scripts/dados.json").get_data())
HardwareMonitor("./scripts/dados.json").monitor(iterations=True,delay=0.01)