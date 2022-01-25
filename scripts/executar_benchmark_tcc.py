import time, docker
from gerenciadorDeBD import GerenciadorDeBD
from worker import Paralel
#from datetime import datetime

logstash_data={"host":"192.168.0.116","port":5000}
total_elementos=10000
usuarios_bd={
   "usuario1":{
       "usuario":"ibd4bhkjpyi4hx",
       "senha":"mls83mfbsdnvte"
   },
   "usuario2":{
       "usuario":"fhabpsyubkgo7",
       "senha":"chv9jtnv2r98zw"
   },
   "usuario3":{
       "usuario":"rg2dsvhc6ahajz",
       "senha":"vpzg49u3qaeckl"
   },
   "usuario4":{
       "usuario":"cu9c5qycens55v",
       "senha":"lqr9zrhste5ve6"
   },
   "usuario5":{
       "usuario":"vaddpet2mh7hiq",
       "senha":"p3vqtklfgpnver"
   },
   "usuario6":{
       "usuario":"nyq9kedfwus9d",
       "senha":"tcf6mwpy2ixeex"
   },
   "usuario7":{
       "usuario":"loymzy83yf9kub",
       "senha":"jrffhw8kcpxgzg"
   },
   "usuario8":{
       "usuario":"dvjr3ef9uwukby",
       "senha":"wwz54szihhwmie"
   },
   "usuario9":{
       "usuario":"b2cr7y3twxkfzn",
       "senha":"qxeu6hkv9craqb"
   },
   "usuario10":{
       "usuario":"c7f5w3xj54poop",
       "senha":"nwgtnbwup9pltj"
   },
}

infos_docker={
    "maquina_arm":{
        "url":"192.168.0.10",
        "port_docker_sock":2375,
        "mariadb_id":"alpine-mariadb-1",
        "mariadb_connect":{
            "host":"192.168.0.10",
            "user":"mzramna",
            "password":"safePassword",
            "compiled_users":usuarios_bd,
            "database":"sakila",
            "port":3306,
            "tipo":0,
            "sql_file_pattern":"containers_build/mysql default exemple.sql"
            },
        "postgres_id":"alpine-postgres-1",
        "postgres_connect":{
            "host":"192.168.0.10",
            "user":"mzramna",
            "password":"safePassword",
            "database":"sakila",
            "compiled_users":usuarios_bd,
            "port":5432,
            "tipo":1,
            "sql_file_pattern":"containers_build/postgres default exemple.sql"
            },
        },
    "maquina_amd":{
        "url":"192.168.0.20",
        "port_docker_sock":2375,
        "mariadb_id":"alpine-mariadb-1",
        "mariadb_connect":{
            "host":"192.168.0.10",
            "user":"mzramna",
            "password":"safePassword",
            "compiled_users":usuarios_bd,
            "database":"sakila",
            "port":3306,
            "tipo":0,
            "sql_file_pattern":"containers_build/mysql default exemple.sql"
        },
        "postgres_id":"alpine-postgres-1",
        "postgres_connect":{
            "host":"192.168.0.20",
            "user":"mzramna",
            "password":"safePassword",
            "compiled_users":usuarios_bd,
            "database":"sakila",
            "port":5432,
            "tipo":1,
            "sql_file_pattern":"containers_build/postgres default exemple.sql"
        },
        }
    }

def criar_usuarios(connect:dict,usuarios:dict,bd:str,root:str,quantidade:int=1):
    gerenciador=GerenciadorDeBD(**connect)
    tmp=0
    # for i in usuarios.keys():
    #     gerenciador.creat_user(root_pass=root, user=usuarios[i]["usuario"], password=usuarios[i]["senha"],database=bd)
    #     tmp+=1
    #     if tmp>=quantidade:
    #         break
    if connect["tipo"]==0:
        gerenciador.execute_sql_file("containers_build/mysql user creation.sql")
    elif connect["tipo"]==1:
        gerenciador.execute_sql_file("containers_build/postgres user creation.sql")

def executar_teste(host,database,port,tipo,sql_file_pattern,pre_execucao=1000,total_elementos=10000,total_threads=3,user="",password="",compiled_users:dict={}):
    array=[]
    threads=[]
    for _ in range(pre_execucao,total_threads):
        threads.append([])
    for i in range(pre_execucao,total_elementos):
        array.append({"id":i,"sqlite_file":"scripts/initial_db.db"})
    if (isinstance(user, list) and isinstance(password, list) ) or (compiled_users !={}):
        gerenciador=[]
        if compiled_users != {}:
            #criar_usuarios(connect={"host":host, "user":user, "password":password, "database":database, "port":port,"tipo":tipo,"sql_file_pattern":sql_file_pattern,"logstash_data":logstash_data,"level":40}, usuarios=compiled_users, bd=database, root="SafestRootPassword",quantidade=total_threads)
            for i in compiled_users.keys():
                gerenciador.append(GerenciadorDeBD(host=host, user=compiled_users[i]["usuario"], password=compiled_users[i]["senha"], database=database, port=port,tipo=tipo,sql_file_pattern=sql_file_pattern,logstash_data=logstash_data,level=40))
        elif ( len(user) == len(password) ) and user!="" and password!="":
            for i in range(len(user)):
                gerenciador.append(GerenciadorDeBD(host=host, user=user[i], password=password[i], database=database, port=port,tipo=tipo,sql_file_pattern=sql_file_pattern,logstash_data=logstash_data,level=40))
        
        gerenciador[0].reset_database()
        #criar_usuarios(connect={"host":host, "user":user, "password":password, "database":database, "port":port,"tipo":tipo,"sql_file_pattern":sql_file_pattern,"logstash_data":logstash_data,"level":40}, usuarios=compiled_users, bd=database, root="SafestRootPassword",quantidade=total_threads)
        p=Paralel(total_threads=total_threads)
        functions=[]
        for i in gerenciador:
            functions.append(i.execute_operation_from_sqlite_no_return_with_id)
        p.execute(elementos=array,function=functions)
    elif (isinstance(user, str)  and isinstance(password, str) )and (user != "" and password != ""):
        gerenciador=GerenciadorDeBD(host=host, user=user, password=password, database=database, port=port,tipo=tipo,sql_file_pattern=sql_file_pattern,logstash_data=logstash_data,level=40)
         #reset
        gerenciador.reset_database()
        #gerenciador.execute_operation_from_sqlite_no_return(pre_execucao, "scripts/initial_db.db") 
        p=Paralel(total_threads=total_threads)
        p.execute(elementos=array,function=gerenciador.execute_operation_from_sqlite_no_return_with_id)
    else:
        return 0

def stop_container(ip:str="",port:int=0,id_:str="",compiled:dict={},id_key=""):
    if compiled != {}:
        client = docker.DockerClient(base_url=compiled["url"]+":"+str(compiled["port_docker_sock"]),version="auto")
        client.containers.get(compiled[id_key]).start()
    else:
        if ip == "" or port == 0 or id_key == "":
            return None
        client = docker.DockerClient(base_url=ip+":"+str(port),version="auto")
        client.containers.get(id_).stop()

def start_container(ip:str="",port:int=0,id_:str="",compiled:dict={},id_key=""):
    if compiled != {}:
        client = docker.DockerClient(base_url=compiled["url"]+":"+str(compiled["port_docker_sock"]),version="auto")
        client.containers.get(compiled[id_key]).start()
    else:
        if ip == "" or port == 0 or id_key == "":
            return None
        client = docker.DockerClient(base_url=ip+":"+str(port),version="auto")
        client.containers.get(id_).start()

def start_test(tipo_bd:str,paralel=False):
    start_container(compiled=infos_docker["maquina_arm"],id_key=tipo_bd+"_id")
    start_container(compiled=infos_docker["maquina_amd"],id_key=tipo_bd+"_id")
    time.sleep(10)
    if paralel == True:
        arm=infos_docker["maquina_arm"][tipo_bd+"_connect"]
        arm["total_elementos"]=total_elementos
        amd=infos_docker["maquina_amd"][tipo_bd+"_connect"]
        amd["total_elementos"]=total_elementos
        dados=[arm,amd]
        p=Paralel(total_threads=2)
        p.execute(elementos=dados,function=executar_teste)
    else:
        executar_teste(**infos_docker["maquina_arm"][tipo_bd+"_connect"],total_elementos=total_elementos)
        executar_teste(**infos_docker["maquina_amd"][tipo_bd+"_connect"],total_elementos=total_elementos)
    stop_container(compiled=infos_docker["maquina_arm"],id_key=tipo_bd+"_id")
    stop_container(compiled=infos_docker["maquina_amd"],id_key=tipo_bd+"_id")

#executar testes no bd mariadb
start_test("mariadb",paralel=False)

#executar testes no bd postgres
start_test("postgres",paralel=False)