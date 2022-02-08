import time, docker,json,string
from random import choice
from os import DirEntry
from gerenciadorDeBD import GerenciadorDeBD
from paralelLib import Paralel_pool,Paralel_subprocess,Paralel_thread
#from datetime import datetime

logstash_data={"host":"192.168.0.116","port":5000}
total_elementos=1000
pre_exec=10
threads_paralel_lv2=10
quantidade_usuarios=2
usuarios_bd=json.loads(open("scripts/usuarios.json").read())

infos_docker=json.loads(open("scripts/infos_docker.json").read())


def gerador_usuarios(arquivo:DirEntry,quantidade:int,tamanho:int=10):
    valores = string.ascii_lowercase + string.digits
    usuarios_cadastrados=json.loads(open(arquivo).read())
    for q in range(quantidade+1):
        if q<=len(usuarios_cadastrados.keys()):
            pass
        else:
            tmp={"usuario":"","senha":""}
            for j in ["usuario","senha"]:
                gerado = ''
                for i in range(tamanho):
                    if i ==0:
                        gerado += choice(valores)
                        while gerado[0] in string.digits:
                            gerado = choice(valores)
                    else:
                        gerado += choice(valores)
                tmp[j]=gerado
            usuarios_cadastrados["usuario"+str(q)]=tmp
    json.dump(usuarios_cadastrados,open(arquivo,"w"))

def cadastrar_usuarios(connect:dict,usuarios:dict,bd:str,root:str,quantidade:int=-1):
    gerenciador=GerenciadorDeBD(**connect)
    tmp=0
    if quantidade>len(usuarios.keys()):
        gerador_usuarios("scripts/usuarios.json",quantidade=quantidade)
        usuarios=json.loads(open("scripts/usuarios.json").read())
    for i in usuarios.keys():
        gerenciador.creat_user(root_pass=root, user=usuarios[i]["usuario"], password=usuarios[i]["senha"],database=bd)
        tmp+=1
        if tmp==quantidade and quantidade>-1:
            break


def executar_teste(host,database,port,tipo,sql_file_pattern,pre_execucao=1000,total_elementos=10000,total_threads=3,user:str="",password:str="",compiled_users:dict={},recreate:bool=False,total_users:int=-1
                   ):
    array=[]
    threads=[]
    if recreate == True:
        try:
            reset=GerenciadorDeBD(host=host, user=user, password=password, database=database, port=port,tipo=tipo,sql_file_pattern=sql_file_pattern,logstash_data=logstash_data,level=40)
            time.sleep(10)
            reset.reset_database()
            del reset
        except:
            pass
    for _ in range(pre_execucao,total_threads):
        threads.append([])
    for i in range(pre_execucao,total_elementos):
        array.append({"id":i,"sqlite_file":"scripts/initial_db.db"})
    if compiled_users !={}:
        gerenciador=[]
        #if recreate==True:
        gerador_usuarios("scripts/usuarios.json",total_threads)
        cadastrar_usuarios(connect={"host":host, "user":user, "password":password, "database":database, "port":port,"tipo":tipo,"sql_file_pattern":sql_file_pattern,"logstash_data":logstash_data,"level":40}, usuarios=compiled_users, bd=database, root="SafestRootPassword")
        for i in compiled_users.keys():
            gerenciador.append(GerenciadorDeBD(host=host, user=compiled_users[i]["usuario"], password=compiled_users[i]["senha"], database=database, port=port,tipo=tipo,sql_file_pattern=sql_file_pattern,logstash_data=logstash_data,level=40,autocommit=True))
            if total_users>-1 and len(gerenciador) == total_users:
                break
        if pre_execucao>0:
            gerenciador[0].execute_operation_from_sqlite_no_return(pre_execucao, "scripts/initial_db.db") 
        p=Paralel_subprocess(total_threads=total_threads)
        functions=[]
        for i in gerenciador:
            functions.append(i.execute_operation_from_sqlite_no_return_with_id)
        if host == infos_docker["maquina_arm"]["url"]:
            name_subprocess="arm"
        elif host == infos_docker["maquina_amd"]["url"]:
            name_subprocess="amd"
        p.execute(elementos=array,function=functions,daemon=False,name_subprocess=name_subprocess)
        del gerenciador
        del p
    else:
        return 0

def stop_container(ip:str="",port:int=0,id_:str="",compiled:dict={},id_key=""):
    try:
        if compiled != {}:
            client = docker.DockerClient(base_url=compiled["url"]+":"+str(compiled["port_docker_sock"]),version="auto")
            client.containers.get(compiled[id_key]).stop()
        else:
            if ip == "" or port == 0 or id_key == "":
                return None
            client = docker.DockerClient(base_url=ip+":"+str(port),version="auto")
            client.containers.get(id_).stop()
    except:
            stop_container(ip=ip,port=port,id_=id_,compiled=compiled,id_key=id_key)

def start_container(ip:str="",port:int=0,id_:str="",compiled:dict={},id_key=""):
    try:
        if compiled != {}:
            client = docker.DockerClient(base_url=compiled["url"]+":"+str(compiled["port_docker_sock"]),version="auto")
            client.containers.get(compiled[id_key]).start()
        else:
            if ip == "" or port == 0 or id_key == "":
                return None
            client = docker.DockerClient(base_url=ip+":"+str(port),version="auto")
            client.containers.get(id_).start()
    except:
            start_container(ip=ip,port=port,id_=id_,compiled=compiled,id_key=id_key)

def start_test(tipo_bd:str,paralel=True,recreate:bool=True,total_users=-1):
    start_container(compiled=infos_docker["maquina_arm"],id_key=tipo_bd+"_id")
    start_container(compiled=infos_docker["maquina_amd"],id_key=tipo_bd+"_id")
    result=[]
    try:
        if paralel == True:
            arm=infos_docker["maquina_arm"][tipo_bd+"_connect"]
            arm["total_elementos"]=total_elementos
            arm["total_threads"]=threads_paralel_lv2
            arm["pre_execucao"]=pre_exec
            arm["compiled_users"]=usuarios_bd
            arm["recreate"]=recreate
            arm["total_users"]=total_users
            amd=infos_docker["maquina_amd"][tipo_bd+"_connect"]
            amd["total_elementos"]=total_elementos
            amd["total_threads"]=threads_paralel_lv2
            amd["pre_execucao"]=pre_exec
            amd["compiled_users"]=usuarios_bd
            amd["recreate"]=recreate
            amd["total_users"]=total_users
            dados=[amd,arm]
            p=Paralel_subprocess(total_threads=2)
            result= p.execute(elementos=dados,function=executar_teste,timer=True,name_subprocess="servidor")
            del p
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
print(start_test("mariadb",paralel=True,recreate=False,total_users=quantidade_usuarios))

#executar testes no bd postgres
print(start_test("postgres",paralel=True,recreate=False,total_users=quantidade_usuarios))