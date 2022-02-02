from multiprocessing import Queue,Process,Pool,current_process,Manager 
import multiprocessing
from functools import partial
from queue import Queue,Empty
from threading import Thread
from timer import Timer
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
    def __init__(self,   *args, **kwargs):
        # self.removedor=True
        # if "remove_element" in kwargs:
        #     if kwargs["remove_element"] == False:
        #         self.removedor=False
        self.operacao=0
        self.index=0
        self.close_=False
        super().__init__(*args, **kwargs)

    def function_treat(self,work:dict):
        if type(self.function)==type([]):
            if self.index<len(self.function):
                self.index+=1
                return self.function[self.index-1](**work)
            else:
                self.index=0
                return self.function[self.index](**work)
        else:
            return self.function(**work)

    def run(self):
        rodar=True
        while rodar == True:
            try:
                tamanho=len(self.elementos)
                if tamanho<1:
                    self.close_=True
                    rodar = False
                    break
                work=self.elementos[0]
                self.elementos.remove(work)
                if self.retroativo!="":
                    work[self.retroativo]=self.retorno[self.index_retorno]
                result=self.function_treat(work)
                if self.retorno != None:
                    if self.function_array:
                        self.retorno[self.index_retorno].append(result)
                    else:
                        self.retorno[self.index_retorno]+=result
            except ValueError:
                pass
            except IndexError:
                pass
            except Exception as e:
                traceback.print_exc()
                pass
        return 0

    def exec_function(self,elementos,function,retorno=None,index_retorno=None,function_array=False,retroativo=""):
        self.retorno=retorno
        if index_retorno != None:
            self.index_retorno=index_retorno
            if self.retorno !=None:
                self.retorno[self.index_retorno]=0
        self.function=function
        self.function_array=function_array
        self.retroativo=retroativo
        self.elementos=elementos
        if function_array:
            self.retorno[self.index_retorno]=[]

class Paralel_subprocess:
    def __init__(self,total_threads:int=0,max_size:int=0):
        #self.q=Queue(maxsize=max_size)
        self.manager=Manager()
        
        self.threads=[]
        self.resultados=[]
        if total_threads==0:
            total_threads=multiprocessing.cpu_count()*2
        for _ in range(total_threads):
            self.threads.append([])
            self.resultados.append(0)
        
    def execute(self,elementos,function,retorno=None,daemon=False,timer=False,name_subprocess:str="subprocess",**kwargs):
        # for j in elementos:
        #         self.q.put(j)
        _elementos=self.manager.list(elementos)
        if retorno !=None:
            self.retorno == retorno
        if timer ==True:
            self.timer=[]
            self.time_=True
        else:
            self.time_=False
        for i in range(len(self.threads)):
            self.threads[i]=Worker_subprocess(name=name_subprocess+"_"+str(i))
            self.threads[i].exec_function(elementos=_elementos,function=function,index_retorno=i,retorno=retorno)#,kwargs=pass_kwargs)
            if daemon == True:
                self.threads[i].daemon=True
            self.threads[i].start()
            if timer ==True:
                self.timer.append(Timer())
                self.timer[-1].inicio()
            
        for i in self.threads:
            i.join()
        # while len(self.threads)>0:
        #     for i in self.threads:
        #         if i.close_ == True:
        #             i.close()
        #             self.threads.remove(i)
        if retorno !=None and timer==False:
            return (self.retorno,None)
        elif retorno == None and timer ==True:
            retorno_timer=[]
            for i in self.timer:
                retorno_timer.append(i.fim())
            return (None,retorno_timer)
        elif retorno !=None and timer ==True:
            retorno_timer=[]
            for i in self.timer:
                retorno_timer.append(i.fim())
            return (self.retorno,retorno_timer)
        else:
            return(None,None)
        # if join is True:
        #     return self.q.join()

class Worker_thread(Thread):
    def __init__(self, q,  *args, **kwargs):
        self.q = q
        self.operacao=0
        self.index=0
        super().__init__(*args, **kwargs)

    def print_element(self):
        while True:
            try:
                work = self.q.get()  # 3s timeout
                print(work)
            except Empty:
                return
            # do whatever work you have to do on work
            self.q.task_done()

    def sum_element(self):
        while True:
            try:
                work = self.q.get()  # 3s timeout
                self.retorno[self.index_retorno]+=work
            except Empty:
                return 
            # do whatever work you have to do on work
            self.q.task_done()

    def function_treat(self,work:dict):
        if type(self.function)==type([]):
            if self.index<len(self.function):
                self.index+=1
                return self.function[self.index-1](**work)
            else:
                self.index=0
                return self.function[self.index](**work)
        else:
            return self.function(**work)

    def function_element(self):
        while True:
            try:
                work = self.q.get()
                if self.retroativo!="":
                    work[self.retroativo]=self.retorno[self.index_retorno]
                result=self.function_treat(work)
                if self.retorno != None:
                    if self.function_array:
                        self.retorno[self.index_retorno].append(result)
                    else:
                        self.retorno[self.index_retorno]+=result
            except Empty:
                return 
            finally:
            # do whatever work you have to do on work
                self.q.task_done()

    def run(self):
        if self.operacao==1:
            self.print_element()
        elif self.operacao==2:
            self.sum_element()
        elif self.operacao==3:
            self.function_element()
        else:
            return None

    def exec_print(self):
        self.operacao=1

    def exec_sum(self,retorno,index_retorno=None):
        self.retorno=retorno
        if index_retorno != None:
            self.index_retorno=index_retorno
            if self.retorno !=None:
                self.retorno[self.index_retorno]=0
        self.operacao=2

    def exec_function(self,function,retorno=None,index_retorno=None,function_array=False,retroativo=""):
        self.exec_sum(retorno,index_retorno)
        self.operacao=3
        self.function=function
        self.function_array=function_array
        self.retroativo=retroativo
        if function_array:
            self.retorno[self.index_retorno]=[]

class Paralel_thread:
    def __init__(self,total_threads:int,max_size:int=0):
        self.q=Queue(maxsize=max_size)
        self.threads=[]
        self.resultados=[]
        for _ in range(total_threads):
            self.threads.append([])
            self.resultados.append(0)
        
    def execute(self,elementos,function,retorno=None,join:bool=False):
        for j in elementos:
                self.q.put(j)
        for i in range(len(self.threads)):
            self.threads[i]=Worker_thread(self.q)
            self.threads[i].exec_function(function=function,index_retorno=i,retorno=retorno)
            self.threads[i].setDaemon(True)
            self.threads[i].start()
        if join is True:
            return self.q.join()
