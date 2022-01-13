from geradorDeSql import GeradorDeSql
from pprint import pprint
from random import randint, random,uniform,choice
import os,json,time
from timer import Timer

#logstash_data={"host":"192.168.0.116","port":5000,"username":"elastic","password":"changeme"}
#logstash_data={"host":"192.168.0.116","port":5000}
logstash_data={}

try:
    f = open("teste_tempo_aditional_data_amd64.json", "r")
    loaded=json.load(f)
    f.close()
except:
    loaded={}
total_por_ciclo=4
maximo_elementos=3000
incremento=100
if "quantidade_elementos" not in loaded.keys():
    loaded["quantidade_elementos"]=0
if "tempos" not in loaded.keys():
    loaded["tempos"]=[]
while loaded["quantidade_elementos"]<maximo_elementos:
    if  len(loaded["tempos"])<1 or len(loaded["tempos"][-1])>=total_por_ciclo :
        loaded["tempos"].append([])
    loaded["quantidade_elementos"]+=incremento
    while len(loaded["tempos"][-1])<total_por_ciclo:
        timer=Timer()
        f = open("teste_tempo_execucao_amd64.log", "a")
        try:
            os.remove("scripts/teste_tempo_db.db")
        except:
            pass
        timer.inicio()
        gerador=GeradorDeSql(sqlite_db="scripts/teste_tempo_db.db",sql_file_pattern="scripts/sqlitePattern.sql", log_file="scripts/teste_tempo.log",level=40,logging_pattern='%(asctime)s - %(name)s - %(levelname)s - %(message)s',logstash_data=logstash_data)

        gerador.gerar_todos_dados_por_json(select_country="pt_br",quantidade_final=loaded["quantidade_elementos"])

        duracao=timer.fim()
        print(duracao)
        f.write(str(duracao)+"\n")
        f.close()
        f = open("teste_tempo_aditional_data_amd64.json", "w")
        loaded["tempos"][-1].append(duracao)
        json.dump(loaded,f)
        f.close()
        del gerador
    #pprint(tempos)
    f = open("teste_tempo_execucao_amd64.log", "a")
    print("para ",loaded["quantidade_elementos"]," dados foram gastos os seguintes dados de tempo")
    print("media geração completa ",str(sum(loaded["tempos"][-1])/len(loaded["tempos"][-1])))
    print("media por elemento ",str((sum(loaded["tempos"][-1])/len(loaded["tempos"][-1]))/loaded["quantidade_elementos"]))
    f.write("para "+str(loaded["quantidade_elementos"])+" dados foram gastos os seguintes dados de tempo"+"\n")
    f.write("media geração completa "+str(sum(loaded["tempos"][-1])/len(loaded["tempos"][-1]))+"\n")
    f.write("media por elemento "+str((sum(loaded["tempos"][-1])/len(loaded["tempos"][-1]))/loaded["quantidade_elementos"])+"\n")
quantidade_elementos=0
somatorio_total=0
quantidades=0
while quantidade_elementos<maximo_elementos:
    somatorio_total+=sum(loaded["tempos"][i])
    quantidades+=len(loaded["tempos"][i])
    quantidade_elementos+=incremento
f = open("teste_tempo_execucao_amd64.log", "a")
print("media geração completa "+str(somatorio_total/quantidades)+"\n")
print("media por elemento "+str((somatorio_total/quantidades)/quantidade_elementos)+"\n")
f.write("media geração completa "+str(somatorio_total/quantidades)+"\n")
f.write("media por elemento "+str((somatorio_total/quantidades)/quantidade_elementos)+"\n")
os.remove("teste_tempo_aditional_data_amd64.json")
