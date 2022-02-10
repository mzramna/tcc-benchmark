from geração_bd_testes import Gerar_bd_teste
from executar_benchmark_tcc import Executar_benchmark
import json
threads=0
bd_teste="scripts/teste_db.db"
adicional=5000
gerados_sqlite=Gerar_bd_teste(local_sqlite=bd_teste,total_threads=threads)
retorno="valores_tempo_velocidade_benchmark.json"
try:
    valores_benchmark=json.loads(open(retorno,"r").read())
except:
    with open(retorno, "w") as out_file:
        json.dump({}, out_file)
        out_file.close()
    valores_benchmark=json.loads(open(retorno,"r").read())
if "valores_execucao" in valores_benchmark.keys():
    valor_inicial=valores_benchmark["valores_execucao"]["valor_inicial"]+adicional
    valor_final=valores_benchmark["valores_execucao"]["valor_final"]+adicional
    valor_max=valores_benchmark["valores_execucao"]["valor_max"]
else:
    valor_inicial=0
    valor_final=5000
    valor_max=100000
# benchmark=Executar_benchmark(sqlite_bd=bd_teste,recreate=False,threads_paralel_lv2=0)
# if valor_inicial == 0:
    # benchmark.reset_bd_full()
with open(retorno, "w") as out_file:
        json.dump(valores_benchmark, out_file)
        out_file.close()
# del benchmark
while valor_final<=valor_max:
    benchmark=Executar_benchmark(sqlite_bd=bd_teste,recreate=False,threads_paralel_lv2=0)
    gerados_sqlite.executar(quantidade_elementos_iniciais_insercao=valor_inicial,quantidade_elementos_totais=valor_final)
    
    resultado_benchmark=benchmark.executar(total_elementos=valor_final,pre_execucao=valor_inicial,pre_exec=False)
    del benchmark
    tmp={"postgres":resultado_benchmark[0],"mariadb":resultado_benchmark[1]}
    valores_benchmark["valor_final"+str(valor_max)]=tmp
    print(tmp)
    valores_benchmark["valores_execucao"]={"valor_inicial":valor_inicial,"valor_final":valor_final,"valor_max":valor_max}
    with open(retorno, "w") as out_file:
        json.dump(valores_benchmark, out_file)
        out_file.close()
    valor_inicial=valor_final
    valor_final+=adicional