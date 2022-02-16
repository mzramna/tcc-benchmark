from multiprocessing import Queue,Process,Pool,Manager
import multiprocessing
from multiprocessing.managers import ValueProxy
from queue import Queue,Empty
from threading import Thread
from timer import Timer
import time
import os
import traceback
import signal

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
    def __init__(self,special_timeout=0,   *args, **kwargs):
        # self.removedor=True
        # if "remove_element" in kwargs:
        #     if kwargs["remove_element"] == False:
        #         self.removedor=False
        self.special_timeout=special_timeout
        self.operacao=0
        self.index=0
        self._close=False
        super().__init__(*args, **kwargs)

    def is_colse(self):
        return self._close

    def handler(self,signum, frame):
        raise Exception("timeout")

    def function_treat(self,work:dict):
        """faz com que a iteração seja feita de forma correta entre os multiplos elementos do array de funções caso seja um array ou executa como uma função normal

        Args:
            work (dict): kwargs das funções passadas 

        Returns:
            [type]: retorno da função passada nos parametros da classe
        """        
        try:
            if self.special_timeout>0:
                signal.signal(signal.SIGALRM, self.handler)
                signal.alarm(self.special_timeout)
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
            if e.args[0]=="timeout":
                self.elementos.insert(0,work)
            raise
        
    def run(self):
        """executa o processo paralelo
        """        
        rodar=True
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
        self.name_subprocess=name
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
            if type(retorno)==list:
                self.retorno_modo=[]
                self.retorno=self.retorno.list()
                for i in retorno:
                    self.retorno.append(i)
            elif type(retorno)==dict:
                self.retorno_modo={}
                self.retorno=self.retorno.dict()
                for key in retorno.keys():
                    self.retorno[key]=[]
        else:
            self.retorno_ = False
        self.time_=timer
        if timer ==True:
            self.timer=[]
        
        
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
        _elementos=self.manager.list(elementos)
        retorno_timer=[]
        for i in range(len(self.threads)):
            self.threads[i]=Worker_subprocess(name=self.name_subprocess+"_"+str(i),special_timeout=self.special_timeout)
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
            if self.time_ == True:
                self.timer.append(Timer())
                self.timer[-1].inicio()
                retorno_timer.append(0)
        if self.join == False:
            contador=0
            while(contador < len(self.threads) or len(_elementos)>0 ) and len(self.threads)>1:
                contador=0
                for i in range(len(self.threads)):
                    if self.threads[i].is_alive() == False or self.threads[i].is_colse() == True or len(_elementos)<=1:#or len(i.elementos)<1 
                        total_elementos=len(_elementos)
                        # cosed=i.is_colse()
                        condicao=contador/len(self.threads)
                        contador+=1
                        if self.time_ == True and retorno_timer[i]==0:
                            retorno_timer[i]=self.timer[i].fim()
                    if contador/len(self.threads) >=self.timeout_percent:
                        contador = len(self.threads)
                        for i in range(len(self.threads)):
                            try:
                                self.threads[i].terminate()
                                self.threads.remove(self.threads[i])
                                if self.time_ == True and retorno_timer[i]==0:
                                    retorno_timer[i]=self.timer[i].fim()
                            except:
                                pass
                        break
        else:
            for i in self.threads:
                i.join()
            if self.time_ == True:
                for i in self.timer:
                    retorno_timer.append(i.fim())

        for i in self.threads:
            try:
                os.killpg(os.getpgid(i.pid), signal.SIGTERM)
            except Exception as e:
                pass
            self.threads.remove(i)

        if self.retorno != None and self.time_ == False:
            return (self.retorno,None)
        elif self.retorno == None and self.time_ == True:
            return (None,retorno_timer)
        elif self.retorno != None and self.time_ == True:
            return (self.retorno,retorno_timer)
        else:
            return(None,None)
        # if join is True:
        #     return self.q.join()

class Worker_thread(Thread):
    def __init__(self, q,name="thread",  *args, **kwargs):
        self.q = q
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
        while rodar == True:
            try:
                if self.q.empty():
                    rodar = False
                    self._close=True
                    break
                work = self.q.get()
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
        return 0
        self.q.task_done()
        self._is_running = False

    def exec_function(self,function,retorno=None,index=-1,retorno_modo=None):
        self.retorno=retorno
        if type(function) == list and type(index) != ValueProxy:
            return None
        else:
            self.index=index
        self.function=function
        self.retorno_modo=retorno_modo

    def kill(self):
        raise SystemExit()

class Paralel_thread:
    def __init__(self,total_threads:int,max_size:int=0,retorno=None,timer=False,daemon=False,join:bool=True,special_timeout:float=0,timeout_percent:float=1,name="thread"):
        self.q=Queue(maxsize=max_size)
        self.threads=[]
        self.retorno=retorno
        self.daemon=daemon
        self.special_timeout=special_timeout
        if timeout_percent>1 or timeout_percent<0:
            raise
        self.timeout_percent=timeout_percent
        self.join=join
        self.name=name
        if total_threads==0:
            total_threads=multiprocessing.cpu_count()*2
        for _ in range(total_threads):
            self.threads.append([])
            if retorno != None:
                self.resultados.append(0)
        if retorno != None:
            self.retorno_ = True
            if type(retorno)==list:
                self.retorno_modo=[]
                self.retorno=self.retorno.list()
                for i in retorno:
                    self.retorno.append(i)
            elif type(retorno)==dict:
                self.retorno_modo={}
                self.retorno=self.retorno.dict()
                for key in retorno.keys():
                    self.retorno[key]=[]
        else:
            self.retorno_ = False
        if timer == True:
            self.timer=[]
            self.time_=True
        else:
            self.time_=False

    def execute(self,elementos,function):
        for j in elementos:
            self.q.put(j)
        retorno_timer=[]
        for i in range(len(self.threads)):
            self.threads[i]=Worker_thread(q=self.q,name=self.name+"_"+str(i))
            if self.retorno_ == True:
                if type(function)==list:
                    self.index=Manager().Value(typecode=int,value=0)
                    self.threads[i].exec_function(function=function,index_retorno=i,retorno=self.retorno,retorno_modo=self.retorno_modo,index=self.index)
                else:
                    self.threads[i].exec_function(function=function,index_retorno=i,retorno=self.retorno,retorno_modo=self.retorno_modo)
            else:
                if type(function)==list:
                    self.index=Manager().Value(typecode=int,value=0)
                    self.threads[i].exec_function(function=function,index=self.index)
                else:
                    self.threads[i].exec_function(function=function)
            self.threads[i].daemon=self.daemon 
            self.threads[i].start()
            if self.time_ == True:
                self.timer.append(Timer())
                self.timer[-1].inicio()
                retorno_timer.append(0)
        if self.join == False:
            contador=0
            while (contador < len(self.threads) or self.q.empty() ) and len(self.threads)>1:
                contador=0
                for thread in range(len(self.threads)):
                    if self.threads[thread].is_alive() == False or self.q.empty():#or len(i.elementos)<1 
                        total_elementos=self.q.qsize()
                        # cosed=i.is_colse()
                        # condicao=contador/len(self.threads)
                        contador+=1
                        if self.time_ == True and retorno_timer[thread]==0:
                            retorno_timer[thread]=self.timer[thread].fim()
                    if contador/len(self.threads) >=self.timeout_percent:
                        contador = len(self.threads)
                        for thread in range(len(self.threads)):
                            try:
                                self.threads[thread].terminate()
                                self.threads.remove(self.threads[thread])
                                if self.time_ == True and retorno_timer[thread]==0:
                                    retorno_timer[thread]=self.timer[thread].fim()
                            except:
                                pass
                        break
        else:
            for thread in self.threads:
                thread.join()
            if self.time_ == True:
                for thread in len(self.timer):
                    retorno_timer[thread]=self.timer[thread].fim()

        # for i in self.threads:
        #     i.terminate()
        if self.retorno_ == True and self.time_== False:
            return (self.retorno,None)
        elif self.retorno_ == False and self.time_ == True:
            return (None,retorno_timer)
        elif self.retorno_ == True and self.time_ == True:
            return (self.retorno,retorno_timer)
        else:
            return(None,None)
