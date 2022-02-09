import time, docker,json,string
from random import choice
from os import DirEntry
from gerenciadorDeBD import GerenciadorDeBD
from paralelLib import Paralel_pool,Paralel_subprocess,Paralel_thread
import traceback
#from datetime import datetime

logstash_data={"host":"192.168.0.116","port":5000}
paralel=True
total_elementos=100000
pre_exec=100
threads_paralel_lv2=10
threads_pct_timeout_lv2=0.6
quantidade_usuarios=-1
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

def preparacao_pre_teste(host,database,port,tipo,sql_file_pattern,total_users=10,user:str="",password:str="",compiled_users:dict={},recreate:bool=False):
    try:
        if tipo == 0:
            tipo_bd="mariadb"
        elif tipo ==1:
            tipo_bd="postgres"
        if host == infos_docker["maquina_arm"]["url"]:
                start_container(compiled=infos_docker["maquina_arm"],id_key=tipo_bd+"_id")
        elif host == infos_docker["maquina_amd"]["url"]:
            start_container(compiled=infos_docker["maquina_amd"],id_key=tipo_bd+"_id")
        time.sleep(10)
        if recreate == True:
                try:
                    reset=GerenciadorDeBD(host=host, user=user, password=password, database=database, port=port,tipo=tipo,sql_file_pattern=sql_file_pattern,logstash_data=logstash_data,level=40)
                    time.sleep(10)
                    reset.reset_database()
                    del reset
                except BaseException as e:
                    raise
        if compiled_users !={}:
            gerador_usuarios("scripts/usuarios.json",total_users)
            cadastrar_usuarios(connect={"host":host, "user":user, "password":password, "database":database, "port":port,"tipo":tipo,"sql_file_pattern":sql_file_pattern,"logstash_data":logstash_data,"level":40}, usuarios=compiled_users, bd=database, root="SafestRootPassword")
    except:
        traceback.print_exc()
        raise

def executar_teste(host,database,port,tipo,sql_file_pattern,pre_execucao=1000,total_elementos=10000,total_threads=3,user:str="",password:str="",compiled_users:dict={},recreate:bool=False,total_users:int=-1):
    array=[]
    threads=[]
    try:
        preparacao_pre_teste(host=host,database=database,port=port,tipo=tipo,sql_file_pattern=sql_file_pattern,total_users=total_users, user=user,password=password,compiled_users=compiled_users,recreate=recreate)
        for _ in range(pre_execucao,total_threads):
            threads.append([])
        for i in range(pre_execucao,total_elementos):
            array.append({"id":i,"sqlite_file":"scripts/initial_db.db"})
        if compiled_users !={}:
            gerenciador=[]
            for i in compiled_users.keys():
                gerenciador.append(GerenciadorDeBD(host=host, user=compiled_users[i]["usuario"], password=compiled_users[i]["senha"], database=database, port=port,tipo=tipo,sql_file_pattern=sql_file_pattern,logstash_data=logstash_data,level=40,autocommit=True))
                if total_users>-1 and len(gerenciador) == total_users:
                    break
            if pre_execucao>0:
                gerenciador[0].execute_operation_from_sqlite_no_return(pre_execucao, "scripts/initial_db.db") 
            name_subprocess=""
            if host == infos_docker["maquina_arm"]["url"]:
                name_subprocess="arm"
            elif host == infos_docker["maquina_amd"]["url"]:
                name_subprocess="amd"
            p=Paralel_subprocess(total_threads=total_threads,timeout_percent=threads_pct_timeout_lv2,daemon=False,name_subprocess=name_subprocess)
            functions=[]
            for i in gerenciador:
                functions.append(i.execute_operation_from_sqlite_no_return_with_id)
            p.execute(elementos=array,function=functions)
            del gerenciador
            del p
        else:
            return 0
    except:
        raise
    finally:
        if tipo == 0:
            tipo_bd="mariadb"
        elif tipo ==1:
            tipo_bd="postgres"
        if host == infos_docker["maquina_arm"]["url"]:
            stop_container(compiled=infos_docker["maquina_arm"],id_key=tipo_bd+"_id")
        elif host == infos_docker["maquina_amd"]["url"]:
            stop_container(compiled=infos_docker["maquina_amd"],id_key=tipo_bd+"_id")


def start_test(tipo_bd:str,paralel=True,recreate:bool=True,total_users=-1):
    result=[]
    arm=infos_docker["maquina_arm"][tipo_bd+"_connect"]
    arm["compiled_users"]=usuarios_bd
    arm["recreate"]=recreate
    arm["total_users"]=total_users
    amd=infos_docker["maquina_amd"][tipo_bd+"_connect"]
    amd["compiled_users"]=usuarios_bd
    amd["recreate"]=recreate
    amd["total_users"]=total_users
    dados=[arm,amd]
    if paralel == False:
        try:
            for i in dados:
                preparacao_pre_teste(**i)
        except:
            pass
    arm["total_elementos"]=total_elementos
    arm["pre_execucao"]=pre_exec
    arm["total_threads"]=threads_paralel_lv2
    amd["total_elementos"]=total_elementos
    amd["total_threads"]=threads_paralel_lv2
    amd["pre_execucao"]=pre_exec
    dados=[arm,amd]
    try:
        if paralel == True:
            p=Paralel_thread(total_threads=2,timer=True)
            result= p.execute(elementos=dados,function=executar_teste)
            del p
        else:
            for i in dados:
                executar_teste(**i)
    except BaseException as e:
        pass
    finally:
        return result

#executar testes no bd mariadb
print(start_test("mariadb",paralel=paralel,recreate=True,total_users=quantidade_usuarios))

#executar testes no bd postgres
print(start_test("postgres",paralel=paralel,recreate=True,total_users=quantidade_usuarios))