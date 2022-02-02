from geradorDeSql import GeradorDeSql
from pprint import pprint
from random import randint, random,uniform,choice
import os,multiprocessing
#logstash_data={"host":"192.168.0.116","port":5000,"username":"elastic","password":"changeme"}
#logstash_data={"host":"192.168.0.116","port":5000}
logstash_data={}
quantidade_elementos_geracao=1000
quantidade_elementos=10000
gerador=GeradorDeSql(sqlite_db="scripts/initial_db.db",sql_file_pattern="scripts/sqlitePattern.sql", log_file="scripts/geradorSQL.log",level=40,logging_pattern='%(asctime)s - %(name)s - %(levelname)s - %(message)s',logstash_data=logstash_data)
print(multiprocessing.cpu_count())
gerador.gerar_todos_dados_por_json_paralel(threads=4,select_country="pt_br",tipo=[1],quantidade_final=quantidade_elementos_geracao)
print("gerados dados de inserção")
gerador.gerar_todos_dados_por_json_paralel(threads=0,select_country="pt_br",quantidade_final=quantidade_elementos)
print("gerados dados randomicos")
