from geradorDeSql import GeradorDeSql
import os
from timer import Timer

#logstash_data={"host":"192.168.0.116","port":5000,"username":"elastic","password":"changeme"}
logstash_data={"host":"192.168.0.116","port":5000}
#logstash_data={}
bd="scripts/teste_db.db"
quantidade_elementos_geracao=1000
quantidade_elementos=10000
tempos ={}
timer=Timer()
try:
    os.remove(bd)
except:
    pass
gerador=GeradorDeSql(sqlite_db=bd,sql_file_pattern="scripts/sqlitePattern.sql", log_file="scripts/geradorSQL.log",level=40,logging_pattern='%(asctime)s - %(name)s - %(levelname)s - %(message)s',logstash_data=logstash_data)
gerador.gerar_todos_dados_por_json(select_country="pt_br",tipo=[1],quantidade_final=quantidade_elementos_geracao)
print("gerados dados de inserção sequencial")
timer.inicio()
gerador.gerar_todos_dados_por_json(select_country="pt_br",quantidade_final=quantidade_elementos)
tempos["sequencial"]=timer.fim(print_=True)
print("gerados dados randomicos sequencial")
del gerador
os.remove(bd)

gerador=GeradorDeSql(sqlite_db=bd,sql_file_pattern="scripts/sqlitePattern.sql", log_file="scripts/geradorSQL.log",level=40,logging_pattern='%(asctime)s - %(name)s - %(levelname)s - %(message)s',logstash_data=logstash_data)

gerador.gerar_todos_dados_por_json(select_country="pt_br",tipo=[1],quantidade_final=quantidade_elementos_geracao)
print("gerados dados de inserção paralelo")
timer.inicio()
gerador.gerar_todos_dados_por_json_paralel(threads=4,select_country="pt_br",quantidade_final=quantidade_elementos)
tempos["paralel"]=timer.fim(print_=True)
print("gerados dados randomicos paralelo")

print("tempos")
print(tempos)

