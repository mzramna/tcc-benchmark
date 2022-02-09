from geração_bd_testes import Gerar_bd_teste
from executar_benchmark_tcc import Executar_benchmark
import json
threads=0
bd_teste="scripts/teste_db.db"
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
    valor_inicial=valores_benchmark["valores_execucao"]["valor_inicial"]
    valor_final=valores_benchmark["valores_execucao"]["valor_final"]
    valor_max=valores_benchmark["valores_execucao"]["valor_max"]
else:
    valor_inicial=20
    valor_final=100000
    valor_max=1000

with open(retorno, "w") as out_file:
        json.dump(valores_benchmark, out_file)
        out_file.close()

while valor_max<valor_final:
    benchmark=Executar_benchmark(total_elementos=valor_max,sqlite_bd=bd_teste).executar()
    valores_benchmark["valor_final"+str(valor_max)]={"postgres":benchmark[0],"mariadb":benchmark[1]}
    print(benchmark)
    valores_benchmark["valores_execucao"]={"valor_inicial":valor_inicial,"valor_final":valor_final,"valor_max":valor_max}
    with open(retorno, "w") as out_file:
        json.dump(valores_benchmark, out_file)
        out_file.close()
    valor_max+=1000