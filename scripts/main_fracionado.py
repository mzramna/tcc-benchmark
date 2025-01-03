from geração_bd_testes import Gerar_bd_teste
from executar_benchmark_tcc import Executar_benchmark
import json
threads=0
adicao=5000
bd_teste="scripts/teste_db.db"
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
    quantidade_subprocessos=1
    valores_benchmark["valores_execucao"]={ "valor_inicial":valor_inicial ,"valor_final":valor_final, "valor_max":valor_max,"quantidade_subprocessos":quantidade_subprocessos }

if quantidade_subprocessos<2:
    benchmark=Executar_benchmark(sqlite_bd=bd_teste,recreate=False,threads_paralel_lv2=quantidade_subprocessos,threads_pct_timeout_lv2=1,threads_timeout_lv2=6)
else:
    benchmark=Executar_benchmark(sqlite_bd=bd_teste,recreate=False,threads_paralel_lv2=quantidade_subprocessos,threads_pct_timeout_lv2=0.5,threads_timeout_lv2=6)

if valor_inicial == 0:
    benchmark.reset_bd_full()
with open(retorno, "w") as out_file:
    json.dump(valores_benchmark, out_file)
    out_file.close()
while valor_final<=valor_max:
    #benchmark.reset_bd_full()
    gerados_sqlite.executar(quantidade_elementos_iniciais_insercao=valor_inicial,quantidade_elementos_totais=valor_final)
    # benchmark=Executar_benchmark(sqlite_bd=bd_teste,recreate=False,threads_paralel_lv2=4)
    resultado_benchmark=benchmark.executar(total_elementos=valor_final,pre_execucao=valor_inicial,pre_exec=False)
    # del benchmark
    tmp={"valor_final":valor_final,"postgres":resultado_benchmark[0],"mariadb":resultado_benchmark[1],"subprocessos":quantidade_subprocessos}
    valores_benchmark["valor_final_"+str(valor_final)+"_"+str(quantidade_subprocessos)]=tmp
    print(tmp)
    valores_benchmark["valores_execucao"]={"valor_inicial":valor_inicial,"valor_final":valor_final,"valor_max":valor_max,"quantidade_subprocessos": quantidade_subprocessos}
    with open(retorno, "w") as out_file:
        json.dump(valores_benchmark, out_file)
        out_file.close()
    valor_inicial=valor_final
    valor_final+=adicao

del benchmark
#valor_final=5000
# valores_benchmark["valores_execucao"]={"valor_inicial":valor_inicial,"valor_final":valor_final,"valor_max":valor_max,"quantidade_subprocessos": quantidade_subprocessos}
# with open(retorno, "w") as out_file:
#     json.dump(valores_benchmark, out_file)
#     out_file.close()
