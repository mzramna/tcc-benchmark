from loggingSystem import loggingSystem
from faker import Faker
from random import random
from sqlite3 import Error as sqliteError
import os,sys,re,pprint,sqlite3
class GeradorDeSql:
    class ValorInvalido(Exception):
        def __init__(self, valor_inserido,mensagem_principal_replace=False,mensage_adicional="",campo="",valor_possivel="") :
            if not mensagem_principal_replace:
                self.message="um valor inserido foi inserido de forma errada\no valor "+str(valor_inserido)+" é invalido ou foi inserido de forma errada"
                if campo!="":
                    self.message=+" no campo "+str(campo)
                self.message=+"\n"
                self.listagem_valores_possiveis(valores_possiveis=valor_possivel)
                self.message=+"\n"
            self.message=+str(mensage_adicional)
            
            super().__init__(self.message)

        def listagem_valores_possiveis(self,valores_possiveis="",campo=""):
            if valores_possiveis !="":
                if  type("")==type(valores_possiveis):
                    self.message=+" o valor possivel "
                    if campo!="":
                        self.message=+"no campo "+str(campo)+" "
                    self.message=+"é "
                elif  type("")==type(valores_possiveis):
                    self.message=+" os valores possiveis "
                    if campo!="":
                        self.message=+"no campo "+str(campo)+" "
                    self.message=+"são "+str(valores_possiveis)
                self.valores_possiveis(valores_possiveis)

        def valores_possiveis(self,valores_possiveis=""):
            if type(valores_possiveis)==type([]):
                for valor in valores_possiveis:
                    self.message+=str(valor) 
                    if valor == valores_possiveis[-2]:
                        self.message+=" ou "
                    elif valor not in valores_possiveis[-2:]:
                        self.message+=","
            else:
                self.message+=str(valores_possiveis)
    class TamanhoArrayErrado(ValorInvalido):
        def __init__(self,valor_inserido,valor_possivel="",campo="") :
            self.message="o tamanho para o array passado "
            if campo!="":
                self.message=+"no campo "+str(campo)+" "
            self.message+="é invalido\n"
            if valor_possivel!="":
                self.message+=" o tamanho esperado era de "+self.valores_possiveis(valor_inserido)+" programa não pode continuar"
            super().__init__(valor_inserido,mensagem_principal_replace=True,mensage_adicional=self.message,campo=campo)

        def valores_possiveis(self,valores_possiveis=""):
            super.valores_possiveis(valores_possiveis)

        def listagem_valores_possiveis(self,valores_possiveis="",campo=""):
            super.listagem_valores_possiveis(valores_possiveis="",campo="")
    class TipoDeDadoIncompativel(ValorInvalido):
        def __init__(self,valor_inserido,tipo_possivel="",campo="") :
            self.message="o tipo da variavel passada "
            if campo!="":
                self.message=+"no campo "+str(campo)+" "
            self.message+="é invalido\n"
            if valor_possivel!="":
                self.message+=" o tipo esperado era de "+self.valores_possiveis(valor_inserido)+" programa não pode continuar"
            super().__init__(valor_inserido,mensagem_principal_replace=True,mensage_adicional=self.message,campo=campo)

        def valores_possiveis(self,valores_possiveis=""):
            super.valores_possiveis(valores_possiveis)

        def listagem_valores_possiveis(self,valores_possiveis="",campo=""):
            super.listagem_valores_possiveis(valores_possiveis="",campo="")

    def __init__(self,sqlite_db="./initial_db.db",sql_file_pattern="./sqlitePattern.sql",loggin_name="geradorSQL", log_file="./geradorSQL.log",level=10):
        """
        classe para gerenciar arquivos csv
        :param loggin_name: nome do log que foi definido para a classe,altere apenas em caso seja necessário criar multiplas insstancias da função
        :param log_file: nome do arquivo de log que foi definido para a classe,altere apenas em caso seja necessário criar multiplas insstancias da função
        """
        self.logging = loggingSystem(loggin_name, arquivo=log_file,level=level)
        if not os.path.isfile(sqlite_db):
            self.create_temporary_DB(local=sqlite_db,pattern=sql_file_pattern)
        self.conn = sqlite3.connect(sqlite_db)
    
    def create_temporary_DB(self,local,pattern):
        try:
            sqlfile=open(pattern).read()
            self.logging.debug(sqlfile)
            conn = sqlite3.connect(local)
            cursor = conn.cursor()
            cursor.execute(sqlfile)
            conn.close()
            self.logging.debug("bd gerado com sucesso")
        except sqliteError as e:
            print("erro no sqlite")
            self.logging.exception(e)
        except :
            self.logging.exception("Unexpected error:", sys.exc_info()[0])

    def create_data(self,table,pattern,select_country="random"): 
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
        try:
            if select_country=="random":
                fake = Faker()
                fake = Faker(fake.locale()) #define o faker para seguir o padrão de um pais expecifico selecionado aleatoriamente dentre os disponiveis
            else:
                fake = Faker(select_country)#se for definido então o codigo usado será o do pais inserido
            dados_gerados={"nomeBD":table,"tipoOperacao":1}
            for dado in pattern.keys():
                if pattern[dado][0] == "nomeCompleto":
                    '''supoe-se que qualquer pessoa pode ter nascido em qq lugar e morar em qualquer outro lugar,nomes são dados pelo gerador de qualquer idioma,por isso nao foi definido um pais para a geracao'''
                    dados_gerados[dado]=fake.name()
                elif pattern[dado][0] == "primeiroNome":
                    dados_gerados[dado]=fake.first_name()
                elif pattern[dado][0] == "sobrenome":
                    dados_gerados[dado]=fake.last_name()
                elif pattern[dado][0] == "timestamp":
                    '''precisa obrigatoriamente de 1 parametro dizendo se vai ser tudo randomico ou se vai ter um intervalo,se tiver um intervalo devem ser passados mais 2 parametros,um inicial e um final , se o final for o valor "agora" então o valor final sera o timestamp de agora do sistema operacional

                    para gerar com mais precisão usar o 2 parametro como: "-30y",sendo: - > significando anterior , 30 > quanto tempo , y > escala de tempo(anos) ou usando o padrão Date("dia") onde o dia deve ser passado como "1999-02-02"

                    o 3 parametro deve ser passado como o 2,mas não se limita apenas ao token de tempo anterior,sendo possivel um intervalo do futuro
                    '''
                    if len(pattern[dado])<1:
                        raise self.TamanhoArrayErrado(valor_possivel=[1,2,3],valor_inserido=len(pattern[dado]))
                    if pattern[dado][1]:#se true é tudo randomico
                        dados_gerados[dado]=fake.date_between(end_date="today")
                    else:
                        if pattern[dado][3] == "agora":
                            dados_gerados[dado]=fake.fake.date_between(start_date=pattern[dado][2],end_date="today")
                        else:
                            dados_gerados[dado]=fake.date_between_dates(pattern[dado][2],pattern[dado][3])
                elif pattern[dado][0] == "pais":
                    dados_gerados[dado]=fake.current_country()
                elif pattern[dado][0] == "cidade":
                    dados_gerados[dado]=fake.city()
                elif pattern[dado][0] == "endereco":
                    dados_gerados[dado]=fake.street_address()
                elif pattern[dado][0] == "cep":
                    dados_gerados[dado]=fake.postcode()
                elif pattern[dado][0] == "telefone":
                    if fake.boolean():
                        dados_gerados[dado]=fake.phone_number()
                    else:
                        try:
                            dados_gerados[dado]=fake.cellphone_number()
                        except:
                            dados_gerados[dado]=fake.phone_number()
                elif pattern[dado][0] == "nomeCategoria":
                    dados_gerados[dado]=fake.word()
                elif pattern[dado][0] == "email":
                    dados_gerados[dado]=fake.email()
                elif pattern[dado][0] == "usuario":
                    dados_gerados[dado]=fake.profile(fields=["username"])["username"]
                elif pattern[dado][0] == "senha":
                    dados_gerados[dado]=fake.password(length=fake.random_int(min=8,max=32))
                elif pattern[dado][0] == "boleano":
                    dados_gerados[dado]=fake.boolean()
                elif pattern[dado][0] == "idioma":
                    dados_gerados[dado]=fake.locale()
                elif pattern[dado][0] == "titulo":
                    dados_gerados[dado]=fake.sentence(nb_words=fake.random_int(min=1,max=10))
                elif pattern[dado][0] == "textoLongo":
                    dados_gerados[dado]=fake.paragraphs(nb=fake.random_int(min=1,max=2))
                elif pattern[dado][0] == "nota":
                    dados_gerados[dado]=random.uniform(0.0,10.0)
                elif pattern[dado][0] == "duracaoDias":
                    dados_gerados[dado]=fake.random_int(min=1,max=10)
                elif pattern[dado][0] == "duracaoHoras":
                    dados_gerados[dado]=random.uniform(0.0,4.0)
                elif pattern[dado][0] == "classificacao":
                    dados_gerados[dado]=fake.word(ext_word_list=['G','PG','PG-13','R','NC-17'])
                elif pattern[dado][0] == "funcaoEspecial":
                    dados_gerados[dado]=fake.word(ext_word_list=['Trailers','Commentaries','Deleted Scenes','Behind the Scenes'])
                elif pattern[dado][0] == "valorPago":
                    dados_gerados[dado]=random.uniform(0.0,50.0)
                elif pattern[dado][0] == "associacao":
                    ##associação entre as as varias tabelas,precisa de ter 
                    pass
        except self.TamanhoArrayErrado as e :
            self.logging.exception(e)
        except self.ValorInvalido as e:
            self.logging.exception(e)
        except self.TipoDeDadoIncompativel as e:
            self.logging.exception(e)
        except :
            self.logging.exception("Unexpected error:", sys.exc_info()[0])


    def insert_data(self,data):
        '''
        INSERT INTO "operacoes"(	"tipoOperacao",	"nomeBD","associacoes","dados")
        VALUES(1,"empregado","[(pessoas,pessoas_id,1),(lojas,loja_id)]","{salario:1200,contratado:30/12/20}")
        '''
        insert_command="INSERT INTO  'operacoes'('tipoOperacao',	'nomeBD','associacoes','dados') VALUES("
        insert_command+=str(data["tipoOperacao"])+","
        insert_command+=str(data["nomeBD"])+","
        insert_command+=str(data["associacoes"]).replace("\n","")+","
        insert_command+=str(data["dados"]).replace("\n","")+","
        self.logging.debug(insert_command)
        try:
            cursor = self.conn.cursor()
            cursor.execute(insert_command)
            self.conn.commit()
        except sqliteError as e:
            print("erro no sqlite")
            self.logging.exception(e)
        except :
            self.logging.exception("Unexpected error:", sys.exc_info()[0])

    def process_data_generated(self,text):
        pattern_geral=r"([0-9]*),'(.*)','(.*)','(.*)'"
        etapa1_operacoes=re.findall(pattern_geral,text)[0]
        self.logging.debug(etapa1_operacoes)
        output={}
        output["tipoOpracao"]=etapa1_operacoes[0]
        output["nomeBD"]=etapa1_operacoes[1]
        output["associacoes"]=etapa1_operacoes[2]
        output["dados"]=etapa1_operacoes[3]
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

    def generate_SQL_command_from_data(self,data):
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
                    command+=str(coluna)
                    if coluna != data["dados"].keys()[-1]:
                        command+=","
                command+=") VALUES ("
                for coluna in data["dados"].keys():
                    command+=str(data["dados"][coluna])
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
                command+=";"
        except sqliteError as e:
            print("erro no sqlite")
            self.logging.exception(e)
        except self.ValorInvalido as e :
            self.logging.exception(e)
        except :
            self.logging.exception("Unexpected error:", sys.exc_info()[0])

        return command

gerador=GeradorDeSql(sqlite_db="scripts/initial_db.db",sqli_file_pattern="scripts/sqlitePattern.sql", log_file="scripts/geradorSQL.log",level=10)
pprint.pprint(gerador.processDataGenerated("1,'empregado','[{'bdAssociado': 'pessoas', 'fkAssociada': 'pessoas_id', 'id associado': '1'},{'bdAssociado': 'lojas', 'fkAssociada': 'loja_id', 'id associado': '1'}]','{salario:1200,contratado:'30/12/20'}'"))
