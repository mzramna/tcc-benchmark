from geradorDeSql import GeradorDeSql
from pprint import pprint
from random import randint, random,uniform,choice
import os
from timer import Timer

#logstash_data={"host":"192.168.0.116","port":5000,"username":"elastic","password":"changeme"}
logstash_data={"host":"192.168.0.116","port":5000}
#logstash_data={}
quantidade_elementos_geracao=500
quantidade_elementos=10000
tempos ={}
timer=Timer()
try:
    os.remove("scripts/initial_db.db")
except:
    pass
gerador=GeradorDeSql(sqlite_db="scripts/initial_db.db",sql_file_pattern="scripts/sqlitePattern.sql", log_file="scripts/geradorSQL.log",level=40,logging_pattern='%(asctime)s - %(name)s - %(levelname)s - %(message)s',logstash_data=logstash_data)
gerador.gerar_todos_dados_por_json(select_country="pt_br",tipo=[1],quantidade_final=quantidade_elementos_geracao)
print("gerados dados de inserção")
timer.inicio()
gerador.gerar_todos_dados_por_json(select_country="pt_br",quantidade_final=quantidade_elementos)
tempos["sequencial"]=timer.fim(print_=True)
print("gerados dados randomicos")

os.remove("scripts/initial_db.db")

gerador=GeradorDeSql(sqlite_db="scripts/initial_db.db",sql_file_pattern="scripts/sqlitePattern.sql", log_file="scripts/geradorSQL.log",level=40,logging_pattern='%(asctime)s - %(name)s - %(levelname)s - %(message)s',logstash_data=logstash_data)

gerador.gerar_todos_dados_por_json(select_country="pt_br",tipo=[1],quantidade_final=quantidade_elementos_geracao)
print("gerados dados de inserção")
timer.inicio()
gerador.gerar_todos_dados_por_json_paralel(threads=4,select_country="pt_br",quantidade_final=quantidade_elementos)
tempos["paralel"]=timer.fim(print_=True)
print("gerados dados randomicos")

print("tempos")
print(tempos)
