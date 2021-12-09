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
        
        try:
            os.remove("scripts/initial_db.db")
        except:
            pass
        inicio=time()
        gerador=GeradorDeSql(sqlite_db="scripts/initial_db.db",sql_file_pattern="scripts/sqlitePattern.sql", log_file="scripts/geradorSQL.log",level=10,logging_pattern='%(asctime)s - %(name)s - %(levelname)s - %(message)s',logstash_data=logstash_data)

        gerador.gerar_todos_dados_por_json(select_country="pt_br",quantidade_ciclo=1,total_ciclos=100,quantidade_final=quantidade_elementos)
        #gerador.gerar_dados_validos_por_json(table="actor",tipo=1,select_country="pt_br",quantidade=10)#create
        #gerador.gerar_dados_validos_por_json(table="actor",tipo=2,select_country="pt_br",quantidade=10)#leitura completa
        #gerador.gerar_dados_validos_por_json(table="actor",tipo=3,select_country="pt_br",quantidade=10)#busca
        #gerador.gerar_dados_validos_por_json(table="actor",tipo=4,select_country="pt_br",quantidade=10,dado_existente=True)#busca filtrada
        #gerador.gerar_dados_validos_por_json(table="actor",tipo=5,select_country="pt_br",quantidade=10,dado_existente=True)#edição
        # gerador.gerar_dados_validos_por_json(table="actor",tipo=6,select_country="pt_br",quantidade=10,dado_existente=True)#deleção

        #pprint(gerador.read_contadores())
        fim=time()
        tempo.append(fim-inicio)
        print(fim-inicio)
        del gerador
    #pprint(tempos)
    tempos.append(tempo)
    print("para ",quantidade_elementos," dados foram gastos os seguintes dados de tempo")
    print("media geração completa",sum(tempo)/len(tempo))
    print("media por elemento",(sum(tempo)/len(tempo))/quantidade_elementos)
    
quantidade_elementos=0
for i in range(30):
    quantidade_elementos+=100
print("media geração completa",sum(tempos)/len(tempos))
print("media por elemento",(sum(tempos)/len(tempos))/quantidade_elementos)
#dados_retornados=gerador.processamento_sqlite.read_operacoes(filtro={"nomeBD":"actor"})
#dados_separados=[[] for x in range(0,7)]
#for i in dados_retornados:
#    dados_separados[i["tipoOperacao"]].append(i)
#for i in range(1,7):
#    tmp=choice(dados_separados[i])
#    pprint(tmp)
#    print(gerador.generate_SQL_command_from_data(data=tmp))
