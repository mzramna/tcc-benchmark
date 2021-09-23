from sqlite3 import Error as sqliteError
from sqlite3 import OperationalError as sqliteOperationalError
from loggingSystem import loggingSystem
import sqlite3,sys

class ProcessamentoSqlite:
    def __init__(self,sqlite_db="./initial_db.db",sql_file_pattern="./sqlitePattern.sql", log_file="./processadorSQlite.log",level:int=10,logging_pattern='%(name)s - %(levelname)s - %(message)s',log_name:str="gerenciador sqlite",logstash_data:dict={}):
        """
        classe para gerenciar arquivos sqlite
        :param loggin_name: nome do log que foi definido para a classe,altere apenas em caso seja necessário criar multiplas insstancias da função
        :param log_file: nome do arquivo de log que foi definido para a classe,altere apenas em caso seja necessário criar multiplas insstancias da função
        """
        self.logging = loggingSystem(name=log_name, arquivo=log_file,level=level,format=logging_pattern,logstash_data=logstash_data)
        self.create_temporary_DB(local=sqlite_db,pattern=sql_file_pattern)
        self.conn = sqlite3.connect(sqlite_db)
    
    def create_temporary_DB(self,local,pattern):
        """verifica a integridade do db caso ele n exista 

        Args:
            local (path): local onde o bd sqlite está salvo
            pattern (path): local onde o arquivo sql está salvo
        """        
        try:
            f = open(local, "a")
            f.write("")
            f.close()
            conn = sqlite3.connect(local)
            self.execute_sqlfile_sqlite(pattern,conn)
            conn.close()
            self.logging.info("bd gerado com sucesso")
        except sqliteOperationalError as e:
            print("erro operacional no sqlite")
            self.logging.error(e)
            quit()
        except sqliteError as e:
            print("erro desconhecido no sqlite")
            self.logging.error(e)
        except :
            self.logging.error("Unexpected error:", str(sys.exc_info()[0]))

    def insert_data_sqlite(self,data:dict,table:str=""):
        '''
        INSERT INTO "operacoes"(	"tipoOperacao",	"nomeBD","adicionais","dados")
        VALUES(1,"empregado","[(pessoas,pessoas_id,1),(lojas,loja_id)]","{salario:1200,contratado:30/12/20}")
        '''
        self.logging.info("insercao dado sqlite")
        insert_command="INSERT INTO "
        insert_command+="'"+"operacoes"+"' ("
        self.logging.debug(data)
        for coluna in data.keys():
            insert_command+=str(coluna)
            if table == "" and coluna == 'nomeBD':
                table=data["nomeBD"]
            if coluna !=  list(data.keys())[-1]:
                insert_command+=","
        insert_command+=") VALUES ("
        for coluna in data.keys():
            if type(data[coluna]) == type("") :
                insert_command+='"'+data[coluna].replace("\n","")+'"'
            elif type(data[coluna]) == type({}) or  type(data[coluna]) == type([]):
                for i in list(data[coluna]):
                    i.replace("\n","")
                insert_command+='"'+str(data[coluna])+'"'
            else:
                insert_command+=str(data[coluna])
            if coluna !=  list(data.keys())[-1]:
                insert_command+=","
        insert_command+=");"
        self.logging.debug(insert_command)
        try:
            cursor = self.conn.cursor()
            cursor.execute(insert_command)
            self.conn.commit()
        except sqliteOperationalError as e:
            print("erro operacional no sqlite")
            self.logging.error(e)
            quit()
        except sqliteError as e:
            print("erro desconhecido no sqlite")
            self.logging.error(e)
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])

    def read_data_sqlite(self,table:str,filtro:dict={},query="*"):
        self.logging.info("lendo sqlite")
        read_command=""
        read_command+="SELECT "
        if query != "*":
            read_command+="("
            for key in query:
                read_command+=key
                if key !=  query[-1]:
                    read_command+=","
            read_command+=")"
        else:
            read_command+=query
        read_command+=" FROM "
        read_command+="'"+table+"'"
        if filtro != {}:
            read_command+=" WHERE "
            for coluna in filtro.keys():
                        read_command+=str(coluna) + " IS "
                        if type(filtro[coluna])==type(""):
                            read_command+="'"+filtro[coluna]+"'"
                        else:
                            read_command+=str(filtro[coluna])
                        if coluna !=  list(filtro.keys())[-1]:
                            read_command+=" AND "
        read_command+=";"
        try:
            cursor = self.conn.cursor()
            self.logging.info(read_command)
            cursor.execute(read_command)
            self.conn.commit()
            saida=cursor.fetchall()
            return saida 
        except sqliteOperationalError as e:
            print("erro operacional no sqlite")
            self.logging.error(e)
            quit()
        except sqliteError as e:
            print("erro desconhecido no sqlite")
            self.logging.error(e)
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])

    def execute_sqlfile_sqlite(self,pattern:dict,conn=None):
        self.logging.info("executar arquivo sql em sqlite")
        if conn != None:
            cursor = conn.cursor()
        else:
            cursor=self.conn.cursor()
        sqlfile=open(pattern).read().split(";\n")
        for sqlstatement in sqlfile:
            if sqlstatement[-1] != ";":
                sqlstatement+=";"
            self.logging.debug(sqlstatement)
            cursor.execute(sqlstatement)
            conn.commit()