from datetime import datetime
from elasticsearch import Elasticsearch ,ApiError
from elasticsearch import helpers
from paralelLib import Paralel_thread
from more_itertools import unique_everseen
import csv,os,ast
import re,time
import shutil
import gc
import psutil


def add_to_csv(value,arquivo,fieldnames=[],processar=False):
    with open(arquivo, 'a', newline='\n') as csvfile:
        if fieldnames == []:
            if type(value) == type([]):
                fieldnames = list(value[0].keys())
            else:
                fieldnames = list(value.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        existingLines = list(csv.reader(open(arquivo, 'r')))
        if len(existingLines)<=0:
            writer.writeheader()
        if type(value) == type([]):
            #for i in range(len(value)):
                #linha = list(value[i].values())
                #for i in range(len(linha)):
                #    if linha[i] == None :
                #        linha[i]=""
                #if linha in existingLines:
                #    value[i]=[]
                #try:
                #    value.remove([])
                #except:
                #    pass
            if processar==True:
                for linha in value:
                    writer.writerow(processamento_automatico(linha))
            else:
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

def processamento_automatico(linha):
        tmp_result={}
        #tmp_result["logger_name"]=linha["logger_name"]
        tmp_result["@timestamp"]=linha["@timestamp"]
        tmp_dict=linha["disk_io_counters"]
        for dado in tmp_dict:
            pattern = r"(\w+)=([0-9]+),"
            tmp_dict_2={}
            for m in re.findall(pattern=pattern,string= re.search(r'sdiskio\((.*)\)',tmp_dict[dado]).group(1)):
                tmp_dict_2[dado+"_"+m[0]]=int(m[1])
            tmp_result[dado+"_read_bytes"]=tmp_dict_2[dado+"_read_bytes"]
            tmp_result[dado+"_write_bytes"]=tmp_dict_2[dado+"_write_bytes"]
            tmp_dict_2={}
        tmp_dict=linha["cpu_percent"]
        cpu_dict={}
        for dado in range(len( tmp_dict)):
            cpu_dict[list(tmp_dict.keys())[dado]]=tmp_dict[list(tmp_dict.keys())[dado]]
            tmp_result[list(tmp_dict.keys())[dado]]=tmp_dict[list(tmp_dict.keys())[dado]]
        #tmp_result["cpu_percent"]=cpu_dict
        tmp_dict=linha["virtual_memory"]
        tmp_dict_2={}
        for dado in tmp_dict:
            tmp_dict_2[dado]=tmp_dict[dado]
        tmp_result["ram_used"]=tmp_dict_2["used"]
        tmp_result["ram_available"]=tmp_dict_2["available"]
        tmp_result["container_root_usage_percent"]=linha["disk_usage"]["percent"]
        tmp_dict=linha["net_io_counters"]
        tmp_dict_2={}
        for dado in tmp_dict:
            tmp_dict_2[dado]=tmp_dict[dado]
        tmp_result["net_bytes_recv"]=tmp_dict_2["bytes_recv"]
        tmp_result["net_bytes_sent"]=tmp_dict_2["bytes_sent"]
        return tmp_result

def processamento_elasticsearch_data(arquivo,t0=0,t1=0,url="http://elastic:changeme@192.168.0.116:9200",remove_duplicate=True,remove_old=True,processar=True,ram_usage:float=95):
    es = Elasticsearch(url,http_compress=True,)
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
        dados_cont=0
        for i in scanResp:
            if processar==True:
                dados.append(processamento_automatico(i["_source"]))
            else:
                dados.append(i["_source"])
            # if len(dados)==maxsize:
            #     add_to_csv(dados,arquivo+".csv")
            #     del dados
            #     dados=[]
            dados_cont+=1
            #if str(dados_cont)[-6:] in ["500000","000000"]:
            ram_percent=psutil.virtual_memory().percent
            if ram_percent>=ram_usage:
                 print(dados_cont)
                 add_to_csv(dados,arquivo+".csv",processar=(not processar))
                 dados=[dados[-1]]
                 gc.collect()
        # if len(dados)==1640376:
        #     print("completo")
        add_to_csv(dados,arquivo+".csv")#fieldnames=['@timestamp', 'cpu_percent_0', 'cpu_percent_1',  'cpu_percent_2', 'cpu_percent_3','ram_available', 'net_bytes_recv', 'sda_read_bytes', 'sda_write_bytes', 'net_bytes_sent','container_root_usage_percent', 'ram_used']
        del dados
    except ConnectionError as e:
        time.sleep(30)
        del dados
        del es
        del query
        gc.collect()
        processamento_elasticsearch_data(arquivo,t0,t1,url,remove_duplicate,remove_old,processar)
    except ApiError as e:
        time.sleep(60)
        del dados
        del es
        del query
        gc.collect()
        processamento_elasticsearch_data(arquivo,t0,t1,url,remove_duplicate,remove_old,processar)
    except Exception as e:
        #time.sleep(1)
        pass
    gc.collect()
    if remove_duplicate==True:
        remove_duplicate_file(arquivo+".csv","./"+arquivo+"_limpo.csv")
        sort_csv("./"+arquivo+"_limpo.csv","@timestamp")
    else:
        sort_csv("./"+arquivo+".csv","@timestamp")
    if remove_old==True:
        os.remove(arquivo+".csv")

def remove_duplicate_file(infile,outfile):
    with open(infile,'r') as f, open(outfile,'w') as out_file:
        out_file.writelines(unique_everseen(f))

def sort_csv(infile,sort_by):
    with open(infile,newline='') as csvfile:
        a=[]
        for row in csv.DictReader(csvfile, skipinitialspace=True):
            a.append(row)
        headers=list(a[0].keys())
        csvfile.close()
    sortedlist=sorted(a, key=lambda d: d[sort_by])

    with open("./tmp.csv", 'w') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in sortedlist:
            writer.writerow(row)
        f.close()
    shutil.move("./tmp.csv",infile)


if __name__ == "__main__":
    arquivos=["container_postgres_armhf","container_mariadb_armhf","container_postgres_amd","container_mariadb_amd"]
    url="http://elastic:changeme@192.168.0.116:9200"
    remove_duplicate=False
    remove_old=False
    sequential=False
    ram_usage=95
    # dados=[]
    if sequential==True:
        for i in arquivos:
            print(i)
            processamento_elasticsearch_data(i,remove_duplicate=remove_duplicate,remove_old=remove_old,url=url,ram_usage=ram_usage)
    else:
        dados=[]
        for i in arquivos:
            dados.append({"arquivo":i,"url":url,"remove_duplicate":remove_duplicate,"remove_old":remove_old,"ram_usage":ram_usage})
        p=Paralel_thread(total_threads=2,join=True)
        p.execute(elementos=dados,function=processamento_elasticsearch_data)
    #import manipular_dump_elasticsearch
    #import altair as alt

    #arquivos=["container_postgres_armhf","container_mariadb_armhf","container_postgres_amd","container_mariadb_amd"]

    #arquivos=os.listdir("./")
    #for arquivo in arquivos:
        #if arquivo.endswith(".csv") and not arquivo.endswith("_processado.csv"):
            #manipular_dump_elasticsearch.filtrar_csv_util(os.path.join("./", arquivo),os.path.join("./", arquivo[:-4]+"_processado.csv"))

    #arquivos=os.listdir("./")
    #resize = alt.selection_interval(bind='scales')
    #resultados=[]
    #for arquivo in arquivos:
        #if arquivo.endswith("_processado.csv"):
            #resultados.append(manipular_dump_elasticsearch.plot_graphs(os.path.join("./",arquivo),jpg=False,html=True,save=True,show=False,resize=resize))

    #final=alt.hconcat(*resultados)
    #final.save("dados do container concatenados.html",embed_options={'renderer':'svg'})
