from faker import Faker
import sqlite3
from sqlite3 import Error as sqliteError
import logging

class geradorDeSql:
    def __init__(self,loggin_name="csvManager", log_file="./csvManager.log"):
        """
        classe para gerenciar arquivos csv
        :param loggin_name: nome do log que foi definido para a classe,altere apenas em caso seja necessário criar multiplas insstancias da função
        :param log_file: nome do arquivo de log que foi definido para a classe,altere apenas em caso seja necessário criar multiplas insstancias da função
        """
        self.logging = loggingSystem(loggin_name, arquivo=log_file)
    
    def create_temporary_db(self,sqlfile,local="./initial_db.db"):
        try:
            '''
                tipo de operação:int
                bd:string
                associações:
                [
                    (nome_do_bd_associado:string,tipo:string)
                ]
                outros dados do bd:
                {
                    nome da variavel:conteudo da variavel #string:string
                }
            '''
            conn = sqlite3.connect(local)
            cursor = conn.cursor()
            cursor.execute(sqlfile)
            conn.close()
        except sqliteError as e:
            print("erro no sqlite")
            self.logging.error(e)
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])
            
            
    def create_data(self,table,):    
        fake = Faker()


print("hello world") 
