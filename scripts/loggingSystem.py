import logging
class loggingSystem:
    def __init__(self,  arquivo='./arquivo.log', format='%(name)s - %(levelname)s - %(message)s',level=logging.DEBUG):
        """
        :param name: nome do log a ser escrito no arquivo
        :param arquivo: nome do arquivo a ser utilizado
        :param format: formato do texto a ser inserido no output do log
        :param level: nivel de log padrão de saida
        Level	Numeric value
        CRITICAL	50
        ERROR	40
        WARNING	30
        INFO	20
        DEBUG	10
        NOTSET	0
        """
        # formatter = logging.Formatter(format)
        # handler = logging.FileHandler(arquivo)
        # handler.setFormatter(formatter)
        # f = open(arquivo, "w+")
        # f.write("")
        # f.close()
        self.logger = logging
        self.logger.basicConfig(filename=arquivo, level=level,format=format)
        #self.logger.addHandler(handler)
        self.debug = self.logger.debug
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.info = self.logger.info
        self.log = self.logger.log
        self.critical = self.logger.critical
        self.fatal = self.logger.fatal
        self.exception = self.logger.exception