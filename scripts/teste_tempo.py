from geradorDeSql import GeradorDeSql
from pprint import pprint
from random import randint, random,uniform,choice
import os
import time


class TimerError(Exception):

    """A custom exception used to report errors in use of Timer class"""


class Timer:

    def __init__(self):

        self._start_time = None


    def inicio(self):

        """Start a new timer"""

        if self._start_time is not None:

            raise TimerError(f"Timer is running. Use .stop() to stop it")


        self._start_time = time.perf_counter()


    def fim(self,print_=False):

        """Stop the timer, and report the elapsed time"""

        if self._start_time is None:

            raise TimerError(f"Timer is not running. Use .start() to start it")


        elapsed_time = time.perf_counter() - self._start_time

        self._start_time = None
        if print_:
            print(f"Elapsed time: {elapsed_time:0.4f} seconds")
        return float(f"{elapsed_time:0.6f}")

#logstash_data={"host":"192.168.0.116","port":5000,"username":"elastic","password":"changeme"}
#logstash_data={"host":"192.168.0.116","port":5000}
logstash_data={}
tempos=[]
quantidade_elementos=0
for k in range(30):
    tempo=[]
    quantidade_elementos+=100
    for i in range(4):
        timer=Timer()
        f = open("teste_tempo_execucao.log", "a")
        try:
            os.remove("scripts/teste_tempo_db.db")
        except:
            pass
        timer.inicio()
        gerador=GeradorDeSql(sqlite_db="scripts/teste_tempo_db.db",sql_file_pattern="scripts/sqlitePattern.sql", log_file="scripts/teste_tempo.log",level=40,logging_pattern='%(asctime)s - %(name)s - %(levelname)s - %(message)s',logstash_data=logstash_data)

        gerador.gerar_todos_dados_por_json(select_country="pt_br",quantidade_final=quantidade_elementos)

        duracao=timer.fim()
        tempo.append(duracao)
        print(duracao)
        f.write(str(duracao)+"\n")
        f.close()
        del gerador
    #pprint(tempos)
    tempos.append(tempo)
    f = open("teste_tempo_execucao.log", "a")
    print("para ",quantidade_elementos," dados foram gastos os seguintes dados de tempo")
    print("media geração completa ",str(sum(tempo)/len(tempo)))
    print("media por elemento ",str((sum(tempo)/len(tempo))/quantidade_elementos))
    f.write("para "+str(quantidade_elementos)+" dados foram gastos os seguintes dados de tempo"+"\n")
    f.write("media geração completa "+str(sum(tempo)/len(tempo))+"\n")
    f.write("media por elemento "+str((sum(tempo)/len(tempo))/quantidade_elementos)+"\n")
quantidade_elementos=0
somatorio_total=0
quantidades=0
for i in range(30):
    somatorio_total+=sum(tempos[i])
    quantidades+=len(tempos[i])
    quantidade_elementos+=100
f = open("teste_tempo_execucao.log", "a")
print("media geração completa "+str(somatorio_total/quantidades)+"\n")
print("media por elemento "+str((somatorio_total/quantidades)/quantidade_elementos)+"\n")
f.write("media geração completa "+str(somatorio_total/quantidades)+"\n")
f.write("media por elemento "+str((somatorio_total/quantidades)/quantidade_elementos)+"\n")

