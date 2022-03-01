from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import csv
es = Elasticsearch('http://elastic:changeme@192.168.192.116:9200',http_compress=True)
def add_to_csv(value,arquivo):
    with open(arquivo, 'a', newline='\n') as csvfile:
        fieldnames = list(value.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        reader = csv.reader(open(arquivo, 'r'))
        if len(list(reader))<=0:
            writer.writeheader()
        del reader
        writer.writerow(value)
        csvfile.close()
doc = {
    'author': 'author_name',
    'text': 'Interensting content...',
    'timestamp': datetime.now(),
}
print(es.info())

aliases = es.indices.get_alias()
# for i in aliases:
#     print(i)
arquivos=["container_postgres_armhf","container_mariadb_armhf","container_postgres_amd","container_mariadb_amd"]
temp_index="monitoramento"
mapping=es.indices.get_mapping(index=temp_index)[temp_index]['mappings']['properties'].keys()
print(mapping)
scanResp= helpers.scan(client=es,scroll="10m", request_timeout=3000)
print(scanResp)
cont=0
for i in scanResp:
        if i['_index'] == "monitoramento":
            print(i)
            for logger in arquivos:
                if i["_source"]["logger_name"]==logger:
                    linha=i["_source"]
                    add_to_csv(linha,logger+".csv")
            cont+=1
            if str(cont)[-3:]=="000":
                print(cont)

print(cont)
if cont == 1640376 or cont == 1640375 or cont == 1640377:
    print("completo")
#print(resp['result'])