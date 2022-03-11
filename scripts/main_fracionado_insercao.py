from geração_bd_testes import Gerar_bd_teste
from executar_benchmark_tcc import Executar_benchmark
import json
import os
import manipular_dump_elasticsearch
import extract_elasticsearch
import altair as alt

threads=int(os.cpu_count()/2)
threads=int(os.cpu_count())/2
adicao=5000
bd_teste="scripts/main_fracionado_insercao_db.db"
gerados_sqlite=Gerar_bd_teste(local_sqlite=bd_teste,total_threads=threads)
#fracionado
retorno="valores_tempo_velocidade_benchmark_fracionado.json"
try:
    valores_benchmark=json.loads(open(retorno,"r").read())
except:
    with open(retorno, "w") as out_file:
        json.dump({}, out_file)
        out_file.close()
    valores_benchmark=json.loads(open(retorno,"r").read())
if "valores_execucao" in valores_benchmark.keys():
    valor_inicial=valores_benchmark["valores_execucao"]["valor_inicial"]+adicao
    valor_final=valores_benchmark["valores_execucao"]["valor_final"]+adicao
    valor_max=valores_benchmark["valores_execucao"]["valor_max"]
    quantidade_subprocessos=valores_benchmark["valores_execucao"]["quantidade_subprocessos"]
else:
    valor_inicial=0
    valor_final=10000
    valor_max=100000
    quantidade_subprocessos=int(os.cpu_count()/2)
    valores_benchmark["valores_execucao"]={ "valor_inicial":valor_inicial ,"valor_final":valor_final, "valor_max":valor_max,"quantidade_subprocessos":quantidade_subprocessos }

if quantidade_subprocessos<2:
    benchmark=Executar_benchmark(sqlite_bd=bd_teste,recreate=False,threads_paralel_lv2=quantidade_subprocessos,threads_pct_timeout_lv2=1,threads_timeout_lv2=6,logstash_data={"host":"192.168.0.116","port":5000,"level":40})
else:
    benchmark=Executar_benchmark(sqlite_bd=bd_teste,recreate=False,threads_paralel_lv2=quantidade_subprocessos,threads_pct_timeout_lv2=0.5,threads_timeout_lv2=6,logstash_data={"host":"192.168.0.116","port":5000,"level":40})

if valor_inicial == 0:
    benchmark.reset_bd_full()
    gerados_sqlite.executar(quantidade_elementos_iniciais_insercao=valor_max)
with open(retorno, "w") as out_file:
    json.dump(valores_benchmark, out_file)
    out_file.close()
while valor_final<=valor_max:
    #benchmark.reset_bd_full()
    # benchmark=Executar_benchmark(sqlite_bd=bd_teste,recreate=False,threads_paralel_lv2=4)
    resultado_benchmark=benchmark.executar(pre_execucao=valor_inicial,total_elementos=valor_final,pre_exec=False,timer_geral=False)
    # del benchmark
    tmp={"valor_final":valor_final,"postgres":resultado_benchmark[0],"mariadb":resultado_benchmark[1],"subprocessos":quantidade_subprocessos}
    valores_benchmark["valor_final_"+str(valor_final)+"_"+str(quantidade_subprocessos)]=tmp
    print(tmp)
    valores_benchmark["valores_execucao"]={"valor_inicial":valor_inicial,"valor_final":valor_final,"valor_max":valor_max,"quantidade_subprocessos": quantidade_subprocessos}
    with open(retorno, "w") as out_file:
                json.dump(valores_benchmark, out_file,indent=4)
                out_file.close()
    valor_inicial=valor_final
    valor_final+=adicao

del benchmark

arquivos=["container_postgres_armhf","container_mariadb_armhf","container_postgres_amd","container_mariadb_amd"]

for i in arquivos:
    extract_elasticsearch.processamento_elasticsearch_data(i)

arquivos=os.listdir("./")
for arquivo in arquivos:
    if arquivo.endswith(".csv") and not arquivo.endswith("_processado.csv"):
        manipular_dump_elasticsearch.filtrar_csv_util(os.path.join("./", arquivo),os.path.join("./", arquivo[:-4]+"_processado.csv"))

arquivos=os.listdir("./")
resize = alt.selection_interval(bind='scales')
resultados=[]
for arquivo in arquivos:
    if arquivo.endswith("_processado.csv"):
        resultados.append(manipular_dump_elasticsearch.plot_graphs(os.path.join("./",arquivo),jpg=False,html=True,save=True,show=False,resize=resize))

final=alt.hconcat(*resultados)
final.save("dados do container concatenados.html",embed_options={'renderer':'svg'})