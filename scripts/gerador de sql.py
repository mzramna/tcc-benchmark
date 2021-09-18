from loggingSystem import loggingSystem
from faker import Faker
from random import random,uniform
from sqlite3 import Error as sqliteError
import sys,re,pprint,sqlite3,json
class GeradorDeSql:
#tratamento de erro
    class ValorInvalido(Exception):
        def __init__(self, valor_inserido="",mensagem_principal_replace=False,mensage_adicional="",campo="",valor_possivel="") :
            self.valor_inserido=str(valor_inserido)
            self.valor_possivel=valor_possivel
            self.mensage_adicional=mensage_adicional
            self.mensagem_principal_replace=mensagem_principal_replace
            self.campo=campo
            self.construir_mensagem()
            super().__init__(self.message)

        def listagem_valores_possiveis(self,valores_possiveis="",campo=""):
            if valores_possiveis !="":
                if  type("")==type(valores_possiveis):
                    self.message+=" o valor possivel "
                    if campo!="":
                        self.message+="no campo "+str(campo)+" "
                    self.message+="é "
                elif  type("")==type(valores_possiveis):
                    self.message+=" os valores possiveis "
                    if campo!="":
                        self.message+="no campo "+str(campo)+" "
                    self.message+="são "+str(valores_possiveis)
                return self.valores_possiveis(valores_possiveis)

        def valores_possiveis(self,valores_possiveis=""):
            retorno=""
            if type(valores_possiveis)==type([]) or type(valores_possiveis)==type({}):
                for valor in valores_possiveis:
                    if type(valor)==type(""):
                        retorno+=valor
                    else:
                        retorno+=str(valor) 
                    if valor == valores_possiveis[-2]:
                        retorno+=" ou "
                    elif valor not in valores_possiveis[-2:]:
                        retorno+=","
            elif type(valores_possiveis)==type(""):
                    retorno+=valores_possiveis
            else:
                retorno+=str(valores_possiveis)
            return retorno

        def construir_mensagem(self,mensage_adicional=""):
            if not self.mensagem_principal_replace:
                self.message="um valor inserido foi inserido de forma errada\no valor "
                self.message+=self.valor_inserido
                " é invalido ou foi inserido de forma errada"
                if self.campo!="":
                    self.message+=" no campo "
                    self.message+=self.campo
                self.message+="\n"
                self.message+=self.listagem_valores_possiveis(valores_possiveis=self.valor_possivel)
                self.message+="\n"
            if mensage_adicional == "":
                self.message+=str(self.mensage_adicional)
            else:
                self.message+=mensage_adicional

        def __str__(self):
            return self.message
    class TamanhoArrayErrado(ValorInvalido):
        def __init__(self,valor_inserido,valor_possivel="",campo="") :
            super(GeradorDeSql.ValorInvalido, self).__init__()
            self.valor_inserido=str(valor_inserido)
            self.valor_possivel=valor_possivel
            self.campo=campo
            self.valor_inserido=valor_inserido
            self.mensagem_principal_replace=True
            self.construir_mensagem()

        def valores_possiveis(self,valores_possiveis=""):
            print(valores_possiveis)
            retorno=super(GeradorDeSql.TamanhoArrayErrado, self).valores_possiveis(valores_possiveis)
            return retorno

        def listagem_valores_possiveis(self,valores_possiveis="",campo=""):
            return super(GeradorDeSql.TamanhoArrayErrado, self).listagem_valores_possiveis(valores_possiveis=valores_possiveis,campo=campo)

        def construir_mensagem(self):
            self.message="o tamanho para o array passado "
            if self.campo!="":
                if type(self.campo)==type(""):
                    self.message+="no campo "+self.campo+" "
                else:
                    self.message+="no campo "+str(self.campo)+" "
            self.message+="é invalido\n"
            if self.valor_possivel != "":
                self.message+=" o tamanho esperado era de "
                self.message+=self.valores_possiveis(self.valor_inserido)
                self.message+=" programa não pode continuar"
            
            #super(GeradorDeSql.TamanhoArrayErrado, self).construir_mensagem(self.message)

        def __str__(self):
            return self.message
    class TipoDeDadoIncompativel(ValorInvalido):
        def __init__(self,valor_inserido,tipo_possivel="",campo="") :
            super(GeradorDeSql.ValorInvalido, self).__init__()
            self.valor_inserido=valor_inserido
            self.tipo_possivel=tipo_possivel
            self.mensagem_principal_replace=True
            self.campo=campo
            self.construir_mensagem()

        def valores_possiveis(self,valores_possiveis=""):
            return super(GeradorDeSql.TipoDeDadoIncompativel, self).valores_possiveis(valores_possiveis=valores_possiveis)

        def listagem_valores_possiveis(self,valores_possiveis="",campo=""):
            return super(GeradorDeSql.TipoDeDadoIncompativel, self).listagem_valores_possiveis(valores_possiveis=valores_possiveis,campo=campo)

        def construir_mensagem(self):
            self.message="o tipo da variavel passada "
            if self.campo!="":
                if type(self.campo)==type(""):
                    self.message+="no campo "+self.campo+" "
                else:
                    self.message+="no campo "+str(self.campo)+" "
            self.message+="é invalido\n"
            if self.tipo_possivel != "":
                self.message+=" o tipo esperado era de "
                self.message+=self.valores_possiveis(self.tipo_possivel)
                self.message+=" programa não pode continuar"
                self.message+=" mas foi inserido"
                self.message+=str(self.valor_inserido)
            #self.construir_mensagem(self.message)

        def __str__(self):
            return self.message

#inicialização
    def __init__(self,sqlite_db="./initial_db.db",sql_file_pattern="./sqlitePattern.sql",loggin_name="geradorSQL", log_file="./geradorSQL.log",level=10):
        """
        classe para gerenciar arquivos csv
        :param loggin_name: nome do log que foi definido para a classe,altere apenas em caso seja necessário criar multiplas insstancias da função
        :param log_file: nome do arquivo de log que foi definido para a classe,altere apenas em caso seja necessário criar multiplas insstancias da função
        """
        self.logging = loggingSystem( arquivo=log_file,level=level)
        self.create_temporary_DB(local=sqlite_db,pattern=sql_file_pattern)
        self.conn = sqlite3.connect(sqlite_db)
    
    def create_temporary_DB(self,local,pattern):
        try:
            f = open(local, "a")
            f.write("")
            f.close()
            conn = sqlite3.connect(local)
            self.execute_sqlfile_sqlite(pattern,conn)
            conn.close()
            self.logging.debug("bd gerado com sucesso")
        except sqliteError as e:
            print("erro no sqlite")
            self.logging.exception(e)
        except :
            self.logging.error("Unexpected error:", str(sys.exc_info()[0]))

#relacionado com o processamento/geração de dados
    def create_data(self,table,pattern,select_country="random",id:int=-1):      
        '''
            pattern deve ser dado da seguinte forma:
            {
                "nome da coluna no bd":["tipo de dado gerado","dado adicional necessario"], #sempre desve ser passado como um array cada indice do dict,ja que alguns tipos de dados precisam mais do que apenas um dado para funcionar
                ...
            }


            o padrão de saida deve ser semelhante ao padrão do sqlite:
            {
            "tipoOperacao":1 #sempre será 1 já que apenas são gerados dados para inserção por padrão,caso seja necessário algo diferente,deve ser modificado em outra função
            "nomeBD": # nome do bd q será realizado a operação
            "associacoes": {} # vazio por padrão,caso seja necessário deversá ser tratado externamente em outra função
            "dados"{
                "nome da coluna":"dado", #nome da coluna deve ser passado no input e dado é gerado pela função
                ...
            }
            }
        '''
        self.logging.debug("create_data")
        try:
            self.logging.logger.getLogger('faker').setLevel(self.logging.logger.ERROR)
            if select_country=="random":
                fake = Faker()
                random_locale=fake.locale()
                self.logging.debug(random_locale)
                fake = Faker(random_locale)#define o faker para seguir o padrão de um pais expecifico selecionado aleatoriamente dentre os disponiveis
            else:
                fake = Faker(select_country)#se for definido então o codigo usado será o do pais inserido
            dados_gerados={"nomeBD":table,"tipoOperacao":1,"dados":{},"associacoes":[]}
            if id == -1:
                id=self.buscar_ultimo_id_cadastrado(table)+1
            dados_gerados["idNoBD"]=id
            for dado in pattern.keys():
                self.logging.debug(dado)
                if pattern[dado][0] == "nomeCompleto":
                    '''supoe-se que qualquer pessoa pode ter nascido em qq lugar e morar em qualquer outro lugar,nomes são dados pelo gerador de qualquer idioma,por isso nao foi definido um pais para a geracao'''
                    dados_gerados["dados"][dado]=fake.name()
                elif pattern[dado][0] == "primeiroNome":
                    dados_gerados["dados"][dado]=fake.first_name()
                elif pattern[dado][0] == "sobrenome":
                    dados_gerados["dados"][dado]=fake.last_name()
                elif pattern[dado][0] == "timestamp":
                    '''precisa obrigatoriamente de 1 parametro dizendo se vai ser tudo randomico ou se vai ter um intervalo,se tiver um intervalo devem ser passados mais 2 parametros,um inicial e um final , se o final for o valor "agora" então o valor final sera o timestamp de agora do sistema operacional

                    para gerar com mais precisão usar o 2 parametro como: "-30y",sendo: - > significando anterior , 30 > quanto tempo , y > escala de tempo(anos) ou usando o padrão Date("dia") onde o dia deve ser passado como "1999-02-02"

                    o 3 parametro deve ser passado como o 2,mas não se limita apenas ao token de tempo anterior,sendo possivel um intervalo do futuro
                    '''
                    if len(pattern[dado])<2:
                        raise self.TamanhoArrayErrado(valor_possivel=[2,3],valor_inserido=len(pattern[dado]),campo="timestamp")
                    regex1=r'[\+,\-][0-9]*[d,m,y]'
                    regex2=r'[0-9]{4}[\/,\-][0-9]{2}[\/,\-][0-9]{2}'
                    if len(pattern[dado])>=2:
                        match1=re.match(regex1,pattern[dado][1])
                        match2=re.match(regex2,pattern[dado][1])
                        if type(pattern[dado][1] )!=type("") or ((not match1 and not match2 and (match1 != None or match2 != None)) and pattern[dado][1] != "agora"):
                            if type(pattern[dado][1] ) != type(""):
                                print("tipo")
                            if (not match1 and not match2 and type(match1) != None):
                                print("regex")
                                print(match1)
                                print(match2)
                            if pattern[dado][1]!="agora":
                                print("string especial")
                            raise self.TipoDeDadoIncompativel(pattern[dado][1],tipo_possivel="string com padrão -30y ou 1999-02-02 ou 1999/02/02",campo="campo 1 adicional em timestamp")
                    if len(pattern[dado])>=3:
                        match1=re.match(regex1,pattern[dado][2])
                        match2=re.match(regex2,pattern[dado][2])
                        if type(pattern[dado][2] )!=type("") or ((not match1 and not match2 and (match1 != None or match2 != None)) and pattern[dado][2] != "agora") :
                            raise self.TipoDeDadoIncompativel(pattern[dado][2],tipo_possivel="string com padrão -30y ou 1999-02-02 ou 1999/02/02",campo="campo 2 adicional em timestamp")
                    start_date=""
                    end_date=""
                    if pattern[dado][1] == "agora" :#se true é tudo randomico
                        end_date="today"
                    else:
                        end_date=pattern[dado][1]
                        if len(pattern[dado])>2:
                            start_date=end_date
                            if pattern[dado][2] == "agora":
                                end_date="today"
                    if start_date == "" :
                        dados_gerados["dados"][dado]=fake.date_between(end_date=end_date).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        dados_gerados["dados"][dado]=fake.date_between_dates(start_date=start_date,end_date=end_date).strftime('%Y-%m-%d %H:%M:%S')
                elif pattern[dado][0] == "pais":
                    dados_gerados["dados"][dado]=fake.current_country()
                elif pattern[dado][0] == "cidade":
                    dados_gerados["dados"][dado]=fake.city()
                elif pattern[dado][0] == "endereco":
                    dados_gerados["dados"][dado]=fake.street_address()
                elif pattern[dado][0] == "cep":
                    dados_gerados["dados"][dado]=fake.postcode()
                elif pattern[dado][0] == "telefone":
                    if fake.boolean():
                        dados_gerados["dados"][dado]=fake.phone_number()
                    else:
                        try:
                            dados_gerados["dados"][dado]=fake.cellphone_number()
                        except:
                            dados_gerados["dados"][dado]=fake.phone_number()
                elif pattern[dado][0] == "nomeCategoria":
                    dados_gerados["dados"][dado]=fake.word()
                elif pattern[dado][0] == "email":
                    dados_gerados["dados"][dado]=fake.email()
                elif pattern[dado][0] == "usuario":
                    dados_gerados["dados"][dado]=fake.profile(fields=["username"])["username"]
                elif pattern[dado][0] == "senha":
                    dados_gerados["dados"][dado]=fake.password(length=fake.random_int(min=8,max=32))
                elif pattern[dado][0] == "boleano":
                    dados_gerados["dados"][dado]=fake.boolean()
                elif pattern[dado][0] == "idioma":
                    dados_gerados["dados"][dado]=fake.locale()
                elif pattern[dado][0] == "titulo":
                    dados_gerados["dados"][dado]=fake.sentence(nb_words=fake.random_int(min=1,max=10))
                elif pattern[dado][0] == "textoLongo":
                    dados_gerados["dados"][dado]=fake.paragraphs(nb=fake.random_int(min=1,max=2))
                elif pattern[dado][0] == "nota":
                    dados_gerados["dados"][dado]=uniform(0.0,10.0)
                elif pattern[dado][0] == "ano":
                    dados_gerados["dados"][dado]=fake.date(pattern='%Y')
                elif pattern[dado][0] == "duracaoDias":
                    dados_gerados["dados"][dado]=fake.random_int(min=1,max=10)
                elif pattern[dado][0] =="datetime":
                    dados_gerados["dados"][dado]=fake.date_time().strftime('%Y-%m-%d')
                elif pattern[dado][0] == "duracaoHoras":
                    dados_gerados["dados"][dado]=uniform(0.0,4.0)
                elif pattern[dado][0] == "naLista":
                    if not all(isinstance(n, str) for n in list(pattern[dado][0])):
                        raise self.TipoDeDadoIncompativel(pattern[dado][1],tipo_possivel="string",campo="variaveis adicionais da variavel naLista")
                    dados_gerados["dados"][dado]=fake.word(ext_word_list=pattern[dado][1:] )
                elif pattern[dado][0] == "valorPago":
                    dados_gerados["dados"][dado]=uniform(0.0,50.0)
                elif pattern[dado][0] == "associacao":
                    '''
                    parametros obrigatórios são nome da tabela e se random ou se definido
                    '''
                    if len(pattern[dado])<2:
                        raise self.TamanhoArrayErrado(valor_possivel=2,valor_inserido=len(pattern[dado]),campo="associacao")
                    if type(pattern[dado][1]) != type(""):
                        raise self.TipoDeDadoIncompativel(valor_inserido=pattern[dado][1],tipo_possivel=["string","array"],campo="associacao")
                    if pattern[dado][1]!="random":
                        dados_gerados["dados"][dado]=pattern[dado][1]
                    else:
                        total_cadastrado=self.buscar_ultimo_id_cadastrado(pattern[dado][1])
                        if total_cadastrado>1:
                            dados_gerados["dados"][dado]=fake.random_int(min=1,max=self.buscar_ultimo_id_cadastrado(pattern[dado][1]))
                        else:
                            dados_gerados["dados"][dado]=1
                elif pattern[dado][0] == "id":
                    dados_gerados["dados"][dado]=id
            return dados_gerados
        except self.TamanhoArrayErrado as e :
            self.logging.error(e)
        except self.ValorInvalido as e:
            self.logging.error(e)
        except self.TipoDeDadoIncompativel as e:
            self.logging.error(e)
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])

    def gerador_filtro(self,table,pattern,select_country="random",id:int=-1):
        parametros=pattern.keys()
        created_data=self.create_data(table=table,pattern=pattern,select_country=select_country,id=id)
        return {"filtro":parametros,"data":created_data}

    def process_data_generated(self,text):
        pattern_geral=r"([0-9]*),'(.*)',([0-9]*),'(.*)','(.*)'"
        etapa1_operacoes=re.findall(pattern_geral,text)[0]
        self.logging.debug(etapa1_operacoes)
        output={}
        output["tipoOpracao"]=etapa1_operacoes[0]
        output["nomeBD"]=etapa1_operacoes[1]
        output["idNoBD"]=etapa1_operacoes[2]
        output["associacoes"]=etapa1_operacoes[3]
        output["dados"]=etapa1_operacoes[4]
        self.logging.debug(output)
        pattern_associacoes=r"\[\{(.*)\}\]"
        associacoes=[]
        for dado in re.findall(pattern_associacoes, output["associacoes"])[0].split("},{"):
            associacoes.append(self.string_to_dict(dado,patter_externo=r"(.*)"))
        self.logging.debug(associacoes)
        output["associacoes"]=associacoes
        output["dados"]=self.string_to_dict(output["dados"])
        return output

    def string_to_dict(self,text,patter_externo=r"\{(.*)\}",pattern_interno=r"(.*)\:(.*)",external_header_list=[]):
        pattern_etapa1=patter_externo
        etapa1_dados=re.findall(pattern_etapa1,text)
        etapa1_dados=etapa1_dados[0].split(",")
        self.logging.debug(etapa1_dados)
        pattern_dados_etapa2=pattern_interno
        dados={}
        tmp=0
        for dado in etapa1_dados:
            etapa2_dados=re.findall(pattern_dados_etapa2,dado)[0]
            if external_header_list == []:
                dados[etapa2_dados[0].replace("'","").replace('"',"")]=etapa2_dados[1].replace("'","").replace('"',"")
            else:
                dados[external_header_list[tmp]]=etapa2_dados[0]
                tmp+=1
        self.logging.debug(dados)
        return dados

#relacionado a interação com sqlite
    def buscar_ultimo_id_cadastrado(self,table):
        filtro={"nomeBD":table}
        query=["numeroDDadosCadastrados"]
        self.verify_if_contador_exists(table)
        retorno=self.read_data_sqlite("contadores",filtro,query)
        return int(retorno[0][0])

    def insert_data_sqlite(self,data:dict,nomeDB:str=""):
        '''
        INSERT INTO "operacoes"(	"tipoOperacao",	"nomeBD","associacoes","dados")
        VALUES(1,"empregado","[(pessoas,pessoas_id,1),(lojas,loja_id)]","{salario:1200,contratado:30/12/20}")
        '''
        insert_command="INSERT INTO "
        insert_command+="'"+"operacoes"+"' ("
        for coluna in data.keys():
            insert_command+=str(coluna)
            if nomeDB == "" and coluna == 'nomeBD':
                nomeDB=data["nomeBD"]
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
            pprint.pprint(data)
            self.verify_if_contador_exists(nomeDB)
            cursor.execute("UPDATE contadores SET numeroDDadosCadastrados = numeroDDadosCadastrados+1 WHERE nomeBD='"+nomeDB+"';")
            self.conn.commit()
        except sqliteError as e:
            print("erro no sqlite")
            self.logging.error(e)
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])
    
    def verify_if_contador_exists(self,nomeDB):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM contadores WHERE nomeBD is '"+nomeDB+"';")
        listagem=cursor.fetchall() 
        if listagem == []:
            cursor.execute("INSERT INTO contadores(nomeBD,numeroDDadosCadastrados) VALUES ('"+nomeDB+"',0);")

    def read_data_sqlite(self,tabela:str,filtro="",query="*"):
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
        read_command+="'"+tabela+"'"
        if filtro != "":
            read_command+=" WHERE "
            for coluna in filtro.keys():
                        read_command+=str(coluna) + " IS "
                        if type(filtro[coluna])==type(""):
                            read_command+="'"+filtro[coluna]+"'"
                        else:
                            read_command+=filtro[coluna]
                        if coluna !=  list(filtro.keys())[-1]:
                            read_command+=" AND "
        read_command+=";"
        try:
            cursor = self.conn.cursor()
            self.logging.debug(read_command)
            cursor.execute(read_command)
            self.conn.commit()
            return cursor.fetchall()
        except sqliteError as e:
            print("erro no sqlite")
            self.logging.error(e)
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])

    def read_contadores(self,filtro="",query="*"):
        return gerador.read_data_sqlite("contadores",filtro=filtro,query=query)

    def read_operacoes(self,filtro="",query="*"):
        return gerador.read_data_sqlite("operacoes",filtro=filtro,query=query)

    def execute_sqlfile_sqlite(self,pattern,conn=None):
        if conn != None:
            cursor = conn.cursor()
        else:
            cursor=self.conn
        sqlfile=open(pattern).read().split(";\n")
        for sqlstatement in sqlfile:
            if sqlstatement[-1] != ";":
                sqlstatement+=";"
            self.logging.debug(sqlstatement)
            cursor.execute(sqlstatement)
            conn.commit()

#relacionado com a geração do sql final
    def generate_SQL_command_from_data(self,data,nome_coluna_id="id"):
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
        command=""
        try:
            if data["tipoOpracao"]==1:#insercao
                command+="INSERT INTO "
            elif data["tipoOpracao"]==2:#leitura completa
                command+="SELECT * FROM "
            elif data["tipoOpracao"]==3:#busca
                command+="SELECT * FROM"
            elif data["tipoOpracao"]==4:#busca filtrada
                command+="SELECT ("
                for i in data['associacoes']:
                    command+= str(i["variavelRetornada"])+ ","
                if (data["idNoBD"]!=-1) and ("idNoBD" in data):
                    command+=nome_coluna_id
                command+=") FROM "
            elif data["tipoOpracao"]==5:#edicao
                command+=" UPDATE "
            elif data["tipoOpracao"]==6:#delecao
                command+="DELETE FROM "
            else:
                raise self.ValorInvalido(valor_inserido=data["tipoOpracao"])

            command+=str(data["nomeBD"])

            if data["tipoOpracao"]==1:#insercao
                command+="("
                for coluna in data["dados"].keys():
                    if type(data[coluna])==type("") or type(data[coluna])==type({}) or  type(data[coluna])==type([])  :
                        command+='"'+data[coluna].replace("\n","")+'"'
                    else:
                        command+=str(data[coluna])
                    if coluna != data["dados"].keys()[-1]:
                        command+=","
                command+=") VALUES ("
                for coluna in data["dados"].keys():
                    if type(data[coluna])==type("") or type(data[coluna])==type({}) or  type(data[coluna])==type([])  :
                        command+='"'+data[coluna].replace("\n","")+'"'
                    else:
                        command+=str(data[coluna])
                    if coluna != data["dados"].keys()[-1]:
                        command+=","
                command+=");"
            elif data["tipoOpracao"]==2:#leitura completa
                command+="; "
            elif data["tipoOpracao"] in [3,4,6]:# busca #busca filtrada #remocao
                command+=" WHERE "
                for coluna in data["dados"].keys():
                    command+=str(coluna) + " IS "+str(data["dados"][coluna])
                    if coluna != data["dados"].keys()[-1]:
                        command+=" AND "
                if (data["idNoBD"]!=-1) and ("idNoBD" in data):
                    if len(data["dados"].keys())>0:
                        command+=" AND "
                    command+=nome_coluna_id+" IS "+data["idNoBD"]
                command+=";"
            elif data["tipoOpracao"]==5:#edicao
                command+=" SET "
                for coluna in data["dados"].keys():
                    command+=str(coluna) + " = "+str(data["dados"][coluna])
                    if coluna != data["dados"].keys()[-1]:
                        command+=" , "
                command+=" WHERE "
                for coluna in data["associacoes"].keys():
                    command+=str(coluna) + " IS "+str(data["associacoes"][coluna])
                    if coluna != data["associacoes"].keys()[-1]:
                        command+=" AND "
                if (data["idNoBD"]!=-1) and ("idNoBD" in data):
                    if len(data["dados"].keys())>0:
                        command+=" AND "
                    command+=nome_coluna_id+" IS "+data["idNoBD"]
                command+=";"
        except sqliteError as e:
            print("erro no sqlite")
            self.logging.error(e)
        except self.ValorInvalido as e :
            self.logging.error(e)
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])

        return command

    def gerar_dado_insersao(self,table,pattern,select_country="random",id:int=-1):
        data=self.create_data(table=table,pattern=pattern,select_country=select_country,id=id)
        self.logging.debug(data)
        self.insert_data_sqlite(data,nomeDB=table)

    def gerar_dados_por_json(self,json_file,select_country="random",tabela="random",quantidade="random"):
        file=open(json_file)
        json_loaded=json.loads(file.read())
        if tabela == "random":
            tabela=random.choice(json_loaded.keys())
        if quantidade == "random":
            quantidade=random.randint(0, 20)
        for i in range(0,quantidade):
            self.logging.debug("table="+tabela+", pattern="+str(json_loaded[tabela])+", select_country="+select_country)
            self.gerar_dado_insersao(table=tabela,pattern=json_loaded[tabela],select_country=select_country)
    
    def gerar_todos_dados_por_json(self,json_file,select_country="random",quantidade="random"):
        if quantidade == "random":
            quantidade=random.randint(0, 20)
        file=open(json_file)
        json_loaded=json.loads(file.read())
        self.logging.debug(json_loaded)
        for table in json_loaded.keys():
            self.gerar_dados_por_json(json_file,select_country=select_country,tabela=table,quantidade=quantidade)

gerador=GeradorDeSql(sqlite_db="scripts/initial_db.db",sql_file_pattern="scripts/sqlitePattern.sql", log_file="scripts/geradorSQL.log",level=10)
#pprint.pprint(gerador.process_data_generated("1,'empregado',1,'[{'bdAssociado': 'pessoas', 'fkAssociada': 'pessoas_id', 'id associado': '1'},{'bdAssociado': 'lojas', 'fkAssociada': 'loja_id', 'id associado': '1'}]','{salario:1200,contratado:'30/12/20'}'"))
# gerador.insert_data_sqlite({"tipoOperacao":1,"nomeBD":'empregado',"idNoBD":1,"associacoes":"[{'bdAssociado': 'pessoas', 'fkAssociada': 'pessoas_id', 'id associado': '1'},{'bdAssociado': 'lojas', 'fkAssociada': 'loja_id', 'id associado': '1'}]","dados":"{salario:1200,contratado:'30/12/20'}"})
# pprint.pprint(gerador.read_operacoes())
# pprint.pprint(gerador.read_contadores())
# print(gerador.buscar_ultimo_id_cadastrado("empregado"))
# tmp=[]
# for i in range(0,10):
#     gerador.gerar_dado_insersao("city",pattern=dict({
#         "city_id":["id"],
#         "city":["cidade"],
#         "country_id":["associacao","country"],
#         "last_update":["timestamp","agora"]
#     }),select_country="en_US")
gerador.gerar_todos_dados_por_json(json_file="./scripts/padroes.json",select_country="en_US",quantidade=3)
pprint.pprint(gerador.read_contadores())