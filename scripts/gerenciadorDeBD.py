import psycopg2, mysql.connector, traceback,json
from loggingSystem import LoggingSystem
from os import DirEntry
from tratamentoErro import ValorInvalido
from interacaoSqlite import InteracaoSqlite
import time
from typing import List,Union
from psycopg2 import errors as psyErro
from mysql.connector import errors as mysqlErro
class GerenciadorDeBD:
    
    def __init__(self,host:str,user:str,password:str,database:str,port:int,tipo:int=0,sql_file_pattern:str="./sqlPattern.sql",autocommit:bool=True, log_file="./gerenciadorBD.log",level:int=10,logging_pattern='%(name)s - %(levelname)s - %(message)s',logstash_data:dict={},json_path:DirEntry="scripts/padroes.json"):
        try:
            self.host=host
            self.user=user
            self.password=password
            self.database=database
            self.port=port
            self.stack_overflow_max=5
            self.autocommit=autocommit
            self.logging = LoggingSystem(name="conexao db",arquivo=log_file,level=level,formato=logging_pattern,logstash_data=logstash_data)
            self.tipo= tipo
            self.mydb,self.tipo=self.create_connector(tipo=tipo,user=user,password= password,database=database,autocommit=autocommit)
            retries=0
            while self.mydb == None and retries<self.stack_overflow_max:
                try:
                    self.mydb,self.tipo=self.create_connector(tipo=tipo,user=user,password= password,database=database,autocommit=autocommit)
                    retries+=1
                except:
                    pass
                if self.mydb == None:
                    time.sleep(5)
            if self.mydb == None:
                raise ValorInvalido(valor_inserido=str(locals().values()),campo="algum parametro de conexão é inválido")
            self.cursor=self.mydb.cursor()
            self.json_loaded=json.loads(open(json_path,"r").read())
            self.sql_file_pattern=sql_file_pattern
            
        except ValorInvalido as e:
            traceback.print_exc()
            try:
                self.logging.error(e)
            except:
                pass

    def __del__(self):
        try:
            self.cursor.close()
        except:
            pass
        try:
            self.mydb.close()
        except:
            pass

#relacionado com a geração do sql final
    def generate_SQL_command_from_data(self,data:dict):
        '''
                tipo de operação:int #1:insersão,2:leitura,3:busca,4:edição,5:deleção
                bd:string # banco de dados en que será inserido
                os dados a baixo estão definidos para uma insercao:
                    associações: #text  IGNORADO
                    outros dados do bd: #text
                    {
                        nome da variavel:conteudo da variavel #string:string  #nome do tipo da variavel do bd e o conteudo dela
                    }

                os dados para uma leitura completa apenas são os basicos,todo o restante será ignorado,quando uma leitura é feita 
                os dados a baixo estão definidos para uma busca:
                    associações: #text     IGNORADO
                    outros dados do bd: #text
                    {
                        nome da variavel:conteudo da variavel #string:string  #nome da coluna e valor a ser pesquisado,podem ser multiplos
                    }
                os dados a baixo são associados com uma busca fitrada
                    associações: #text    
                    [{variavelRetornada:variavel}]  # inserir o termo"variavelRetornada"(nome pode ser alterado,apenas serve para referencia,mas deve ser editado no codigo também) seguido pelo nome da coluna que deseja realmente retornar,cada variavel deve ser colocada em um dictionary com apenas ela,devido a necessidade para compatibilidade com todos os outros comandos
                    outros dados do bd: #text
                    {
                        nome da variavel:conteudo da variavel #string:string  #nome da coluna e valor a ser pesquisado,podem ser multiplos
                    }
            '''
        self.logging.info("generate_SQL_command_from_data",extra=locals())
        command=""
        try:
            command=self.generate_lib_insertion_from_data(data=data,sql=True)
        except ValorInvalido as e :
            self.logging.exception(e)
        except BaseException as e:
            self.logging.error("Unexpected error:", e)
        finally:
            return command

    def generate_SQL_from_sqlite_id(self,id:int)->str:
        """retorna um comando sql a partir de um id de operação do sqlite

        Args:
            id (int): id de operação do sqlite

        Raises:
            ValorInvalido: se o valor de id inserido for maior que o total de operações cadastradas no sqlite

        Returns:
            str: comando sql gerado a partir do elemento cadastrado no sqlite
        """        
        max_id=self.processamento_sqlite.total_operacoes()
        try:
            if id>max_id:
                raise ValorInvalido(valor_inserido=id,campo="id",valor_possivel="não pode ser maior que "+max_id)
            return self.generate_SQL_command_from_data(data=self.processamento_sqlite.get_operacao_by_id(id))

        except ValorInvalido as e:
            self.logging.exception(e)
            return None
        except BaseException as e:
            self.logging.error("Unexpected error:", e)
            return None

    def gernerate_SQL_from_sqlite_range(self,amount:int)->List[str]:
        """gera um raio de elementos,a partir do primeiro até o informado,de comandos sql a partir do sqlite

        Args:
            amount (int): total de elementos que serão gerados a partir do sqlite

        Returns:
            list: comandos sql gerados a partir do sqlite
        """
        retorno=[]
        for i in range(1,amount+1):
            elemento=self.generate_SQL_from_sqlite_id(i)
            if elemento == None:
                break
            else:
                retorno.append(elemento)
        return retorno

#relacionado com execução da lib python

    def generate_lib_insertion_from_data(self,data:dict,sql:bool=False,lib:bool=False):
        '''
                tipo de operação:int #1:insersão,2:leitura,3:busca,4:edição,5:deleção
                bd:string # banco de dados en que será inserido
                os dados a baixo estão definidos para uma insercao:
                    associações: #text  IGNORADO
                    outros dados do bd: #text
                    {
                        nome da variavel:conteudo da variavel #string:string  #nome do tipo da variavel do bd e o conteudo dela
                    }

                os dados para uma leitura completa apenas são os basicos,todo o restante será ignorado,quando uma leitura é feita 
                os dados a baixo estão definidos para uma busca:
                    associações: #text     IGNORADO
                    outros dados do bd: #text
                    {
                        nome da variavel:conteudo da variavel #string:string  #nome da coluna e valor a ser pesquisado,podem ser multiplos
                    }
                os dados a baixo são associados com uma busca fitrada
                    associações: #text    
                    [{variavelRetornada:variavel}]  # inserir o termo"variavelRetornada"(nome pode ser alterado,apenas serve para referencia,mas deve ser editado no codigo também) seguido pelo nome da coluna que deseja realmente retornar,cada variavel deve ser colocada em um dictionary com apenas ela,devido a necessidade para compatibilidade com todos os outros comandos
                    outros dados do bd: #text
                    {
                        nome da variavel:conteudo da variavel #string:string  #nome da coluna e valor a ser pesquisado,podem ser multiplos
                    }
            '''
        self.logging.info("generate_SQL_command_from_data",extra=locals())
        try:
            retorno={"dados_colunas":[],"dados_valores":[],"operacao":0,"adicionais_colunas":[],"adicionais_valores":[],"nomeBD":""}
            retorno["operacao"]=data["tipoOperacao"]
            retorno["nomeBD"]=data["nomeBD"]
            for i in data["dados"].keys():
                if data["tipoOperacao"] == 1 and self.json_loaded[data["nomeBD"]][i][0]=="id":
                    pass
                elif  type(data["dados"][i])==type(None):
                    pass
                else:
                    retorno["dados_colunas"].append(i)
                    retorno["dados_valores"].append(data["dados"][i])
            
            if retorno["operacao"] in[3,4,6] :
                for i in data["adicionais"]:
                    retorno["adicionais_colunas"].append(i)
            else:
                for i in data["adicionais"].keys():
                    if retorno["operacao"] ==5 and self.json_loaded[data["nomeBD"]][i][0]=="id":
                        pass
                    else:
                        retorno["adicionais_colunas"].append(i)
                        retorno["adicionais_valores"].append(data["adicionais"][i])
            
            if lib or sql:
                tmp=[0,0]#transformar no metodo base de geração de elementos generate_lib_insertion_from_data,passar parametro para seleção de qual usar
                command=""
                if retorno["operacao"]==1:#insercao
                    command+="INSERT INTO "
                elif retorno["operacao"] in [2,3]:#leitura completa,#busca
                    command+="SELECT * FROM "
                elif retorno["operacao"] == 4:#busca filtrada
                    command+="SELECT "
                    for i in retorno['adicionais_colunas']:
                        command+= "%s"
                        if i != retorno['adicionais_colunas'][-1]:
                            command+= ","
                    command+=" FROM "
                elif retorno["operacao"]==5:#edicao
                    command+="UPDATE "
                elif retorno["operacao"]==6:#delecao
                    command+="DELETE FROM "

                command+=str(retorno["nomeBD"])

                if retorno["operacao"] == 1:#insercao
                    command+=" ("
                    for coluna in retorno["dados_colunas"]:
                            command+="%s"
                            if coluna != retorno["dados_colunas"][-1]:
                                command+=","
                    command+=") VALUES ("
                    for coluna in retorno["dados_valores"]:
                        if type(coluna)==type("") or type(coluna)==type([]):
                            command+="\'%s\'"
                        else:
                            command+="%s"
                        if coluna != retorno["dados_valores"][-1]:
                            command+=","
                    command+=")"
                elif retorno["operacao"] == 5:#edicao
                    command+=" SET "
                    for coluna in retorno["dados_colunas"]:
                        if type(data["dados"][coluna])==type(""):
                            command+="%s = \'%s\'"
                        else:
                            command+="%s = %s"
                        if coluna != retorno["dados_colunas"][-1]:
                            command+=" , "
                    command+=" WHERE "
                    for coluna in retorno["adicionais_colunas"]:
                        if type(data["adicionais"][coluna])==type("") or type(data["adicionais"][coluna])==type([]):
                            command+="%s = \'%s\'"
                        else:
                            command+="%s = %s"
                        if coluna != retorno["adicionais_colunas"][-1]:
                            command+=" AND "
                if retorno["operacao"] in [3,4,6]:# busca #busca filtrada #remocao
                    command+=" WHERE "
                    for coluna in retorno["dados_colunas"]:
                        if type(data["dados"][coluna])==type("") or type(data["dados"][coluna])==type([]):
                            command+="%s = \'%s\'"
                        else:
                            command+="%s = %s"
                        if coluna != retorno["dados_colunas"][-1]:
                            command+=" AND "
                command+="; "
                tmp[0]=command
                tmp[1]=[]
                if retorno["operacao"] in [1]:
                    for i in retorno["dados_colunas"]:
                        tmp[1].append(i)
                    for i in retorno["dados_valores"]:
                        if type(i)==type([]):
                            tmp[1].append(str(i).replace("[","").replace("]","").replace("'",""))
                        else:
                            tmp[1].append(i)
                elif retorno["operacao"] == 5:
                    for i in range(0, len(retorno["dados_colunas"])):
                        tmp[1].append(retorno["dados_colunas"][i])
                        if type(retorno["dados_valores"][i])==type([]):
                            vetor_processado=""
                            for i in retorno["dados_valores"][i]:
                                vetor_processado+=str(i)
                            tmp[1].append(vetor_processado)
                        else:
                            tmp[1].append(retorno["dados_valores"][i])
                if retorno["operacao"] in [1,5]:#separar o 1 e 5 ,funcionam obrigatoriamente difwerente
                    for i in range(0, len(retorno["adicionais_colunas"])):
                        tmp[1].append(retorno["adicionais_colunas"][i])
                        if type(retorno["adicionais_valores"][i])==type([]):
                            tmp[1].append(str(retorno["adicionais_valores"][i]).replace("[","").replace("]",""))
                        else:
                            tmp[1].append(retorno["adicionais_valores"][i])
                elif retorno["operacao"] in [3,4,6]:#separar o 1 e 5 ,funcionam obrigatoriamente difwerente
                    for i in range(0, len(retorno["adicionais_colunas"])):
                        tmp[1].append(retorno["adicionais_colunas"][i])
                    for i in range(len(retorno["dados_colunas"])):
                        tmp[1].append(retorno["dados_colunas"][i])
                        if type(retorno["dados_valores"][i])==type([]):
                            vetor_processado=""
                            for j in retorno["dados_valores"][i]:
                                vetor_processado+=str(j)
                            tmp[1].append(vetor_processado)
                        else:
                            tmp[1].append(retorno["dados_valores"][i])
                retorno=tmp
                if sql:
                    newtmp=str(tmp[0]).replace('%s',"{}")
                    retorno = newtmp.format(*tmp[1])
                else:
                    retorno[0]=retorno[0].replace("\'","")
            return retorno
        except AttributeError as e:
            self.logging.exception(e)
        except ValorInvalido as e :
            self.logging.exception(e)
        except TypeError as e:
            self.logging.exception(e)
        except BaseException as e:
            self.logging.error("Unexpected error:", e)

    def generate_lib_insertion_from_sqlite_id(self,id:int,sqlite_db:DirEntry,sql:bool=False)->str:
        """retorna um comando sql a partir de um id de operação do sqlite

        Args:
            id (int): id de operação do sqlite

        Raises:
            ValorInvalido: se o valor de id inserido for maior que o total de operações cadastradas no sqlite

        Returns:
            str: comando sql gerado a partir do elemento cadastrado no sqlite
        """    
        processamento_sqlite=InteracaoSqlite(sqlite_db=sqlite_db,log_file=self.logging.log_file,logging_pattern=self.logging.logging_pattern,level=self.logging.level,logstash_data=self.logging.logstash_data)    
        max_id=processamento_sqlite.total_operacoes()
        try:
            if id>max_id:
                raise ValorInvalido(valor_inserido=str(id),campo="id",valor_possivel="não pode ser maior que "+str(max_id))
            return self.generate_lib_insertion_from_data(data=processamento_sqlite.get_operacao_by_id(id),lib=True,sql=sql)
        except ValorInvalido as e:
            self.logging.exception(e)
            return None
        except BaseException as e:
            self.logging.error("Unexpected error:", e)
            return None

    def gernerate_lib_insertion_from_sqlite_range(self,amount:int,sqlite_db:DirEntry,initial:int=1,sql:bool=False)->list:
        """gera um raio de elementos,a partir do primeiro até o informado,de comandos sql a partir do sqlite

        Args:
            amount (int): total de elementos que serão gerados a partir do sqlite

        Returns:
            list: comandos sql gerados a partir do sqlite
        """
        retorno=[]
        for i in range(initial,amount+1):
            elemento=self.generate_lib_insertion_from_sqlite_id(i,sql=sql,sqlite_db=sqlite_db)
            if elemento == None:
                break
            else:
                retorno.append(elemento)

        return retorno

#operações

    def execute_sql_file(self,arquivo:DirEntry,connector=None):
        cursor,mydb=self.process_connector(connector)
        try:
            if self.tipo == "mysql":
                fd = open(arquivo, 'r')
                sqlFile = fd.read()
                fd.close()
                sqlCommands = sqlFile.split(';')
                for command in sqlCommands:
                    try:
                        if command.strip() != '':
                            cursor.execute(command)
                    except IOError as msg:
                        self.logging.error("Command skipped: ", msg)
            elif self.tipo == "postgres":
                cursor.execute(open(arquivo,"r").read())
            if self.autocommit==False:
                mydb.commit()
        except psycopg2.InterfaceError as e:
            self.execute_sql_file(arquivo=arquivo,connector=self.mydb)
        except mysqlErro.OperationalError:
            self.execute_sql_file(arquivo=arquivo,connector=self.mydb)
        except BaseException as e:
            raise
        try:
            cursor.close()
        except:
                pass
    
    def reset_database(self):
        self.execute_sql_file(self.sql_file_pattern)

    def process_connector(self,connector=None):
        cursor=""
        mydb=""
        try:
            if connector ==None:
                    mydb=self.mydb
                    cursor=self.cursor
                    if cursor == None:
                        raise BaseException
            else:
                mydb=connector
                cursor=mydb.cursor()
        except AttributeError as e:
            time.sleep(0.1)
            self.mydb,tmp=self.create_connector(tipo=self.tipo,user=self.user,password= self.password,database=self.database,autocommit=self.autocommit)
            
            return self.process_connector(connector=connector)
        except BaseException as e:
                self.mydb,tmp=self.create_connector(tipo=self.tipo,user=self.user,password= self.password,database=self.database,autocommit=self.autocommit)
                try:
                    mydb=self.mydb
                    self.cursor=self.mydb.cursor()
                    cursor=self.cursor
                    self.logging.exception(e)
                except AttributeError as e:
                    try:
                        chamadas=LoggingSystem.full_inspect_caller() 
                        if chamadas.count(chamadas[0])>self.stack_overflow_max: 
                            return None
                    except IndexError as e:
                        pass
                    except:
                        raise
                    self.process_connector(connector)
                except BaseException as e:
                    #traceback.print_exc()
                    raise
        try:
            if cursor == None:
            # if type(cursor) != mysql.connector.cursor_cext.CMySQLCursor or type(cursor) != psycopg2.extensions.cursor or type(cursor) != psycopg2.cursor:
                print(cursor)
                try:
                    chamadas=LoggingSystem.full_inspect_caller() 
                    if chamadas.count(chamadas[0])>self.stack_overflow_max: 
                        return None
                except IndexError as e:
                    pass
                except:
                    raise
                self.process_connector(connector)
            else:
                return (cursor,mydb)
        except UnboundLocalError as e:
            try:
                chamadas=LoggingSystem.full_inspect_caller() 
                if chamadas.count(chamadas[0])>self.stack_overflow_max: 
                    return None
            except IndexError as e:
                pass
            except:
                raise
            self.process_connector(connector)

    def create_connector(self,tipo:int,user:str,password:str,database:str=None,autocommit:bool=False):
        try:
            if database!=None:
                if tipo==0 or tipo=="mysql":#0=mariadb,1=postgres
                    mydb = mysql.connector.connect(
                            host=self.host,
                            user=user,
                            password=password,
                            database=database,
                            port=self.port
                            )
                    tipo="mysql"
                    mydb.autocommit=autocommit
                elif tipo==1 or tipo=="postgres":
                    mydb = psycopg2.connect(
                            host=self.host,
                            user=user,
                            password=password,
                            database=database,
                            port=self.port
                            )
                    tipo="postgres"
                    mydb.autocommit=autocommit
                else:
                    raise ValorInvalido(campo="tipo",valor_possivel="0 para mariadb,1 para postgres")
            else:
                if tipo==0 or tipo=="mysql":#0=mariadb,1=postgres
                    mydb = mysql.connector.connect(
                            host=self.host,
                            user=user,
                            password=password,
                            port=self.port
                            )
                    tipo="mysql"
                elif tipo==1 or tipo == "postgres":
                    mydb = psycopg2.connect(
                            host=self.host,
                            user=user,
                            password=password,
                            port=self.port
                            )
                    tipo="postgres"
                else:
                    raise ValorInvalido(campo="tipo",valor_possivel="0 para mariadb,1 para postgres")
            return (mydb , tipo)
        except mysqlErro.ProgrammingError as e:
            self.logging.error(e)
            if e.errno == 1045:
                erro="acesso negado"
            return (None,tipo)
        except psycopg2.OperationalError as e:
            self.logging.error(e)
            if "Connection refused" in e.args[0]:
                try:
                    chamadas=LoggingSystem.full_inspect_caller() 
                    if chamadas.count(chamadas[0])>self.stack_overflow_max: 
                        return (None,tipo)
                except IndexError as e:
                    pass
                except:
                    raise
                self.create_connector(tipo=tipo,user=user,password=password,database=database,autocommit=autocommit)
            else:
                return (None,tipo)
        except mysqlErro.DatabaseError as e:
            (2003, "2003 (HY000): Can't connect to MySQL server on '192.168.0.10:3306' (111)", 'HY000')
            if e.errno == 2003:
                pass
            self.logging.error(e)
        except BaseException as e:
            #traceback.print_exc()
            return self.create_connector(tipo=tipo,user=user,password=password,database=database,autocommit=autocommit)

    def creat_user(self,user:str,password:str,database:str,root_pass:str=""):
        try:
            if self.tipo==0 or self.tipo=="mysql":
                operation=[
                "CREATE USER IF NOT EXISTS `{user}`@`%` IDENTIFIED BY '{password}';".format(user=user,password=password),
                "GRANT ALL ON `{database}`.* to `{user}`@`%` IDENTIFIED BY '{password}';" .format(database=database,user=user,password=password)
                ]
                for tabela in self.json_loaded.keys():
                    operation.append("GRANT ALL ON `{database}`.`{tabela}` to `{user}`@`%` IDENTIFIED BY '{password}';" .format(database=database,tabela=tabela,user=user,password=password))
                if root_pass=="":
                    raise ValorInvalido(campo="root_pass",valor_inserido=root_pass)
                con,tipo=self.create_connector(tipo=self.tipo, user="root",password=root_pass)
                self.execute_operation_array_no_return(operation,con)
                # self.execute_operation_array_no_return(operation,self.mydb)
            elif self.tipo==1 or self.tipo == "postgres":
                operation=[
                "DROP ROLE IF EXISTS {user};".format(user=user),
                "CREATE USER {user} WITH PASSWORD '{password}';".format(user=user,password=password),
                'GRANT ALL ON ALL SEQUENCES in SCHEMA public TO {user};' .format(user=user)
                ]
                for tabela in self.json_loaded.keys():
                    operation.append('GRANT ALL ON TABLE public."{tabela}" to {user};' .format(database=database,tabela=tabela,user=user))
                # with open("containers_build/postgres user creation.sql","a") as arquivo:
                #     for i in operation:
                #         arquivo.write(i)
                #         arquivo.write("\n")
                self.execute_operation_array_no_return(operation,self.mydb)
        except:
            pass

    def delete_user(self,user:str,password:str,database:str,root_pass:str=""):
        try:
            if self.tipo==0 or self.tipo=="mysql":
                operation=[
                "DROP USER IF EXISTS `{user}`@`%` ;".format(user=user,password=password)
                ]
                if root_pass=="":
                    raise ValorInvalido(campo="root_pass",valor_inserido=root_pass)
                con,tipo=self.create_connector(tipo=self.tipo, user="root",password=root_pass)
                self.execute_operation_array_no_return(operation,con)
                # self.execute_operation_array_no_return(operation,self.mydb)
            elif self.tipo==1 or self.tipo == "postgres":
                operation=[
                "DROP ROLE IF EXISTS {user};".format(user=user)
                ]
                # with open("containers_build/postgres user creation.sql","a") as arquivo:
                #     for i in operation:
                #         arquivo.write(i)
                #         arquivo.write("\n")
                self.execute_operation_array_no_return(operation,self.mydb)
        except:
            pass

    def execute_operation_array_no_return(self,operations:list,connector=None):
        cursor,mydb=self.process_connector(connector)
        error=0
        for i in range(len(operations)):
            self.logging.debug(operations[i])
            if self.tipo=="mysql":
                try:
                    cursor.execute(operations[i])
                    try:
                        if self.autocommit==False:
                            mydb.commit()
                    except:
                        try:
                            cursor.fetchall()
                        except:
                            pass
                except mysql.connector.Error as e:
                    self.logging.exception(e)
            elif self.tipo=="postgres":
                try:
                    cursor.execute(operations[i])
                    try:
                        if self.autocommit==False:
                            mydb.commit()
                    except BaseException as e:
                        try:
                            cursor.fetchall()
                        except BaseException as e:
                            pass
                except psycopg2.InterfaceError as e:
                    cursor,mydb=self.process_connector(connector=self.mydb)
                except psyErro.InFailedSqlTransaction as e :
                    try:
                        mydb.rollback()
                    except BaseException :
                        pass
                    if error<self.stack_overflow_max:#se rolar rollback ele vai tentar dnv,limite de 5 vezes
                        i-=1
                        error+=1
                        time.sleep(0.01)
                    else:
                        #print(self.user)
                        error=0
                    self.logging.exception(e)
                except psycopg2.DatabaseError as e:
                    self.logging.exception(e)
                except psyErro.ForeignKeyViolation as e:
                    # try:
                    #     mydb.rollback()
                    # except BaseException :
                    #     pass
                    # if error<self.stack_overflow_max:#se rolar rollback ele vai tentar dnv,limite de 5 vezes
                    #     i-=1
                    #     error+=1
                    #     time.sleep(0.001)
                    # else:
                    #     #print(self.user)
                    #     error=0
                    if e.pgcode == "23503":
                        test="operação sem retorno,essa pesquisa ou update não encontra nada no banco de dados existente"
                        pass
                    self.logging.exception(e)
                except psyErro.DuplicateObject as e:
                    pass
                except psyErro.InsufficientPrivilege as e:
                    self.logging.exception(e)
                except psyErro.OperationalError as e:
                    self.logging.exception(e)
                except BaseException as e:
                    # self.logging.error("Unexpected error:", e)
                    raise
        # try:
        #     cursor.close()
        # except:
        #         pass

    def execute_operation_array_return(self,operations:list)-> List[str]:
        retorno=[]
        for i in operations:
            self.logging.debug(i)
            self.cursor.execute(i)
            try:
                retorno.append(self.cursor.fetchall())
            except:
                retorno.append([])
        return retorno

    def execute_operation_from_sqlite_no_return(self,amount:int,sqlite_file:DirEntry,initial:int=1):
        self.execute_operation_array_no_return(self.gernerate_lib_insertion_from_sqlite_range(amount=amount,sqlite_db=sqlite_file,sql=True,initial=initial))

    def execute_operation_from_sqlite_return(self,amount:int,sqlite_file:DirEntry,initial:int=1):
        return self.execute_operation_array_return(self.gernerate_lib_insertion_from_sqlite_range(amount=amount,sqlite_db=sqlite_file,sql=True,initial=initial))

    def execute_operation_from_sqlite_no_return_with_id(self,id:int,sqlite_file:DirEntry):
        self.execute_operation_array_no_return([self.generate_lib_insertion_from_sqlite_id(id=id,sqlite_db=sqlite_file,sql=True)])

#gerencia
    def get_status(self):
        if self.tipo=="mysql":
            # consulta_queries="""SHOW GLOBAL STATUS
            #     Map keys: [Com_select, Com_insert, Com_update, Com_delete]
            #     Map labels: [Select, Insert, Update, Delete]"""
            # consulta_sessions="""SELECT Command,count(*) from information_schema.PROCESSLIST GROUP BY Command"""
            return self.mydb.cmd_statistics()
        elif self.tipo == "postgre":
            # consulta_queries="""SELECT
            #     (SELECT sum(xact_commit) + sum(xact_rollback) AS "Total" FROM pg_stat_database),
            #     (SELECT sum(xact_commit) AS "Commit" FROM pg_stat_database),
            #     (SELECT sum(xact_rollback) AS "Rollback" FROM pg_stat_database)"""
            # consulta_sessions="""SELECT
            # (SELECT count(*) AS "Active" FROM pg_catalog.pg_stat_activity sa WHERE state='active'),
            # (SELECT count(*) AS "Idle" FROM pg_catalog.pg_stat_activity sa WHERE state='idle'),
            # (SELECT count(*) AS "Total" FROM pg_catalog.pg_stat_activity sa WHERE state IS NOT NULL)"""
            return None