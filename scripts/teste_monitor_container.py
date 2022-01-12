from monitor_container import HardwareMonitor
from pprint import pprint
pprint(HardwareMonitor("./scripts/dados.json").get_data())