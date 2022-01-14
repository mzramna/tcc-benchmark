from monitor_container import HardwareMonitor

print(HardwareMonitor("/config/dados.json",PROCFS_PATH="/proc/").get_data())
HardwareMonitor("/config/dados.json").monitor(iterations=True,delay=0.1)