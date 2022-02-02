import psutil,json,time
from loggingSystem import loggingSystem 
from os import name,DirEntry
from os.path import exists as exists
from tratamentoErro import ValorInvalido
class HardwareMonitor():
    def __init__(self,log_data:DirEntry="dados.json",PROCFS_PATH="/proc/"):
        psutil.PROCFS_PATH = PROCFS_PATH
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
    
    def filter_dict(self,dictionary,filter_:list):
        retorno={}
        if type(dictionary) != type({}):
            dictionary=self.class_to_dict(dictionary)

        for your_key in filter_:
            try:
                if type(dictionary[your_key]) not in [type({}),type("")]:
                    retorno[your_key]=str(dictionary[your_key])
                else:
                    retorno[your_key]=dictionary[your_key]
                
            except KeyError as e:
                pass
        return retorno

    def class_to_dict(self,element):
        retorno={}
        #{ your_key: message[dado].__getattribute__(your_key) for your_key in message[dado]._fields }
        try:
            retorno = element.__dict__
        except:
            for your_key in element._fields:
                retorno[your_key]=str(element.__getattribute__(your_key))
        return retorno

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
                            try:
                                if type(message[dado][i]) not in [type({}),type("")]:
                                    tmp[i]=str(message[dado][i])
                                else:
                                    tmp[i]=message[dado][i]
                            except KeyError as e:
                                pass
                        else:
                            try:
                                if type(message[dado]) is type([]):
                                    tmp={}
                                    for i in range(len( message[dado])):
                                        tmp[dado+"_"+str(i)]=self.filter_dict(dictionary=message[dado][i],filter_=monitoring_columns)
                                else:
                                    tmp[i]=self.filter_dict(dictionary=message[dado][i],filter_=monitoring_columns)
                            except KeyError as e:
                                pass

                else:
                    for i in monitoring_return:
                        if len(monitoring_columns)<1:
                            try:
                                if type(message[dado][i]) not in [type({}),type("")]:
                                    tmp[i]=str(message[dado][i])
                                else:
                                    tmp[i]=message[dado][i]
                            except KeyError as e:
                                pass
                        else:
                            try:
                                tmp[i]=self.filter_dict(dictionary=message[dado][i],filter_=monitoring_columns)
                            except KeyError as e:
                                pass
                if tmp=={}:
                    if type(message[dado]) not in [type({}),type("")]:
                        tmp=str(message[dado])
                    else:
                        tmp=message[dado]
                message[dado]=tmp
            else:
                if len(monitoring_columns)<1:
                    if type(message[dado]) is type([]):
                        tmp={}
                        for i in range(len( message[dado])):
                            if type(message[dado]) not in [type({}),type("")]:
                                tmp[dado+"_"+str(i)]=str(message[dado][i])
                            else:
                                tmp[dado+"_"+str(i)]=message[dado][i]
                        message[dado]=tmp
                        # message[dado]=message[dado]
                    elif type(message[dado]) is type({}):
                        pass
                    else:
                        message[dado]=self.class_to_dict(message[dado])
                else:
                    message[dado]=self.filter_dict(dictionary=message[dado],filter_=monitoring_columns)
        return message

    def get_data_class(self,monitoring=None):
        message={}
        if monitoring is None:
            monitoring = self.monitoring
        for classe in list(monitoring.keys()):
            for dado in list(monitoring[classe].keys()):
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
                
                message[dado]= eval(classe+"."+dado+parameters)

                if "array" in monitoring[dado]:
                    tmp={}
                    monitoring_return=list(message[dado].keys())
                    if type(monitoring[dado]["array"]) is type([]):
                        for i in monitoring[dado]["array"]:
                            if len(monitoring_columns)<1:
                                try:
                                    tmp[i]=message[dado][i]
                                except KeyError as e:
                                    pass
                            else:
                                try:
                                    if type(message[dado]) is type([]):
                                        tmp={}
                                        for i in range(len( message[dado])):
                                            tmp[dado+"_"+str(i)]=self.filter_dict(dictionary=message[dado][i],filter_=monitoring_columns)
                                    else:
                                        tmp[i]=self.filter_dict(dictionary=message[dado][i],filter_=monitoring_columns)
                                except KeyError as e:
                                    pass

                    else:
                        for i in monitoring_return:
                            if len(monitoring_columns)<1:
                                try:
                                    tmp[i]=message[dado][i]
                                except KeyError as e:
                                    pass
                            else:
                                try:
                                    tmp[i]=self.filter_dict(dictionary=message[dado][i],filter_=monitoring_columns)
                                except KeyError as e:
                                    pass
                    if tmp=={}:
                        tmp=message[dado]
                    message[dado]=tmp
                else:
                    if len(monitoring_columns)<1:
                        if type(message[dado]) is type([]):
                            tmp={}
                            for i in range(len( message[dado])):
                                tmp[dado+"_"+str(i)]=message[dado][i]
                            message[dado]=tmp
                            # message[dado]=message[dado]
                        elif type(message[dado]) is type({}):
                            pass
                        else:
                            message[dado]=self.class_to_dict(message[dado])
                    else:
                        message[dado]=self.filter_dict(dictionary=message[dado],filter_=monitoring_columns)
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

    def monitor(self,iterations=True,delay:float=0,level="info",monitoring=None):
        if iterations is True:
            while True:
                time.sleep(delay)
                self.send_data_to_log(level=level,message="",extra=self.get_data(monitoring))
        else:
            for _ in range(iterations):
                time.sleep(delay)
                self.send_data_to_log(level=level,message="",extra=self.get_data(monitoring))
