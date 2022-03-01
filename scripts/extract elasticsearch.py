from datetime import datetime
from elasticsearch import Elasticsearch ,ApiError
from elasticsearch import helpers
from paralelLib import Paralel_thread
import csv,time

def add_to_csv(value,arquivo):
    with open(arquivo, 'a', newline='\n') as csvfile:
        fieldnames = list(value.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        existingLines = list(csv.reader(open(arquivo, 'r')))
        if len(existingLines)<=0:
            writer.writeheader()
        linha = list(value.values())
        for i in range(len(linha)):
            if linha[i] == None :
                linha[i]=""
        if linha in existingLines:
            pass
        else:
            writer.writerow(value)
        
        csvfile.close()

def processamento_elasticsearch_data(arquivo):
    es = Elasticsearch('http://elastic:changeme@192.168.192.116:9200',http_compress=True,)
    scanResp= helpers.scan(client=es,index="monitoramento",scroll="1d",query={"query" : { "term" : { "logger_name" : arquivo }}}, request_timeout=3000,raise_on_error=False)
    try:
        for i in scanResp:
            if i['_index'] == "monitoramento" and i["_source"]["logger_name"]==arquivo:
            # print(i)
                linha=i["_source"]
                add_to_csv(linha,arquivo+".csv")
    except ApiError as e:
        pass
    except Exception as e:
        time.sleep(1)
        pass



# for i in aliases:
#     print(i)
arquivos=["container_postgres_armhf","container_mariadb_armhf","container_postgres_amd","container_mariadb_amd"]

dados=[]
for i in arquivos:
    dados.append({"arquivo":i})
p=Paralel_thread(total_threads=4,join=True)
p.execute(elementos=dados,function=processamento_elasticsearch_data)
# print(cont)
# if cont == 1640376 or cont == 1640375 or cont == 1640377:
#     print("completo")