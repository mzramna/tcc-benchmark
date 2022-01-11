from queue import Queue,Empty
from threading import Thread

class Worker(Thread):
    def __init__(self, q,  *args, **kwargs):
        self.q = q
        self.operacao=0
        super().__init__(*args, **kwargs)

    def print_element(self):
        while True:
            try:
                work = self.q.get()  # 3s timeout
                print(work)
            except queue.Empty:
                return
            # do whatever work you have to do on work
            self.q.task_done()

    def sum_element(self):
        while True:
            try:
                work = self.q.get()  # 3s timeout
                self.retorno[self.index_retorno]+=work
            except queue.Empty:
                return 
            # do whatever work you have to do on work
            self.q.task_done()

    def function_element(self):
        while True:
            try:
                work = self.q.get()  # 3s timeout
                if self.retroativo!="":
                    work[self.retroativo]=self.retorno[self.index_retorno]
                result=self.function(**work)
                if self.retorno != None:
                    if self.function_array:
                        self.retorno[self.index_retorno].append(result)
                    else:
                        self.retorno[self.index_retorno]+=result
            except Empty:
                return 
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

class Paralel:
    def __init__(self,total_threads:int,elementos:list,function,max_size:int=0):
        self.q=Queue(maxsize=max_size)
        self.threads=[]
        self.resultados=[]
        self.function=function
        for _ in range(total_threads):
            self.threads.append([])
            self.resultados.append(0)
        for i in elementos:
            self.q.put(i)
        
    def execute(self,retorno=None):
        for i in range(len(self.threads)):
            self.threads[i]=Worker(self.q)
            self.threads[i].exec_function(function=self.function,index_retorno=i,retorno=retorno)
            self.threads[i].setDaemon(True)
            self.threads[i].start()
        self.q.join()
