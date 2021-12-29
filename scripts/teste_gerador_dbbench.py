from geradorDeSql import GeradorDeSql
from pprint import pprint
from random import randint, random,uniform,choice
import os
#logstash_data={"host":"192.168.0.116","port":5000,"username":"elastic","password":"changeme"}
#logstash_data={"host":"192.168.0.116","port":5000}
logstash_data={}
quantidade_elementos_geracao=500
quantidade_elementos=50000
gerador=GeradorDeSql(sqlite_db="scripts/dbbench_teste.db",sql_file_pattern="scripts/sqlitePattern.sql", log_file="scripts/dbbench_teste.log",level=40,logging_pattern='%(asctime)s - %(name)s - %(levelname)s - %(message)s',logstash_data=logstash_data)

gerador.gerar_todos_dados_por_json(select_country="pt_br",tipo=[1],quantidade_final=quantidade_elementos_geracao)
gerador.gerar_todos_dados_por_json(select_country="pt_br",quantidade_final=quantidade_elementos)
gerador.generate_all_dbbench_data(file_path="./dbbench/",default_name_pre="teste_de_dbbench",table_name_in_file=True)
