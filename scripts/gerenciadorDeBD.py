import psycopg2, mysql.connector, sys,traceback,json
from loggingSystem import loggingSystem
from os import DirEntry
from tratamentoErro import *
from interacaoSqlite import InteracaoSqlite
class GerenciadorDeBD:
    
    def __init__(self,host:str,user:str,password:str,database:str,port:int,tipo:int=0,sql_file_pattern:str="./sqlPattern.sql", log_file="./gerenciadorBD.log",level:int=10,logging_pattern='%(name)s - %(levelname)s - %(message)s',logstash_data:dict={},json_path:DirEntry="scripts/padroes.json"):
        try:
            if tipo==0:#0=mariadb,1=postgres
                self.mydb = mysql.connector.connect(
                        host=host,
                        user=user,
                        password=password,
                        database=database,
                        port=port
                        )
                self.type="mysql"
            elif tipo==1:
                self.mydb = psycopg2.connect(
                        host=host,
                        user=user,
                        password=password,
                        database=database,
                        port=port
                        )
                self.type="postgres"
            else:
                raise ValorInvalido(campo="tipo",valor_possivel="0 para mariadb,1 para postgres")
            self.cursor=self.mydb.cursor()
            
            self.json_loaded=json.loads(open(json_path,"r").read())
            self.logging = loggingSystem(name="conexao db",arquivo=log_file,level=level,formato=logging_pattern,logstash_data=logstash_data)
            self.sql_file_pattern=sql_file_pattern
        except ValorInvalido:
            traceback.print_exc()

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
        try:
            command=self.generate_lib_insertion_from_data(data=data,sql=True)
        except ValorInvalido as e :
            self.logging.exception(e)
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])
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
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])
            return None

    def gernerate_SQL_from_sqlite_range(self,amount:int)->list:
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
                if data["tipoOperacao"] ==1 and self.json_loaded[data["nomeBD"]][i][0]=="id":
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
        except ValorInvalido as e :
            self.logging.exception(e)
        except TypeError as e:
            self.logging.exception(e)
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])            

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
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])
            return None

    def gernerate_lib_insertion_from_sqlite_range(self,amount:int,sqlite_db:DirEntry,sql:bool=False)->list:
        """gera um raio de elementos,a partir do primeiro até o informado,de comandos sql a partir do sqlite

        Args:
            amount (int): total de elementos que serão gerados a partir do sqlite

        Returns:
            list: comandos sql gerados a partir do sqlite
        """
        retorno=[]
        for i in range(1,amount+1):
            elemento=self.generate_lib_insertion_from_sqlite_id(i,sql=sql,sqlite_db=sqlite_db)
            if elemento == None:
                break
            else:
                retorno.append(elemento)

        return retorno

#operações

    def execute_sql_file(self,file:DirEntry):
        if self.type == "mysql":
            fd = open(file, 'r')
            sqlFile = fd.read()
            fd.close()
            sqlCommands = sqlFile.split(';')

            for command in sqlCommands:
                try:
                    if command.strip() != '':
                        self.cursor.execute(command)
                except IOError as msg:
                    self.logging.error("Command skipped: ", msg)
        elif self.type == "postgres":
            self.cursor.execute(open("containers_build/postgres default exemple.sql","r").read())
        self.mydb.commit()
    
    def reset_database(self):
        self.execute_sql_file(self.sql_file_pattern)

    def execute_operation_array_no_return(self,operations:list):
        for i in operations:
            self.logging.debug(i)
            if self.type=="mysql":
                try:
                    self.cursor.execute(i)
                    try:
                        self.mydb.commit()
                    except:
                        try:
                            self.cursor.fetchall()
                        except:
                            pass
                except mysql.connector.Error as e:
                    self.logging.exception(e)
            elif self.type=="postgres":
                try:
                    self.cursor.execute(i)
                    try:
                        self.mydb.commit()
                    except:
                        try:
                            self.cursor.fetchall()
                        except:
                            pass
                except psycopg2.errors.ForeignKeyViolation as e:
                    self.logging.exception(e)
                except psycopg2.OperationalError as e:
                    #self.cursor.execute("ROLLBACK")
                    #self.mydb.commit()
                    self.logging.exception(e)
                except psycopg2.errors.InFailedSqlTransaction as e :
                    self.mydb.rollback()
                    self.logging.exception(e)
                #except:
                 #   self.logging.error("Unexpected error:", sys.exc_info()[0])

    def execute_operation_array_return(self,operations:list)->list:
        retorno=[]
        for i in operations:
            self.logging.debug(i)
            self.cursor.execute(i)
            try:
                retorno.append(self.cursor.fetchall())
            except:
                retorno.append([])

    def execute_operation_from_sqlite_no_return(self,amount:int,sqlite_file:DirEntry):
        self.execute_operation_array_no_return(self.gernerate_lib_insertion_from_sqlite_range(amount=amount,sqlite_db=sqlite_file,sql=True))

    def execute_operation_from_sqlite_return(self,amount:int,sqlite_file:DirEntry):
        return self.execute_operation_array_return(self.gernerate_lib_insertion_from_sqlite_range(amount=amount,sqlite_db=sqlite_file,sql=True))

    def execute_operation_from_sqlite_no_return_with_id(self,id:int,sqlite_file:DirEntry):
        self.execute_operation_array_no_return([self.generate_lib_insertion_from_sqlite_id(id=id,sqlite_db=sqlite_file,sql=True)])
