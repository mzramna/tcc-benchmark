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

    def insertData(self,data,pattern):
        '''
        INSERT INTO "operacoes" VALUES(
        1,"empregado","[(pessoas,pessoas_id,1),
        (lojas,loja_id)
    	]",
    	"{salario:1200,
    	contratado:30/12/20}"
        )
        '''

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


gerador=geradorDeSql(sqlitedb="scripts/initial_db.db",sqliFilePattern="scripts/sqlitePattern.sql", log_file="scripts/geradorSQL.log",level=10)
pprint.pprint(gerador.processDataGenerated("1,'empregado','[{'bdAssociado': 'pessoas', 'fkAssociada': 'pessoas_id', 'id associado': '1'},{'bdAssociado': 'lojas', 'fkAssociada': 'loja_id', 'id associado': '1'}]','{salario:1200,contratado:'30/12/20'}'"))
print("bd gerado")
