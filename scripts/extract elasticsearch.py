from datetime import datetime
from elasticsearch import Elasticsearch ,ApiError
from elasticsearch import helpers
from paralelLib import Paralel_thread
import csv,time

def add_to_csv(value,arquivo):
    with open(arquivo, 'a', newline='\n') as csvfile:
        if type(value) == type([]):
            fieldnames = list(value[0].keys())
        else:
            fieldnames = list(value.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        existingLines = list(csv.reader(open(arquivo, 'r')))
        if len(existingLines)<=0:
            writer.writeheader()
        if type(value) == type([]):
            for i in range(len(value)):
                linha = list(value[i].values())
                for i in range(len(linha)):
                    if linha[i] == None :
                        linha[i]=""
                if linha in existingLines:
                    
                    value[i]=[]
                try:
                    value.remove([])
                except:
                    pass
                writer.writerows(value)
        else:
            linha = list(value.values())
            for i in range(len(linha)):
                if linha[i] == None :
                    linha[i]=""
            if linha in existingLines:
                pass
            else:
                writer.writerow(value)
        csvfile.close()

def processamento_elasticsearch_data(arquivo,t0=0,t1=0,maxsize=100000):
    es = Elasticsearch('http://elastic:changeme@192.168.192.116:9200',http_compress=True,)
    if t0 == t1 == 0:
        t0='2022-02-25T20:30:00.000Z'
        t1='2022-02-26T12:30:00.000Z'
    date1 = datetime.strptime(t0, "%Y-%m-%dT%H:%M:%S.%fZ")
    date2 = datetime.strptime(t1, "%Y-%m-%dT%H:%M:%S.%fZ")
    query={"query" : { "term" : { "logger_name" : arquivo }}}#,"range":{"@timestamp":{"gte":date1,"lt":date2}}}
    # time:(from:'2022-02-25T21:00:00.000Z',to:'2022-02-26T12:00:00.000Z')
    scanResp= helpers.scan(client=es,index="monitoramento",scroll="1d",query=query, request_timeout=3000,raise_on_error=False)
    try:
        dados=[]
        for i in scanResp:
            dados.append(i["_source"])
            if len(dados)==maxsize:
                add_to_csv(dados,arquivo+".csv")
                del dados
                dados=[]
        add_to_csv(dados,arquivo+".csv")
    except ApiError as e:
        pass
    except Exception as e:
        #time.sleep(1)
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