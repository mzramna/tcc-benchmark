from gerenciadorDeBD import GerenciadorDeBD
from worker import Paralel
import docker
from datetime import datetime


logstash_data={"host":"192.168.0.116","port":5000}
infos_docker={
    "maquina_arm":{
        "url":"192.168.0.10",
        "port_docker_sock":2375,
        "mariadb_id":"alpine-mariadb-1",
        "mariadb_connect":{
            "ip":"192.168.0.10",
            "user":"mzramna",
            "password":"safePassword",
            "database":"sakila",
            "port":3306,
            "tipo":0,
            "sql_file":"containers_build/mysql default exemple.sql"
        },
        "postgres_id":"alpine-postgres-1",
        "postgres_connect":{
            "ip":"192.168.0.10",
            "user":"mzramna",
            "password":"safePassword",
            "database":"sakila",
            "port":5432,
            "tipo":1,
            "sql_file":"containers_build/postgres default exemple.sql"
        },
        },
    "maquina_amd":{
        "url":"192.168.0.20",
        "port_docker_sock":2375,
        "mariadb_id":"alpine-mariadb-1",
        "mariadb_connect":{
            "ip":"192.168.0.10",
            "user":"mzramna",
            "password":"safePassword",
            "database":"sakila",
            "port":3306,
            "tipo":0,
            "sql_file":"containers_build/mysql default exemple.sql"
        },
        "postgres_id":"alpine-postgres-1",
        "postgres_connect":{
            "ip":"192.168.0.20",
            "user":"mzramna",
            "password":"safePassword",
            "database":"sakila",
            "port":5432,
            "tipo":1,
            "sql_file":"containers_build/postgres default exemple.sql"
        },
        }
    }
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

def stop_container(ip:str="",port:int=0,id:str="",compiled:dict={},id_key=""):
    if compiled != {}:
        client = docker.DockerClient(base_url=compiled["url"]+":"+str(compiled["port_docker_sock"]),version="auto")
        client.containers.get(compiled[id_key]).start()
    else:
        if ip == "" or port == 0 or id_key == "":
            return None
        client = docker.DockerClient(base_url=ip+":"+str(port),version="auto")
        client.containers.get(compiled[id]).stop()

def start_container(ip:str="",port:int=0,id:str="",compiled:dict={},id_key=""):
    if compiled != {}:
        client = docker.DockerClient(base_url=compiled["url"]+":"+str(compiled["port_docker_sock"]),version="auto")
        client.containers.get(compiled[id_key]).start()
    else:
        if ip == "" or port == 0 or id_key == "":
            return None
        client = docker.DockerClient(base_url=ip+":"+str(port),version="auto")
        client.containers.get(compiled[id]).start()

def start_test(tipo_bd:str,paralel=False):
    start_container(compiled=infos_docker["maquina_arm"],id_key=tipo_bd+"_id")
    start_container(compiled=infos_docker["maquina_amd"],id_key=tipo_bd+"_id")
    if paralel == True:
        dados={infos_docker["maquina_arm"][tipo_bd+"_connect"],infos_docker["maquina_amd"][tipo_bd+"_connect"]}
        p=Paralel(total_threads=2)
        p.execute(elementos=dados,function=executar_teste)
    else:
        executar_teste(**infos_docker["maquina_arm"][tipo_bd+"_connect"])
        executar_teste(**infos_docker["maquina_amd"][tipo_bd+"_connect"])
    stop_container(compiled=infos_docker["maquina_arm"],id_key=tipo_bd+"_id")
    stop_container(compiled=infos_docker["maquina_amd"],id_key=tipo_bd+"_id")

#executar testes no bd mariadb
start_test("mariadb")

#executar testes no bd postgres
start_test("postgres")