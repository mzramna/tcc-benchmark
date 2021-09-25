import logging,logstash,inspect
class loggingSystem:
    def __init__(self,  arquivo='./arquivo.log', format:str='%(name)s - %(levelname)s - %(message)s',level=logging.DEBUG,name:str="",logstash_data:dict={}):
        """
        :param name: nome do log a ser escrito no arquivo
        :param arquivo: nome do arquivo a ser utilizado
        :param format: formato do texto a ser inserido no output do log
        :param level: nivel de log padrão de saida
        :param logstash_data: dados para conexão com logstash se possivel padrão:{"host":endereço ip,"port":porta}
        Level	Numeric value
        CRITICAL	50
        ERROR	40
        WARNING	30
        INFO	20
        DEBUG	10
        NOTSET	0
        """
        self.logger = logging
        
        if  set(["port","host"]).issubset(logstash_data):
            if name !="":
                self.logger = self.logger.getLogger(name)
            self.logger.setLevel(level)
            if set(["username","password"]).issubset(logstash_data):
                self.logger.addHandler(logstash.AMQPLogstashHandler(host=logstash_data["host"], port=logstash_data["port"], version=1,username=logstash_data["username"],password=logstash_data["password"],durable=True))
            else:
                self.logger.addHandler(logstash.TCPLogstashHandler(logstash_data["host"], logstash_data["port"], version=1))
        else:
            self.logger.basicConfig(filename=arquivo, level=level,format=format,)
            if name !="":
                self.logger = self.logger.getLogger(name)
        #self.logger.addHandler(handler)
        self.debug = self.logger.debug
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.info = self.logger.info
        self.log = self.logger.log
        self.critical = self.logger.critical
        self.fatal = self.logger.fatal
        self.exception = self.logger.exception

    def inspect_caller(self)->str:
        """função que chamou a função atual

        Returns:
            [type]: nome da funcao que chamou
        """        
        return  inspect.stack(context=1)[3][3]
    
    def full_inspect_caller(self)->list:
        """retorna lista com o rastreio das chamadas das funções até a execução atual

        Returns:
            [type]: lista de rastreio
        """        
        retorno=[]
        for i in list(inspect.stack(context=1))[1:-9]:
            retorno.append(i[3])
        return retorno