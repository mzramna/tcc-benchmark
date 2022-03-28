from multiprocessing import Queue,Process,Pool,Manager
import multiprocessing
from multiprocessing.managers import ValueProxy,ListProxy,DictProxy
from queue import Queue,Empty
from threading import Thread
from timer import Timer
import gc
from func_timeout import func_timeout, FunctionTimedOut
import time
import os
import traceback

class Paralel_pool:
    def __init__(self,total_threads:int,max_size:int=0):
        #self.q=Queue(maxsize=max_size)
        self.threads=[]
        self.resultados=[]
        self.total_threads=total_threads
        for _ in range(total_threads):
            self.threads.append([])
            self.resultados.append(0)
        
    def execute(self,elementos,function,join:bool=False,dict_order=[]):
        _elementos=[]
        for j in elementos:
            if isinstance(j,dict):
                tmp=[]
                for i in dict_order:
                    tmp.append(j[i])
                _elementos.append(tmp)
            else:
                _elementos.append(j)
        #         self.q.put(j)
        
        p=Pool(processes=self.total_threads)
        
        retorno=p.starmap(function,_elementos)
        p.close()
        p.join()
        if join is True:
            return retorno

class Worker_subprocess(Process):
    def __init__(self,name="subprocess",special_timeout=0, timer=False,index_timer:int=-1, *args, **kwargs):
        if type(timer)==ListProxy:
            self.timer=timer
            self.time_=True
            if index_timer>-1:
                self.index_timer=index_timer
        else:
            self.time_=False
        self.special_timeout=special_timeout
        self.operacao=0
        self.index=0
        super().__init__(*args, **kwargs)
        self.name=name

    def function_treat(self,work:dict):
        """faz com que a iteração seja feita de forma correta entre os multiplos elementos do array de funções caso seja um array ou executa como uma função normal

        Args:
            work (dict): kwargs das funções passadas 

        Returns:
            [type]: retorno da função passada nos parametros da classe
        """        
        try:
            retorno=None
            if type(self.function) == type([]):
                if self.index.value<len(self.function):
                    self.index.value=self.index.value+1
                    if self.special_timeout == 0:
                        retorno= self.function[self.index.value-1](**work)
                    else:
                        retorno=func_timeout(timeout=self.special_timeout,func=self.function[self.index.value-1],kwargs=work)
                else:
                    self.index.value=0
                    if self.special_timeout == 0:
                        retorno= self.function[self.index.value](**work)
                    else:
                        retorno=func_timeout(timeout=self.special_timeout,func=self.function[self.index.value],kwargs=work)
            else:
                if self.special_timeout == 0:
                    retorno= self.function(**work)
                else:
                    retorno=func_timeout(timeout=self.special_timeout,func=self.function,kwargs=work)
            gc.collect()
            return retorno
        except FunctionTimedOut as e:
            self.elementos.insert(0,work)
            pass
        except Exception as e:
            raise
        
    def run(self):
        """executa o processo paralelo
        """        
        rodar=True
        if self.time_ == True:
            timer=Timer()
            timer.inicio()
        while rodar == True:
            try:
                tamanho=len(self.elementos)
                if tamanho<1:
                    rodar = False
                    self._close=True
                    break
                work=self.elementos[0]
                self.elementos.remove(work)
                result=self.function_treat(work)
                if self.retorno_modo!=None:
                    if type(self.retorno_modo)==list:
                        self.retorno.append(result)
                    if type(self.retorno_modo)==dict:
                        for key in self.retorno.keys():
                            self.retorno[key]=result[key]
            except ValueError as e:
                if e.args[0]=='list.remove(x): x not in list':
                    pass
                else:
                    raise
            except IndexError as e:
                rodar = False
                break
            except Exception as e:
                # traceback.print_exc()
                if e.args[0]=="timeout":
                    pass
                else:
                    rodar = False
                    break
        if self.time_ == True:
            if self.index_timer:
                self.timer[self.index_timer]=timer.fim()
            else:
                self.timer.append(timer.fim())
        return 0

    def exec_function(self,elementos,function,index=-1,retorno=None,retorno_modo=None):
        """executa processo paralelo

        Args:
            elementos ([dict]): array de dictionarys de kwargs para as execuções das funções 
            function ([function]): array de funções,pode ter apenas uma função,só é necessária mais de uma se forem usados varios objetos diferentes para fazer as execuções
            retorno ([manager.list,manager.dict], optional): implementado mas não testado:
            - se passado um array,independente do conteudo,irá retornar um valor para cada input em cada elemento do array,fora de ordem
            - se passado um dict,com as keys definidas e conteudo delas indiferente,essas keys devem ser as mesmas do retorno da função inserida,pois o retorno será dado dessa forma,como array contendo o valor de retorno em cada key,pode estar totalmente fora de ordem,para evitar isso use o modo de array
            - se valor default não será retornado nenhum valor ao final da execução,não compativel com modo daemon no momento. Defaults to None.
            retorno_modo ([type], optional): modo de output que será usado no retorno dos processos. Defaults to None.
        """
        if type(function) == list and type(index) != ValueProxy:
            return None
        else:
            self.index=index
        if retorno != None:
            self.retorno_ = True
            self.retorno=retorno
        else:
            self.retorno_ = False
        if type(function) == list:
            self.function=function
            self.index=index
        else:
            self.function=function
        self.retorno_modo=retorno_modo
        self.elementos=elementos

    def kill(self):
        raise SystemExit()

class Paralel_subprocess:
    """classe de gerenciamento de processos paralelos
    """    
    def __init__(self,total_threads:int=0,retorno=None,timer=False,daemon=False,name:str="subprocess",special_timeout:float=0,timeout_percent:float=1,join:bool=False):
        """classe de gerenciamento de processos paralelos

        Args:
            total_threads (int, optional): quantidade de subprocessos que irão ser criados para fazer o processamento paralelo,se 0 será usado o valor padrão de numero de nucleos * 2. Defaults to 0.
        """        
        #self.q=Queue(maxsize=max_size)
        self.manager=Manager()
        self.retorno=None
        self.threads=[]
        self.resultados=[]
        self.daemon=daemon
        self.special_timeout=special_timeout
        self.name=name
        self.join=join
        if timeout_percent>1 or timeout_percent<0:
            raise
        self.timeout_percent=timeout_percent
        if total_threads==0:
            total_threads=multiprocessing.cpu_count()*2
        for _ in range(total_threads):
            self.threads.append([])
            self.resultados.append(0)
        if retorno != None:
            self.retorno=Manager()
            self.retorno_ = True
            if type(retorno) == ListProxy:
                self.retorno_modo=[]
                self.retorno=self.retorno.list()
                for i in retorno:
                    self.retorno.append(i)
            elif type(retorno) == DictProxy:
                self.retorno_modo={}
                self.retorno=self.retorno.dict()
                for key in retorno.keys():
                    self.retorno[key]=[]
            else:
                raise
        else:
            self.retorno_ = False
        if timer == True:
            self.timer=Manager().list()
            self.time_=True
        else:
            self.time_=False
        
        
    def execute(self,elementos,function):
        """executa o processamento das funções passadas com os parametros passados

        Args:
            elementos ([dict]): array de dictionarys de kwargs para as execuções das funções 
            function ([function]): array de funções,pode ter apenas uma função,só é necessária mais de uma se forem usados varios objetos diferentes para fazer as execuções
            retorno (type, optional): implementado mas não testado:
            - se passado um array,independente do conteudo,irá retornar um valor para cada input em cada elemento do array,fora de ordem
            - se passado um dict,com as keys definidas e conteudo delas indiferente,essas keys devem ser as mesmas do retorno da função inserida,pois o retorno será dado dessa forma,como array contendo o valor de retorno em cada key,pode estar totalmente fora de ordem,para evitar isso use o modo de array
            - se valor default não será retornado nenhum valor ao final da execução,não compativel com modo daemon no momento. Defaults to None.
            daemon (bool, optional): se verdadeiro o processo funcionará em modo daemon,isso fará com que as funções não sejam destruidas ao final da operação,só deve ser usado se forem adicionados novos elementos ao manager em segundo plano em outro subprocesso,não compativel com retorno no momento. Defaults to False.
            timer (bool, optional): retorna o tempo gasto para executar a função. Defaults to False.
            name_subprocess (str, optional): nome para os subprocessos,facilita o debug. Defaults to "subprocess".
        Returns:
            (list,list): primeiro list sendo o retorno,segundo sendo o tempo gasto para a execução,pode ser ignorado o segundo parametro,mas sempre será retornado
        """
        try:
            _elementos=self.manager.list(elementos)
            retorno_timer=[]
            for i in range(len(self.threads)):
                if self.time_==True:
                    self.threads[i]=Worker_subprocess(name=self.name+"_"+str(i),timer=self.timer,index_timer=i,special_timeout=self.special_timeout)
                    self.timer.append(0)
                else:
                    self.threads[i]=Worker_subprocess(name=self.name+"_"+str(i),special_timeout=self.special_timeout)
                if self.retorno_ == True:
                    if type(function)==list:
                        self.index=self.manager.Value(typecode=int,value=0)
                        self.threads[i].exec_function(elementos=_elementos,function=function,index_retorno=i,retorno=self.retorno,retorno_modo=self.retorno_modo,index=self.index)
                    else:
                        self.threads[i].exec_function(elementos=_elementos,function=function,index_retorno=i,retorno=self.retorno,retorno_modo=self.retorno_modo)
                else:
                    if type(function)==list:
                        self.index=self.manager.Value(typecode=int,value=0)
                        self.threads[i].exec_function(elementos=_elementos,function=function,index=self.index)
                    else:
                        self.threads[i].exec_function(elementos=_elementos,function=function)
                self.threads[i].daemon=self.daemon 
                self.threads[i].start()
            if self.join == False:
                contador=0
                while(contador < len(self.threads) or len(_elementos)>0 ) and len(self.threads)>1:
                    contador=0
                    for i in range(len(self.threads)):
                        if self.threads[i].is_alive() == False or len(_elementos) <= 1:
                            total_elementos=len(_elementos)
                            contador+=1
                        condicao=contador/len(self.threads)
                        if condicao >=self.timeout_percent:
                            contador = len(self.threads)
                            for j in range(len(self.threads)):
                                try:
                                    self.threads[j].kill()
                                    # os.killpg(os.getpgid(self.threads[j].pid), signal.SIGTERM)
                                    #self.threads.remove(self.threads[j])
                                except SystemExit as e:#obrigatoria a parada
                                    pass
                                except IndexError as e:
                                    pass
                                except OSError as e:
                                    if e.errno == 3 and e.args[1] == 'No such process':
                                        pass
                                    else:
                                        raise
                                except Exception as e:
                                    pass
                            break
            else:
                for i in range(len(self.threads)):
                    # if self.time_ == True:
                    #     #retorno_timer[i]=
                    #     self.threads[i].join()
                    # else:
                    self.threads[i].join()

            for i in range(len(self.threads)):
                try:
                    self.threads[i].kill()
                    #os.killpg(os.getpgid(i.pid), signal.SIGTERM)
                    self.threads.remove(self.threads[i])
                except ValueError as e:
                    pass
                except IndexError as e:
                    pass
                except AttributeError as e:
                    pass
                except SystemExit as e:
                    pass
                except OSError as e:
                    if e.errno == 3 and e.args[1] == 'No such process':
                        pass
                    else:
                        raise
                except Exception as e:
                    raise
            if self.time_ == True:
                retorno_timer=list(self.timer)
        except Exception as e:
            raise
        del self.threads
        gc.collect()
        if self.retorno != None and self.time_ == False:
            return (self.retorno,None)
        elif self.retorno == None and self.time_ == True:
            return (None,retorno_timer)
        elif self.retorno != None and self.time_ == True:
            return (self.retorno,retorno_timer)
        else:
            return(None,None)

class Worker_thread(Thread):
    def __init__(self,name="thread",special_timeout=0, timer=False,index_timer:int=-1, *args, **kwargs):
        if type(timer) == ListProxy:
            self.timer=timer
            self.time_=True
            if index_timer > -1:
                self.index_timer=index_timer
        else:
            self.time_=False
        self.special_timeout=special_timeout
        self.operacao=0
        self.index=0
        super().__init__(*args, **kwargs)
        self.name=name

    def function_treat(self,work:dict):
        """faz com que a iteração seja feita de forma correta entre os multiplos elementos do array de funções caso seja um array ou executa como uma função normal

        Args:
            work (dict): kwargs das funções passadas 

        Returns:
            [type]: retorno da função passada nos parametros da classe
        """        
        try:
            retorno=None
            if type(self.function)==type([]):
                if self.index.value<len(self.function):
                    self.index.value=self.index.value+1
                    retorno= self.function[self.index.value-1](**work)
                    # subsubprocess=Process(target=self.function[self.index.value-1],kwargs=work)
                    # subsubprocess.start()
                    # retorno=subsubprocess.join(timeout=self.special_timeout)
                else:
                    self.index.value=0
                    retorno= self.function[self.index.value](**work)
                    # subsubprocess=Process(target=self.function[self.index.value],kwargs=work)
                    # subsubprocess.start()
                    # retorno=subsubprocess.join(timeout=self.special_timeout)
            else:
                retorno= self.function(**work)
                # subsubprocess=Process(target=self.function,kwargs=work)
                # subsubprocess.start()
                # retorno=subsubprocess.join(timeout=self.special_timeout)
            return retorno
        except Exception as e:
            # traceback.print_exc()
            # time.sleep(200)
            raise

    def run(self):
        """executa o processo paralelo
        """        
        rodar=True
        if self.time_ == True:
            timer=Timer()
            timer.inicio()
        while rodar == True:
            try:
                tamanho=len(self.elementos)
                if tamanho<1:
                    rodar = False
                    self._close=True
                    break
                work=self.elementos[0]
                self.elementos.remove(work)
                result=self.function_treat(work)
                if self.retorno_modo!=None:
                    if type(self.retorno_modo)==list:
                        self.retorno.append(result)
                    if type(self.retorno_modo)==dict:
                        for key in self.retorno.keys():
                            self.retorno[key]=result[key]
            except ValueError as e:
                if e.args[0]=='list.remove(x): x not in list':
                    pass
                else:
                    raise
            except IndexError as e:
                rodar = False
                break
            except Exception as e:
                # traceback.print_exc()
                if e.args[0]=="timeout":
                    pass
                else:
                    rodar = False
                    break
        if self.time_ == True:
            if self.index_timer:
                self.timer[self.index_timer]=timer.fim()
            else:
                self.timer.append(timer.fim())
        return 0

    def exec_function(self,elementos,function,index=-1,retorno=None,retorno_modo=None):
        """executa processo paralelo

        Args:
            elementos ([dict]): array de dictionarys de kwargs para as execuções das funções 
            function ([function]): array de funções,pode ter apenas uma função,só é necessária mais de uma se forem usados varios objetos diferentes para fazer as execuções
            retorno ([manager.list,manager.dict], optional): implementado mas não testado:
            - se passado um array,independente do conteudo,irá retornar um valor para cada input em cada elemento do array,fora de ordem
            - se passado um dict,com as keys definidas e conteudo delas indiferente,essas keys devem ser as mesmas do retorno da função inserida,pois o retorno será dado dessa forma,como array contendo o valor de retorno em cada key,pode estar totalmente fora de ordem,para evitar isso use o modo de array
            - se valor default não será retornado nenhum valor ao final da execução,não compativel com modo daemon no momento. Defaults to None.
            retorno_modo ([type], optional): modo de output que será usado no retorno dos processos. Defaults to None.
        """
        if type(function) == list and type(index) != ValueProxy:
            return None
        else:
            self.index=index
        if retorno != None:
            self.retorno_ = True
            self.retorno=retorno
        else:
            self.retorno_ = False
        if type(function) == list:
            self.function=function
            self.index=index
        else:
            self.function=function
        self.retorno_modo=retorno_modo
        self.elementos=elementos

    def kill(self):
        raise SystemExit()

class Paralel_thread:
    def __init__(self,total_threads:int=0,retorno=None,timer=False,daemon=False,name:str="thread",special_timeout:float=0,timeout_percent:float=1,join:bool=False):
        """classe de gerenciamento de processos paralelos

        Args:
            total_threads (int, optional): quantidade de subprocessos que irão ser criados para fazer o processamento paralelo,se 0 será usado o valor padrão de numero de nucleos * 2. Defaults to 0.
        """        
        #self.q=Queue(maxsize=max_size)
        self.manager=Manager()
        self.retorno=None
        self.threads=[]
        self.resultados=[]
        self.daemon=daemon
        self.special_timeout=special_timeout
        self.name=name
        self.join=join
        if timeout_percent>1 or timeout_percent<0:
            raise
        self.timeout_percent=timeout_percent
        if total_threads==0:
            total_threads=multiprocessing.cpu_count()*2
        for _ in range(total_threads):
            self.threads.append([])
            self.resultados.append(0)
        if retorno != None:
            self.retorno=Manager()
            self.retorno_ = True
            if type(retorno) == ListProxy:
                self.retorno_modo=[]
                self.retorno=self.retorno.list()
                for i in retorno:
                    self.retorno.append(i)
            elif type(retorno) == DictProxy:
                self.retorno_modo={}
                self.retorno=self.retorno.dict()
                for key in retorno.keys():
                    self.retorno[key]=[]
            else:
                raise
        else:
            self.retorno_ = False
        if timer == True:
            self.timer=Manager().list()
            self.time_=True
        else:
            self.time_=False

    def execute(self,elementos,function):
        try:
            _elementos=self.manager.list(elementos)
            retorno_timer=[]
            for i in range(len(self.threads)):
                if self.time_==True:
                    self.threads[i]=Worker_thread(name=self.name+"_"+str(i),timer=self.timer,index_timer=i,special_timeout=self.special_timeout)
                    self.timer.append(0)
                else:
                    self.threads[i]=Worker_thread(name=self.name+"_"+str(i),special_timeout=self.special_timeout)
                if self.retorno_ == True:
                    if type(function)==list:
                        self.index=self.manager.Value(typecode=int,value=0)
                        self.threads[i].exec_function(elementos=_elementos,function=function,index_retorno=i,retorno=self.retorno,retorno_modo=self.retorno_modo,index=self.index)
                    else:
                        self.threads[i].exec_function(elementos=_elementos,function=function,index_retorno=i,retorno=self.retorno,retorno_modo=self.retorno_modo)
                else:
                    if type(function)==list:
                        self.index=self.manager.Value(typecode=int,value=0)
                        self.threads[i].exec_function(elementos=_elementos,function=function,index=self.index)
                    else:
                        self.threads[i].exec_function(elementos=_elementos,function=function)
                self.threads[i].daemon=self.daemon 
                self.threads[i].start()
            if self.join == False:
                contador=0
                while(contador < len(self.threads) or len(_elementos)>0 ) and len(self.threads)>1:
                    contador=0
                    for i in range(len(self.threads)):
                        if self.threads[i].is_alive() == False or len(_elementos) <= 1:
                            total_elementos=len(_elementos)
                            contador+=1
                        condicao=contador/len(self.threads)
                        if condicao >=self.timeout_percent:
                            contador = len(self.threads)
                            for j in range(len(self.threads)):
                                try:
                                    self.threads[j].kill()
                                    #os.killpg(os.getpgid(self.threads[j].pid), signal.SIGTERM)
                                    #self.threads.remove(self.threads[j])
                                except SystemExit as e:
                                    pass
                                except IndexError as e:
                                    pass
                                except OSError as e:
                                    if e.errno == 3 and e.args[1] == 'No such process':
                                        pass
                                    else:
                                        raise
                                except Exception as e:
                                    pass
                            break
            else:
                for i in range(len(self.threads)):
                    if self.time_ == True:
                        #retorno_timer[i]=
                        self.threads[i].join()
                    else:
                        self.threads[i].join()
            for i in range(len(self.threads)):
                try:
                    self.threads[i].kill()
                    #os.killpg(os.getpgid(i.pid), signal.SIGTERM)
                    self.threads.remove(self.threads[i])
                except ValueError as e:
                    pass
                except IndexError as e:
                    pass
                except AttributeError as e:
                    pass
                except SystemExit as e:
                    pass
                except OSError as e:
                    if e.errno == 3 and e.args[1] == 'No such process':
                        pass
                    else:
                        raise
                except Exception as e:
                    raise
            if self.time_ == True:
                retorno_timer=list(self.timer)
        except Exception as e:
            raise
        del self.threads
        gc.collect()
        if self.retorno_ == True and self.time_== False:
            return (self.retorno,None)
        elif self.retorno_ == False and self.time_ == True:
            return (None,retorno_timer)
        elif self.retorno_ == True and self.time_ == True:
            return (self.retorno,retorno_timer)
        else:
            return(None,None)
