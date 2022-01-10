from gerenciadorDeBD import GerenciadorDeBD
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

array=[]
total_threads=10
threads=[]
total_elementos=10000
for _ in range(total_threads+1):
    threads.append([])
for i in range(total_elementos):
    array.append(i)
q = Queue(maxsize=0)
for i in array:
    q.put({"id":i,"sqlite_file":"scripts/initial_db.db"})#    def generate_lib_insertion_from_sqlite_id(self,id:int,sqlite_db:DirEntry,sql:bool=False)->str:
#logstash_data={"host":"192.168.0.116","port":5000,"username":"elastic","password":"changeme"}
#logstash_data={"host":"192.168.0.116","port":5000}
logstash_data={}

gerenciador=GerenciadorDeBD(host="192.168.0.100", user="mzramna", password="safePassword", database="sakila", port=3306,tipo=0,sql_file_pattern="containers_build/mysql default exemple.sql",logstash_data=logstash_data)
#reset
gerenciador.reset_database()

for i in range(len(threads)):
    threads[i]=Worker(q)
    threads[i].exec_function(function= gerenciador.execute_operation_from_sqlite_no_return_with_id,index_retorno=i)
    threads[i].setDaemon(True)
    threads[i].start()
q.join()


# gerenciador=GerenciadorDeBD(host="192.168.0.100", user="mzramna", password="safePassword", database="sakila", port=5432,tipo=1,sql_file_pattern="containers_build/postgres default exemple.sql",logstash_data=logstash_data)
# #reset
# gerenciador.reset_database()
# gerenciador.execute_operation_from_sqlite_no_return(2000, "scripts/initial_db.db")