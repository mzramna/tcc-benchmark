import time, docker,json
from gerenciadorDeBD import GerenciadorDeBD
from paralelLib import Paralel_pool,Paralel_subprocess,Paralel_thread
#from datetime import datetime

logstash_data={"host":"192.168.0.116","port":5000}
total_elementos=50000
pre_exec=5000
threads_paralel_lv2=10
usuarios_bd=json.loads(open("scripts/usuarios.json").read())

infos_docker=json.loads(open("scripts/infos_docker.json").read())

ordem_executar_teste=["host","database","port","tipo","sql_file_pattern","pre_execucao","total_elementos","total_threads","user","password","compiled_users"]

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

def executar_teste(host,database,port,tipo,sql_file_pattern,pre_execucao=1000,total_elementos=10000,total_threads=3,user="",password="",compiled_users:dict={},recreate:bool=False):
    array=[]
    threads=[]
    if recreate == True:
        try:
            reset=GerenciadorDeBD(host=host, user=user, password=password, database=database, port=port,tipo=tipo,sql_file_pattern=sql_file_pattern,logstash_data=logstash_data,level=40)
            reset.reset_database()
            if tipo == 1:
                reset.execute_sql_file("containers_build/postgres repermission.sql")
            del reset
        except:
            pass
    for _ in range(pre_execucao,total_threads):
        threads.append([])
    for i in range(pre_execucao,total_elementos):
        array.append({"id":i,"sqlite_file":"scripts/initial_db.db"})
    if (isinstance(user, list) and isinstance(password, list) ) or (compiled_users !={}):
        gerenciador=[]
        if compiled_users != {}:
            #criar_usuarios(connect={"host":host, "user":user, "password":password, "database":database, "port":port,"tipo":tipo,"sql_file_pattern":sql_file_pattern,"logstash_data":logstash_data,"level":40}, usuarios=compiled_users, bd=database, root="SafestRootPassword",quantidade=total_threads)
            for i in compiled_users.keys():
                gerenciador.append(GerenciadorDeBD(host=host, user=compiled_users[i]["usuario"], password=compiled_users[i]["senha"], database=database, port=port,tipo=tipo,sql_file_pattern=sql_file_pattern,logstash_data=logstash_data,level=40,autocommit=True))
        elif ( len(user) == len(password) ) and user!="" and password!="":
            for i in range(len(user)):
                gerenciador.append(GerenciadorDeBD(host=host, user=user[i], password=password[i], database=database, port=port,tipo=tipo,sql_file_pattern=sql_file_pattern,logstash_data=logstash_data,level=40))
        if pre_execucao>0:
            gerenciador[0].execute_operation_from_sqlite_no_return(pre_execucao, "scripts/initial_db.db") 
        #criar_usuarios(connect={"host":host, "user":user, "password":password, "database":database, "port":port,"tipo":tipo,"sql_file_pattern":sql_file_pattern,"logstash_data":logstash_data,"level":40}, usuarios=compiled_users, bd=database, root="SafestRootPassword",quantidade=total_threads)
        p=Paralel_subprocess(total_threads=total_threads)
        functions=[]
        for i in gerenciador:
            functions.append(i.execute_operation_from_sqlite_no_return_with_id)
        if host == infos_docker["maquina_arm"]["url"]:
            name_subprocess="arm"
        elif host == infos_docker["maquina_amd"]["url"]:
            name_subprocess="amd"
        p.execute(elementos=array,function=functions,daemon=False,name_subprocess=name_subprocess)
    elif (isinstance(user, str)  and isinstance(password, str) )and (user != "" and password != ""):
        gerenciador=GerenciadorDeBD(host=host, user=user, password=password, database=database, port=port,tipo=tipo,sql_file_pattern=sql_file_pattern,logstash_data=logstash_data,level=40)
         #reset
        gerenciador.reset_database()
        if pre_execucao>0:
            gerenciador.execute_operation_from_sqlite_no_return(pre_execucao, "scripts/initial_db.db") 
        p=Paralel_thread(total_threads=total_threads)
        p.execute(elementos=array,function=gerenciador.execute_operation_from_sqlite_no_return_with_id)
    else:
        return 0

def stop_container(ip:str="",port:int=0,id_:str="",compiled:dict={},id_key=""):
    if compiled != {}:
        client = docker.DockerClient(base_url=compiled["url"]+":"+str(compiled["port_docker_sock"]),version="auto")
        client.containers.get(compiled[id_key]).stop()
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

def start_test(tipo_bd:str,paralel=True,recreate:bool=True):
    start_container(compiled=infos_docker["maquina_arm"],id_key=tipo_bd+"_id")
    start_container(compiled=infos_docker["maquina_amd"],id_key=tipo_bd+"_id")
    try:
        result=[]
        # if recreate:
        #     reset=GerenciadorDeBD(**infos_docker["maquina_arm"][tipo_bd+"_connect"])
        #     reset.reset_database()
        #     reset=GerenciadorDeBD(**infos_docker["maquina_amd"][tipo_bd+"_connect"])
        #     reset.reset_database()
        #     del reset
        # time.sleep(10)
        if paralel == True:
            arm=infos_docker["maquina_arm"][tipo_bd+"_connect"]
            arm["total_elementos"]=total_elementos
            arm["total_threads"]=threads_paralel_lv2
            arm["pre_execucao"]=pre_exec
            arm["compiled_users"]=usuarios_bd
            arm["recreate"]=recreate
            amd=infos_docker["maquina_amd"][tipo_bd+"_connect"]
            amd["total_elementos"]=total_elementos
            amd["total_threads"]=threads_paralel_lv2
            amd["pre_execucao"]=pre_exec
            amd["compiled_users"]=usuarios_bd
            amd["recreate"]=recreate
            dados=[amd,arm]
            p=Paralel_subprocess(total_threads=2)
            result= p.execute(elementos=dados,function=executar_teste,timer=True,name_subprocess="servidor")
        else:
            executar_teste(**infos_docker["maquina_arm"][tipo_bd+"_connect"],total_elementos=total_elementos)
            executar_teste(**infos_docker["maquina_amd"][tipo_bd+"_connect"],total_elementos=total_elementos)
    except:
        pass
    finally:
        stop_container(compiled=infos_docker["maquina_arm"],id_key=tipo_bd+"_id")
        stop_container(compiled=infos_docker["maquina_amd"],id_key=tipo_bd+"_id")
        return result

#executar testes no bd mariadb
#print(start_test("mariadb",paralel=True,recreate=True))

#executar testes no bd postgres
print(start_test("postgres",paralel=True,recreate=True))