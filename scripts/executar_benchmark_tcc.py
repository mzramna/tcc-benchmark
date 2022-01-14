from gerenciadorDeBD import GerenciadorDeBD
from worker import Paralel
import docker
from datetime import datetime


logstash_data={"host":"192.168.0.116","port":5000}

def executar_teste(ip,user,password,database,port,tipo,sql_file,total_elementos=10000,total_threads=5):
    array=[]
    threads=[]
    for _ in range(total_threads):
        threads.append([])
    for i in range(total_elementos):
        array.append({"id":i,"sqlite_file":"scripts/initial_db.db"})
    gerenciador=GerenciadorDeBD(host=ip, user=user, password=password, database=database, port=port,tipo=tipo,sql_file_pattern=sql_file,logstash_data=logstash_data,level=40)
    #reset
    gerenciador.reset_database()

    p=Paralel(total_threads=total_threads)

    p.execute(elementos=array,function=gerenciador.execute_operation_from_sqlite_no_return_with_id)

#executar testes no bd mariadb
executar_teste(ip="192.168.0.100",user="mzramna",password="safePassword",database="sakila",port=3306,tipo=0,sql_file="containers_build/mysql default exemple.sql",)
#executar testes no bd postgres
executar_teste(ip="192.168.0.100",user="mzramna",password="safePassword",database="sakila",port=5432,tipo=1,sql_file="containers_build/postgres default exemple.sql")

##criar metodos para alternar os containers ligados
client = docker.DockerClient(base_url="192.168.0.100:2375",version="auto")
