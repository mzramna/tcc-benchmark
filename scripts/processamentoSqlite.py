from sqlite3 import Error as sqliteError
from sqlite3 import OperationalError as sqliteOperationalError
from loggingSystem import LoggingSystem
import sqlite3,sys,os,time
from typing import Union

class ProcessamentoSqlite:
    def __init__(self,sqlite_db="./initial_db.db",sql_file_pattern="scripts/sqlitePattern.sql", log_file="./processadorSQlite.log",level:int=10,logging_pattern='%(name)s - %(levelname)s - %(message)s',log_name:str="gerenciador sqlite",logstash_data:dict={},thread=False):
        """
        classe para gerenciar arquivos sqlite
        :param loggin_name: nome do log que foi definido para a classe,altere apenas em caso seja necessário criar multiplas insstancias da função
        :param log_file: nome do arquivo de log que foi definido para a classe,altere apenas em caso seja necessário criar multiplas insstancias da função
        """
        self.logging = LoggingSystem(name=log_name, arquivo=log_file,level=level,formato=logging_pattern,logstash_data=logstash_data)
        self.create_temporary_DB(local=sqlite_db,pattern=sql_file_pattern)
        if thread is True:
            self.conn = sqlite3.connect(sqlite_db,check_same_thread=False)
        else:
            self.conn = sqlite3.connect(sqlite_db)
        self.stack_overflow_max=5
    
    def create_temporary_DB(self,local,pattern):
        """verifica a integridade do db caso ele n exista 

        Args:
            local (path): local onde o bd sqlite está salvo
            pattern (path): local onde o arquivo sql está salvo
        """
        try:
            if not os.path.isfile(local):
                f = open(local, "a")
                f.write("")
                f.close()
                conn = sqlite3.connect(local)
                self.execute_sqlfile_sqlite(pattern,conn)
                conn.close()
                self.logging.info("bd gerado com sucesso")
            else:
                self.logging.info("bd já existe")
        except sqliteOperationalError as e:
            #print("erro operacional no sqlite")
            self.logging.error(e)
            quit()
        except sqliteError as e:
            #print("erro desconhecido no sqlite")
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
        insert_command+="'"+table+"' ("
        self.logging.debug(data)
        for coluna in data.keys():
            insert_command+=str(coluna)
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
            #print("erro operacional no sqlite")
            self.logging.error(e)
            time.sleep(0.001)
            try:
                chamadas=LoggingSystem.full_inspect_caller() 
                if chamadas.count(chamadas[0])>self.stack_overflow_max: 
                    return None
            except IndexError as e:
                pass
            except:
                raise
            self.insert_data_sqlite(data=data,table=table)
        except sqliteError as e:
            #print("erro desconhecido no sqlite")
            self.logging.error(e)
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])

    def read_data_sqlite(self,table:str,filtro:Union[str,dict]="*",query:Union[str,dict]="*"):
        self.logging.info("lendo sqlite")
        read_command=""
        read_command+="SELECT "
        if filtro != "*":
            read_command+="("
            for key in filtro:
                read_command+=key
                if len(filtro)>1:
                    if key !=  filtro[-1]:
                        read_command+=","
            read_command+=")"
        else:
            read_command+=filtro
        read_command+=" FROM "
        read_command+="'"+table+"'"
        if query != "*":
            read_command+=" WHERE "
            for coluna in query.keys():
                        read_command+=str(coluna) + " IS "
                        if type(query[coluna])==type(""):
                            read_command+="'"+query[coluna]+"'"
                        else:
                            read_command+=str(query[coluna])
                        if coluna !=  list(query.keys())[-1]:
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
            #print("erro operacional no sqlite")
            self.logging.error(e)
            return self.read_data_sqlite(table,filtro,query)
        except sqliteError as e:
            #print("erro desconhecido no sqlite")
            self.logging.error(e)
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])

    def execute_sqlfile_sqlite(self,pattern:dict,conn=None):
        self.logging.info("executar arquivo sql em sqlite")
        try:
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
        except sqliteOperationalError as e:
            #print("erro operacional no sqlite")
            self.logging.error(e)
            return self.execute_sqlfile_sqlite(pattern,conn)
        except sqliteError as e:
            #print("erro desconhecido no sqlite")
            self.logging.error(e)
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])

    def dict_all_string(self,entrada:dict)-> dict:
        retorno={}
        for i in entrada.keys():
            if type(i)==type(""):
                retorno[i]=entrada[i]
            else:
                retorno[i]=str(entrada[i])