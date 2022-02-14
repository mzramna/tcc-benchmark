import time, docker,json,string
from random import choice
from os import DirEntry
from gerenciadorDeBD import GerenciadorDeBD
from paralelLib import Paralel_pool,Paralel_subprocess,Paralel_thread
import traceback
#from datetime import datetime

class Executar_benchmark:
    def __init__(self,paralel=True,recreate=True,threads_paralel_lv2=10,threads_pct_timeout_lv2=0.5,threads_timeout_lv2=5,quantidade_usuarios=-1,sqlite_bd:DirEntry="scripts/initial_db.db",usuarios_bd:DirEntry="scripts/usuarios.json",infos_docker:DirEntry="scripts/infos_docker.json",logstash_data={}):
        self.logstash_data=logstash_data
        self.paralel=paralel
        self.recreate=recreate
        self.threads_paralel_lv2=threads_paralel_lv2
        self.threads_pct_timeout_lv2=threads_pct_timeout_lv2
        self.threads_timeout_lv2=threads_timeout_lv2
        self.quantidade_usuarios=quantidade_usuarios
        self.sqlite_db=sqlite_bd
        self.usuarios_bd=json.loads(open(usuarios_bd).read())
        self.infos_docker=json.loads(open(infos_docker).read())

    def gerador_usuarios(self,arquivo:DirEntry,quantidade:int,tamanho:int=10):
        valores = string.ascii_lowercase + string.digits
        usuarios_cadastrados=json.loads(open(arquivo).read())
        if quantidade>0:
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

    def cadastrar_usuarios(self,connect:dict,usuarios:dict,bd:str,root:str,quantidade:int=-1):
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

    def stop_container(self,ip:str="",port:int=0,id_:str="",compiled:dict={},id_key=""):
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
                self.stop_container(ip=ip,port=port,id_=id_,compiled=compiled,id_key=id_key)

    def start_container(self,ip:str="",port:int=0,id_:str="",compiled:dict={},id_key=""):
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
                self.start_container(ip=ip,port=port,id_=id_,compiled=compiled,id_key=id_key)

    def preparacao_pre_teste(self,host,database,port,tipo,sql_file_pattern,total_users=10,user:str="",password:str="",compiled_users:dict={},recreate:bool=False):
        try:
            if tipo == 0:
                tipo_bd="mariadb"
            elif tipo ==1:
                tipo_bd="postgres"
            if host == self.infos_docker["maquina_arm"]["url"]:
                    self.start_container(compiled=self.infos_docker["maquina_arm"],id_key=tipo_bd+"_id")
            elif host == self.infos_docker["maquina_amd"]["url"]:
                self.start_container(compiled=self.infos_docker["maquina_amd"],id_key=tipo_bd+"_id")
            time.sleep(10)
            if recreate == True:
                    try:
                        reset=GerenciadorDeBD(host=host, user=user, password=password, database=database, port=port,tipo=tipo,sql_file_pattern=sql_file_pattern,logstash_data=self.logstash_data,level=40)
                        time.sleep(10)
                        reset.reset_database()
                        del reset
                    except BaseException as e:
                        raise
            if compiled_users !={}:
                self.gerador_usuarios(arquivo="scripts/usuarios.json",quantidade=total_users)
                self.cadastrar_usuarios(connect={"host":host, "user":user, "password":password, "database":database, "port":port,"tipo":tipo,"sql_file_pattern":sql_file_pattern,"logstash_data":self.logstash_data,"level":40}, usuarios=compiled_users, bd=database, root="SafestRootPassword")
        except:
            traceback.print_exc()
            raise

    def executar_teste(self,host,database,port,tipo,sql_file_pattern,pre_execucao=1000,total_elementos=10000,total_threads=3,user:str="",password:str="",compiled_users:dict={},recreate:bool=False,total_users:int=-1,pre_exec=True):
        array=[]
        threads=[]
        try:
            self.preparacao_pre_teste(host=host,database=database,port=port,tipo=tipo,sql_file_pattern=sql_file_pattern,total_users=total_users, user=user,password=password,compiled_users=compiled_users,recreate=recreate)
            for _ in range(pre_execucao,total_threads):
                threads.append([])
            for i in range(pre_execucao,total_elementos):
                array.append({"id":i,"sqlite_file":self.sqlite_db})
            if self.threads_paralel_lv2>1 :
                if compiled_users !={}:
                    gerenciador=[]
                    for i in compiled_users.keys():
                        gerenciador.append(GerenciadorDeBD(host=host, user=compiled_users[i]["usuario"], password=compiled_users[i]["senha"], database=database, port=port,tipo=tipo,sql_file_pattern=sql_file_pattern,logstash_data=self.logstash_data,level=40,autocommit=True))
                        if total_users>-1 and len(gerenciador) == total_users:
                            break
                    if pre_execucao>0 and pre_exec == True:
                        gerenciador[0].execute_operation_from_sqlite_no_return(pre_execucao, self.sqlite_db) 
                    name_subprocess=""
                    if host == self.infos_docker["maquina_arm"]["url"]:
                        name_subprocess="arm"
                    elif host == self.infos_docker["maquina_amd"]["url"]:
                        name_subprocess="amd"
                    p=Paralel_subprocess(total_threads=total_threads,timeout_percent=self.threads_pct_timeout_lv2,daemon=False,name_subprocess=name_subprocess,special_timeout=self.threads_timeout_lv2)
                    functions=[]
                    for i in gerenciador:
                        functions.append(i.execute_operation_from_sqlite_no_return_with_id)
                    p.execute(elementos=array,function=functions)
                    del gerenciador
                    del p
                else:
                    return 0
            else:
                gerenciador=GerenciadorDeBD(host=host, user=user, password=password, database=database, port=port,tipo=tipo,sql_file_pattern=sql_file_pattern,logstash_data=self.logstash_data,level=40,autocommit=True)
                gerenciador.execute_operation_from_sqlite_no_return(total_elementos, self.sqlite_db) 
                del gerenciador
        except BaseException as e:
            raise
        finally:
            if tipo == 0:
                tipo_bd="mariadb"
            elif tipo ==1:
                tipo_bd="postgres"
            if host == self.infos_docker["maquina_arm"]["url"]:
                self.stop_container(compiled=self.infos_docker["maquina_arm"],id_key=tipo_bd+"_id")
            elif host == self.infos_docker["maquina_amd"]["url"]:
                self.stop_container(compiled=self.infos_docker["maquina_amd"],id_key=tipo_bd+"_id")

    def start_test(self,tipo_bd:str,pre_execucao=1000,total_elementos=10000,paralel=True,recreate:bool=True,total_users=-1,timer=False,pre_exec=True):
        result=[]
        arm=self.infos_docker["maquina_arm"][tipo_bd+"_connect"]
        arm["compiled_users"]=self.usuarios_bd
        arm["recreate"]=recreate
        arm["total_users"]=total_users
        amd=self.infos_docker["maquina_amd"][tipo_bd+"_connect"]
        amd["compiled_users"]=self.usuarios_bd
        amd["recreate"]=recreate
        amd["total_users"]=total_users
        dados=[arm,amd]
        if paralel == False:
            try:
                for i in dados:
                    self.preparacao_pre_teste(**i)
            except:
                pass
        arm["total_elementos"]=total_elementos
        arm["pre_execucao"]=pre_execucao
        arm["total_threads"]=self.threads_paralel_lv2
        arm["pre_exec"]=pre_exec
        amd["total_elementos"]=total_elementos
        amd["total_threads"]=self.threads_paralel_lv2
        amd["pre_execucao"]=pre_execucao
        amd["pre_exec"]=pre_exec
        dados=[arm,amd]
        try:
            if paralel == True:
                # timeout=200*total_elementos
                p=Paralel_subprocess(total_threads=2,timer=timer,join=True,name_subprocess="servidor")#,special_timeout=timeout
                result=p.execute(elementos=dados,function=self.executar_teste)
                del p
            else:
                for i in dados:
                    self.executar_teste(**i)
        except BaseException as e:
            pass
        finally:
            return result

    def executar(self,pre_execucao=1000,total_elementos=10000,pre_exec=True,tipo:str="",timer_geral=True):
        from timer import Timer
        timer=Timer()
        retorno=[]
        if timer_geral == True:
            #executar testes no bd postgres
            if tipo == "" or tipo == "postgres":
                timer.inicio()
                self.start_test("postgres",pre_execucao=pre_execucao,total_elementos=total_elementos,paralel=self.paralel,recreate=self.recreate,total_users=self.quantidade_usuarios,pre_exec=pre_exec)
                retorno.append(timer.fim())
                print("postgres concluido em "+str(retorno[-1]))
            #executar testes no bd mariadb
            if tipo == "" or tipo == "mariadb":
                timer.inicio()
                self.start_test("mariadb",pre_execucao=pre_execucao,total_elementos=total_elementos,paralel=self.paralel,recreate=self.recreate,total_users=self.quantidade_usuarios,pre_exec=pre_exec)
                retorno.append(timer.fim())
                print("mariadb concluido em "+str(retorno[-1]))
        if timer_geral == False:
            #executar testes no bd postgres
            if tipo == "" or tipo == "postgres":
                retorno.append(self.start_test("postgres",pre_execucao=pre_execucao,total_elementos=total_elementos,paralel=self.paralel,recreate=self.recreate,total_users=self.quantidade_usuarios,pre_exec=pre_exec))
                print("postgres concluido em "+str(retorno[-1]))
            #executar testes no bd mariadb
            if tipo == "" or tipo == "mariadb":
                retorno.append(self.start_test("mariadb",pre_execucao=pre_execucao,total_elementos=total_elementos,paralel=self.paralel,recreate=self.recreate,total_users=self.quantidade_usuarios,pre_exec=pre_exec))
                print("mariadb concluido em "+str(retorno[-1]))
        return retorno
    
    def reset_bd_full(self):
        for tipo_bd in ["mariadb","postgres"]:
            arm=self.infos_docker["maquina_arm"][tipo_bd+"_connect"]
            arm["compiled_users"]=self.usuarios_bd
            arm["recreate"]=True
            arm["total_users"]=-1
            amd=self.infos_docker["maquina_amd"][tipo_bd+"_connect"]
            amd["compiled_users"]=self.usuarios_bd
            amd["recreate"]=True
            amd["total_users"]=-1
            dados=[arm,amd]
            try:
                for i in dados:
                    self.preparacao_pre_teste(**i)
            except:
                pass

if __name__ == "__main__":
    logstash_data={"host":"192.168.0.116","port":5000}
    tempos=Executar_benchmark(logstash_data=logstash_data).executar()
    for i in tempos:
        print(i)
