import psutil,json
from loggingSystem import loggingSystem 
from os import name,DirEntry
from os.path import exists as exists
from tratamentoErro import ValorInvalido
class HardwareMonitor():
    def __init__(self,log_data:DirEntry="dados.json"):
        ##por um name diferente para cada container no arquivo de configuração
        if exists(log_data):
            dados=json.loads(open(log_data).read())
        else:
            dados={"dados_log":{},"monitor_data":{}}

        self.logging = loggingSystem(**dados["dados_log"])#name=log_name, arquivo=log_file,level=level,formato=logging_pattern,logstash_data=logstash_data
        self.monitoring=dados["monitor_data"]
        '''
        cpu_times:{parameters:{},columns:[user,system,idle,nice,iowait,irq,softirq,steal,guest,guest_nice]}
        cpu_percent:{parameters:{},columns:[percpu]}
        virtual_memory:{parameters:{},columns:[total,available,used,free,active,inactive,buffers,cached,shared,slab,wired]}
        swap_memory:{parameters:{},columns:[total,used,free,percent,sin,sout]}
        disk_usage:{parameters:{path:"/"},columns:[total,used,free,percent]}
        disk_io_counter:{parameters:{perdisk:True,nowrap:false},columns:[read_time,write_time,busy_time,read_bytes,write_bytes]}
        net_io_counters:{parameters:{pernic:False,nowrap:False},columns:[bytes_sent,bytes_recv,packets_sent,packets_recv]}
        process_iter:{parameters:{},columns:[pid,name,status,started]}

        '''

    def get_data(self,monitoring=None):
        message={}
        if monitoring is None:
            monitoring = self.monitoring
        for dado in list(monitoring.keys()):
            if "columns" in list(monitoring[dado].keys()):
                monitoring_columns=monitoring[dado]["columns"]
            else:
                monitoring_columns=[]
            if monitoring[dado]["parameters"]!={}:
                parameters="("
                for i in list(monitoring[dado]["parameters"].keys()):
                    parameters+=i
                    parameters+="="
                    if type(monitoring[dado]["parameters"][i]) is type(""):
                        parameters+="'"+monitoring[dado]["parameters"][i]+"'"
                    else:
                        parameters+=str(monitoring[dado]["parameters"][i])
                    if i != list(monitoring[dado]["parameters"].keys())[-1]:
                        parameters+=","
                parameters+=")"
            else:
                parameters="()"
            message[dado]= eval("psutil."+dado+parameters)
            if "array" in monitoring[dado]:
                tmp={}
                monitoring_return=list(message[dado].keys())
                if type(monitoring[dado]["array"]) is type([]):
                    for i in monitoring[dado]["array"]:
                        if len(monitoring_columns)<1:
                            tmp[i]=message[dado][i]
                        else:
                            tmp[i]={ your_key: message[dado][i].__getattribute__(your_key) for your_key in monitoring_columns }
                else:
                    for i in monitoring_return:
                        if len(monitoring_columns)<1:
                            tmp[i]=message[dado][i]
                        else:
                            tmp[i]={ your_key: message[dado][i].__getattribute__(your_key) for your_key in monitoring_columns }
                message[dado]=tmp
            else:
                if len(monitoring_columns)<1:
                    if type(message[dado]) is type([]):
                        message[dado]=message[dado]
                    else:
                        message[dado]={ your_key: message[dado].__getattribute__(your_key) for your_key in message[dado]._fields }
                else:
                    message[dado]={ your_key: message[dado].__getattribute__(your_key) for your_key in monitoring_columns }
        return message

    def send_data_to_log(self,message:str,level="info",extra={}):
        try:
            if not self.logging.send_data_to_log(message=message,level=level,extra=extra):
                raise ValorInvalido(campo="level",valor_inserido=level)
        except ValorInvalido as e:
            self.logging.exception(e)

    def send_hardware_status_to_log(self,level="info",monitoring=None):
        if monitoring is None:
            monitoring = self.monitoring
        self.send_data_to_log(level=level,message="",extra=self.get_data(monitoring=monitoring))

    def monitor(self,iterations=True,level="info",monitoring=None):
        if iterations:
            while True:
                self.send_data_to_log(level=level,message="",extra=self.get_data(monitoring))
        else:
            for _ in range(iterations):
                self.send_data_to_log(level=level,message="",extra=self.get_data(monitoring))
