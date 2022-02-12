from os import DirEntry
from geradorDeSql import GeradorDeSql
#logstash_data={"host":"192.168.0.116","port":5000,"username":"elastic","password":"changeme"}
#logstash_data={"host":"192.168.0.116","port":5000}

class Gerar_bd_teste:
    def __init__(self,local_sqlite:DirEntry="scripts/teste_db.db",total_threads=0,logstash_data={}):
        self.total_threads=total_threads
        self.logstash_data=logstash_data
        self.gerador=GeradorDeSql(sqlite_db=local_sqlite,sql_file_pattern="scripts/sqlitePattern.sql", log_file="scripts/geradorSQL.log",level=40,logging_pattern='%(asctime)s - %(name)s - %(levelname)s - %(message)s',logstash_data=logstash_data)

    def executar(self,quantidade_elementos_iniciais_insercao=100,quantidade_elementos_totais=10000):
        if quantidade_elementos_iniciais_insercao>0:
            self.gerador.gerar_todos_dados_por_json_paralel(threads=self.total_threads,select_country="pt_br",tipo=[1],quantidade_final=quantidade_elementos_iniciais_insercao)
            print("gerados dados de inserção")
        if quantidade_elementos_totais>0:
            self.gerador.gerar_todos_dados_por_json_paralel(threads=self.total_threads,select_country="pt_br",quantidade_final=quantidade_elementos_totais)
            print("gerados dados randomicos")

if __name__ == "__main__":
    Gerar_bd_teste(local_sqlite="scripts/initial_db.db").executar()
    