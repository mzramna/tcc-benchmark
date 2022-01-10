from time import sleep,perf_counter
from queue import Queue
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
                if self.function_array:
                    self.retorno[self.index_retorno].append(result)
                else:
                    self.retorno[self.index_retorno]+=result
            except queue.Empty:
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
            self.retorno[self.index_retorno]=0
        self.operacao=2

    def exec_function(self,retorno,function,index_retorno=None,function_array=False,retroativo=""):
        self.exec_sum(retorno,index_retorno)
        self.operacao=3
        self.function=function
        self.function_array=function_array
        self.retroativo=retroativo
        if function_array:
            self.retorno[self.index_retorno]=[]

class Timer:

    def __init__(self):

        self._start_time = None


    def inicio(self):

        """Start a new timer"""

        if self._start_time is not None:

            raise TimerError(f"Timer is running. Use .stop() to stop it")


        self._start_time = perf_counter()


    def fim(self,print_=False):

        """Stop the timer, and report the elapsed time"""

        if self._start_time is None:

            raise TimerError(f"Timer is not running. Use .start() to start it")


        elapsed_time = perf_counter() - self._start_time

        self._start_time = None
        if print_:
            print(f"Elapsed time: {elapsed_time:0.4f} seconds")
        return float(f"{elapsed_time:0.6f}")

def soma(a,b):
    c=a+b
    print(a,b,c)
    return c

array=[]
total_threads=10
threads=[]
resultados=[]
total_elementos=100
for _ in range(total_threads+1):
    threads.append([])
    resultados.append(0)
tempos={}
for i in range(total_elementos):
    array.append(i)

q = Queue(maxsize=0)
timer=Timer()
for i in array:
    q.put({"a":i,"b":0})
timer.inicio()
for i in range(len(threads)):
    threads[i]=Worker(q)
    threads[i].exec_function(retorno=resultados,function= soma,index_retorno=i,retroativo="")
    threads[i].setDaemon(True)
    threads[i].start()
q.join()

tempos["paralelo"]=timer.fim()



# timer.inicio()
# for i in array:
#     print(i)
# tempos["sequencial"]=timer.fim()


print(resultados)
timer.inicio()
resultado_correto=0
for i in range(total_elementos):
    resultado_correto+=soma(a=i,b=0)
tempos["sequencial"]=timer.fim()
print(tempos)
print("resultado encontrado",sum(resultados))
print("resultado correto",resultado_correto)
# for i in range(len(threads)):
#     threads[i].kill()