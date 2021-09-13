from loggingSystem import loggingSystem
from faker import Faker
import sqlite3
from sqlite3 import Error as sqliteError
import os,sys,re,pprint
class geradorDeSql:
    def __init__(self,sqlitedb="./initial_db.db",sqliFilePattern="./sqlitePattern.sql",loggin_name="geradorSQL", log_file="./geradorSQL.log",level=10):
        """
        classe para gerenciar arquivos csv
        :param loggin_name: nome do log que foi definido para a classe,altere apenas em caso seja necessário criar multiplas insstancias da função
        :param log_file: nome do arquivo de log que foi definido para a classe,altere apenas em caso seja necessário criar multiplas insstancias da função
        """
        self.logging = loggingSystem(loggin_name, arquivo=log_file,level=level)
        self.sqliFilePattern=sqliFilePattern
        if not os.path.isfile(sqlitedb):
            self.createTemporaryDB(local=sqlitedb)
        self.conn = sqlite3.connect(sqlitedb)
    
    def createTemporaryDB(self,local):
        try:
            '''
                tipo de operação:int #1:insersão,2:leitura,3:edição,4:deleção
                bd:string # banco de dados en que será inserido
                associações: #text
                [
                    {"nome_do_bd_associado":nome_do_bd_associado,variavel_associada:string,valor} # o nome do bd associado, o nome da foregin key associada e o valor do id da associação
                ]
                outros dados do bd: #text
                {
                    nome da variavel:conteudo da variavel #string:string  #nome do tipo da variavel do bd e o conteudo dela
                }
            '''
            sqlfile=open(self.sqliFilePattern).read()
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

    def createData(self,table,pattern):    
        fake = Faker()

    def insertData(self,data):
        '''
        INSERT INTO "operacoes"(	"tipoOperacao",	"nomeBD","associacoes","dados")
        VALUES(1,"empregado","[(pessoas,pessoas_id,1),(lojas,loja_id)]","{salario:1200,contratado:30/12/20}")
        '''
        insertCommand="INSERT INTO  'operacoes'('tipoOperacao',	'nomeBD','associacoes','dados') VALUES("
        insertCommand+=str(data["tipoOperacao"])+","
        insertCommand+=str(data["nomeBD"])+","
        insertCommand+=str(data["associacoes"]).replace("\n","")+","
        insertCommand+=str(data["dados"]).replace("\n","")+","
        self.logging.debug(insertCommand)
        try:
            cursor = self.conn.cursor()
            cursor.execute(insertCommand)
            self.conn.commit()
        except sqliteError as e:
            print("erro no sqlite")
            self.logging.exception(e)
        except :
            self.logging.exception("Unexpected error:", sys.exc_info()[0])

    def processDataGenerated(self,text):
        patternGeral=r"([0-9]*),'(.*)','(.*)','(.*)'"
        etapa1Operacoes=re.findall(patternGeral,text)[0]
        self.logging.debug(etapa1Operacoes)
        output={}
        output["tipoOpracao"]=etapa1Operacoes[0]
        output["nomeBD"]=etapa1Operacoes[1]
        output["associacoes"]=etapa1Operacoes[2]
        output["dados"]=etapa1Operacoes[3]
        self.logging.debug(output)
        patternAssociacoes=r"\[\{(.*)\}\]"
        associacoes=[]
        for dado in re.findall(patternAssociacoes, output["associacoes"])[0].split("},{"):
            associacoes.append(self.stringToDict(dado,patterExterno=r"(.*)"))
        self.logging.debug(associacoes)
        output["associacoes"]=associacoes
        output["dados"]=self.stringToDict(output["dados"])
        return output

    def stringToDict(self,text,patterExterno=r"\{(.*)\}",patternInterno=r"(.*)\:(.*)",externalHeaderList=[]):
        patternEtapa1=patterExterno
        etapa1Dados=re.findall(patternEtapa1,text)
        etapa1Dados=etapa1Dados[0].split(",")
        self.logging.debug(etapa1Dados)
        patternDadosEtapa2=patternInterno
        dados={}
        tmp=0
        for dado in etapa1Dados:
            etapa2Dados=re.findall(patternDadosEtapa2,dado)[0]
            if externalHeaderList == []:
                dados[etapa2Dados[0].replace("'","").replace('"',"")]=etapa2Dados[1].replace("'","").replace('"',"")
            else:
                dados[externalHeaderList[tmp]]=etapa2Dados[0]
                tmp+=1
        self.logging.debug(dados)
        return dados

    def generateSQLCommandFromData(self,data):
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
                raise Exception(data["tipoOpracao"],"não é um valor valido para essa posição")

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
        except Exception as e :
            self.logging.exception(e)
        except :
            self.logging.exception("Unexpected error:", sys.exc_info()[0])

        return command

gerador=geradorDeSql(sqlitedb="scripts/initial_db.db",sqliFilePattern="scripts/sqlitePattern.sql", log_file="scripts/geradorSQL.log",level=10)
pprint.pprint(gerador.processDataGenerated("1,'empregado','[{'bdAssociado': 'pessoas', 'fkAssociada': 'pessoas_id', 'id associado': '1'},{'bdAssociado': 'lojas', 'fkAssociada': 'loja_id', 'id associado': '1'}]','{salario:1200,contratado:'30/12/20'}'"))
