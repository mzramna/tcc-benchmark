#from processamentoSqlite import ProcessamentoSqlite 
from typing import Union
import json
from random import randint, random,uniform,choice,sample
from loggingSystem import LoggingSystem
import sqlite3,sys,json,os,time
from typing import Union
from sqlite3 import OperationalError as sqliteOperationalError
from sqlite3 import Error as sqliteError
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
        if type(filtro) != type("*"):
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
            time.sleep(0.5)
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
class InteracaoSqlite(ProcessamentoSqlite):
    def __init__(self,sqlite_db="./initial_db.db",sql_file_pattern="./sqlitePattern.sql", log_file="./geradorSQL.log",level:int=10,logging_pattern='%(name)s - %(levelname)s - %(message)s',logstash_data:dict={}):
        """
        classe para gerenciar arquivos csv
        :param loggin_name: nome do log que foi definido para a classe,altere apenas em caso seja necessário criar multiplas insstancias da função
        :param log_file: nome do arquivo de log que foi definido para a classe,altere apenas em caso seja necessário criar multiplas insstancias da função
        """
        
        super().__init__(sqlite_db=sqlite_db,sql_file_pattern=sql_file_pattern,log_file=log_file,logging_pattern=logging_pattern,level=level,log_name="gerador sql interacao sqlite",logstash_data=logstash_data,thread=True)
        #self.create_temporary_DB(local=sqlite_db,pattern=sql_file_pattern)
        
    def buscar_ultimo_id_cadastrado(self,table:str)->int:
        """musca o ultimo id cadastrado de uma tabela expecifica

        Args:
            table (str): [nome da tabela que sera pesquisada]

        Returns:
            int:ultimo id cadastrado da tabela informada
        """        
        self.logging.info("buscar_ultimo_id_cadastrado",extra=locals())
        query={"nomeBD":table}
        filtro=["numeroDDadosCadastrados"]
        self.certify_if_contador_exists(table)
        retorno=self.read_data_sqlite(table="contadores",query=query,filtro=filtro)
        self.logging.debug("ultimo id cadastrado",extra={"retorno":retorno[0][0]})
        return int(retorno[0][0])

    def random_id_cadastrado(self,table:str) -> int:
        """um id aleatorio dentre os cadastrados numa tabela definida

        Args:
            table (str): nome da tabela que sera usada

        Returns:
            int: um id aleatorio de um bd
        """        
        self.logging.info("random_id_cadastrado",extra=locals())
        tmp=self.buscar_ultimo_id_cadastrado(table=table)
        tmp2=randint(1,tmp)
        self.logging.debug("",extra={"ultimo id":str(tmp),"valor escolhido":str(tmp2)})
        return tmp2

    def add_contador_sqlite(self,table:str):
        """aumenta em um o total de elementos cadastrados em uma tabela expecifica

        Args:
            table (str): nome da tabela
        """        
        self.logging.info("add_contador_sqlite",extra=locals())
        try:
            cursor = self.conn.cursor()
            self.certify_if_contador_exists(table)
            cursor.execute("UPDATE contadores SET numeroDDadosCadastrados = numeroDDadosCadastrados+1 WHERE nomeBD='"+table+"';")
            self.conn.commit()
            self.logging.debug("adicionado contador")
        except sqliteOperationalError as e:
           #print("erro operacional no sqlite")
            self.logging.exception(e)
            self.add_contador_sqlite(table=table)
        except sqliteError as e:
            #print("erro desconhecido no sqlite")
            self.logging.exception(e)
            
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])

    def total_operacoes(self)->int:
        """total de elementos cadastrados na tabela de operações

        Returns:
            int: total de elementos cadastrados na tabela de operações
        """        
        try:
            self.logging.info("buscar_ultimo_id_cadastrado",extra=locals())
            read_command="SELECT id FROM operacoes ORDER BY id DESC LIMIT 1;"
            cursor = self.conn.cursor()
            self.logging.info(read_command)
            cursor.execute(read_command)
            self.conn.commit()
            saida=cursor.fetchall()
            
            if saida == []:
                self.logging.debug("total de operacoes",extra={"total":saida})
                return 0
            else:
                self.logging.debug("total de operacoes",extra={"total":saida[0][0]})
                return int(saida[0][0])
        except:
            return 0
        
    def certify_if_contador_exists(self,table:str):
        """verifica e corrige se um contador não existir na tabela de contadores

        Args:
            table (str): nome da tabela que será verificada se existe o contador
        """        
        self.logging.info("certify_if_contador_exists",extra=locals())
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM contadores WHERE nomeBD is '"+table+"';")
        listagem=cursor.fetchall() 
        if listagem == []:
            cursor.execute("INSERT INTO contadores(nomeBD,numeroDDadosCadastrados) VALUES ('"+table+"',0);")

    def read_contadores(self,filtro:dict={},query:Union[str,dict]="*")->list:
        """consulta e le um elemento ou varios da tabela de contadores

        Args:
            filtro (dict, optional): elementos que serão retornados dos elementos . Defaults to {}.
            query (str, optional): elementos de pesquisa que serão usados . Defaults to "*".

        Returns:
            list: lista de todos elementos que foram reconhecidos pela query
        """        
        self.logging.info("read_contadores",extra=locals())
        return self.read_data_sqlite("contadores",filtro=filtro,query=query)

    def read_operacoes(self,filtro:Union[str,dict]="*",query:Union[str,dict]="*",tipo_adicional:str="dict")->list:
        """consulta e le um elemento ou varios da tabela de operações

        Args:
            filtro (dict, optional): elementos que serão retornados dos elementos . Defaults to {}.
            query (str, optional): elementos de pesquisa que serão usados . Defaults to "*".

        Returns:
            list: lista de todos elementos que foram reconhecidos pela query
        """        
        self.logging.info("read_operacoes",extra=locals())
        tmp=self.read_data_sqlite("operacoes",filtro=filtro,query=query)
        self.logging.debug(tmp)
        retorno=[]
        for i in tmp:
            tmp2=self.process_data_generated(data=i,with_id=True,filtro=filtro,tipo_adicional=tipo_adicional)
            try:
                tmp2.pop("id")
            except:
                pass
            retorno.append(tmp2)
        return retorno

    def get_operacao_by_id(self,id:int)->dict:
        """pesquisa um elemento na tabela de operações pelo id

        Args:
            id (int): id que será pesquisado

        Returns:
            dict: elemento retornado
        """        
        retornos=self.read_operacoes(query={"id":id})
        for i in retornos:
            return i

    def process_data_generated(self,data:list,tipo_adicional:str="dict",with_id:bool=False,filtro:Union[str,dict]="*") -> dict:
        """processa o dado lido do sqlite para um formato de dict usavel 

        Args:
            text (str): texto gerado pelo comando de leitura do sqlite

        Returns:
            dict: dict usavel e processado do que foi lido do sqlite
        """        
        self.logging.info("process_data_generated",extra=locals())
        etapa1_operacoes=data
        self.logging.debug(etapa1_operacoes)
        output={}
        if filtro == "*":
            if with_id:
                output["id"]=etapa1_operacoes[0]
                output["tipoOperacao"]=etapa1_operacoes[1]
                output["nomeBD"]=etapa1_operacoes[2]
                output["idNoBD"]=etapa1_operacoes[3]
                output["adicionais"]=etapa1_operacoes[4]
                output["dados"]=etapa1_operacoes[5]
            else:
                output["tipoOperacao"]=etapa1_operacoes[0]
                output["nomeBD"]=etapa1_operacoes[1]
                output["idNoBD"]=etapa1_operacoes[2]
                output["adicionais"]=etapa1_operacoes[3]
                output["dados"]=etapa1_operacoes[4]
        elif type(filtro)==type(""):
            output[filtro]=etapa1_operacoes[0]
        elif type(filtro)==type({}):
            lista=list(filtro.keys())
            for i in range(len(lista)):
                output[lista[i]]=etapa1_operacoes[i][0]
        self.logging.debug(output)
        if tipo_adicional == "none_dados":
            return output
        elif tipo_adicional == "none":
            output["dados"]=self.string_to_dict(output["dados"])
            return output
        elif tipo_adicional == "dict":
            adicionais=self.string_to_dict(output["adicionais"])
        elif tipo_adicional == "dict_array":
            pattern_adicionais=r"\[\{(.*)\}\]"
            adicionais=[]
            for dado in re.findall(pattern_adicionais, output["adicionais"])[0].split("},{"):
                adicionais.append(self.string_to_dict(dado,patter_externo=r"(.*)"))
        elif tipo_adicional == "array":
            adicionais=self.string_to_dict(output["adicionais"],is_dict=False)
        
        self.logging.debug(adicionais)
        output["adicionais"]=adicionais
        output["dados"]=self.string_to_dict(output["dados"])
        return output
    
    def string_to_dict(self,text:str) -> dict:
        """converte string legivel em dict usavel a partir de um string

        Args:
            text (str): texto de entrada
            patter_externo (regexp, optional): expressão regular usado para processar os dados inseridos,para separar a parte mais externa do string. Defaults to r"\{(.*)}".
            pattern_interno (regexp, optional): expressão regular usado para processar os dados inseridos,para processar a parte mais interna do string. Defaults to r"([^:]*)\:(.*)".
            external_header_list (list, optional): header do dict final. Defaults to [].
            is_dict (boolean): defini se o retorno é um dictionary ou um array
        Returns:
            (dict,list): dictionary ou array com o conteudo usavel do retorno de uma consulta no sqlite
        """
        self.logging.info("string_to_dict",extra=locals())
        if text == None:
            return {}
        text=text.replace("'",'"')
        text=text.replace("None","null")
        text=text.replace("True","true")
        text=text.replace("False","false")
        return json.loads(text)
        