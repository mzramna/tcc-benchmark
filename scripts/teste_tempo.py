from geradorDeSql import GeradorDeSql
from pprint import pprint
from random import randint, random,uniform,choice
from time import time
import os
#logstash_data={"host":"192.168.0.116","port":5000,"username":"elastic","password":"changeme"}
#logstash_data={"host":"192.168.0.116","port":5000}
logstash_data={}
tempos=[]
quantidade_elementos=0
for k in range(30):
    tempo=[]
    quantidade_elementos+=100
    for i in range(4):
        f = open("teste_de_execucao.log", "a")
        try:
            os.remove("scripts/initial_db.db")
        except:
            pass
        inicio=time()
        gerador=GeradorDeSql(sqlite_db="scripts/initial_db.db",sql_file_pattern="scripts/sqlitePattern.sql", log_file="scripts/geradorSQL.log",level=10,logging_pattern='%(asctime)s - %(name)s - %(levelname)s - %(message)s',logstash_data=logstash_data)

        gerador.gerar_todos_dados_por_json(select_country="pt_br",quantidade_ciclo=1,total_ciclos=100,quantidade_final=quantidade_elementos)

        fim=time()
        tempo.append(fim-inicio)
        print(fim-inicio)
        f.write(str(fim-inicio)+"\n")
        f.close()
        del gerador
    #pprint(tempos)
    tempos.append(tempo)
    f = open("teste_de_execucao.log", "a")
    print("para ",quantidade_elementos," dados foram gastos os seguintes dados de tempo")
    print("media geração completa",str(sum(tempo)/len(tempo)))
    print("media por elemento",str((sum(tempo)/len(tempo))/quantidade_elementos))
    f.write("para "+str(quantidade_elementos)+" dados foram gastos os seguintes dados de tempo"+"\n")
    f.write("media geração completa"+str(sum(tempo)/len(tempo))+"\n")
    f.write("media por elemento"+str((sum(tempo)/len(tempo))/quantidade_elementos)+"\n")
quantidade_elementos=0
somatorio_total=0
quantidades=0
for i in range(30):
    somatorio_total+=sum(tempos[i])
    quantidades+=len(tempos[i])
    quantidade_elementos+=100
f = open("teste_de_execucao.log", "a")
print("media geração completa"+str(somatorio_total/quantidades)+"\n")
print("media por elemento"+str((somatorio_total/quantidades)/quantidade_elementos)+"\n")
f.write("media geração completa"+str(somatorio_total/quantidades)+"\n")
f.write("media por elemento"+str((somatorio_total/quantidades)/quantidade_elementos)+"\n")

