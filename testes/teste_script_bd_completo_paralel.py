from gerenciadorDeBD import GerenciadorDeBD
from worker import Paralel_thread


array=[]
total_threads=5
threads=[]
total_elementos=10000
for _ in range(total_threads):
    threads.append([])
for i in range(total_elementos):
    array.append({"id":i,"sqlite_file":"scripts/initial_db.db"})

#logstash_data={"host":"192.168.0.116","port":5000,"username":"elastic","password":"changeme"}
#logstash_data={"host":"192.168.0.116","port":5000}
logstash_data={}

gerenciador=GerenciadorDeBD(host="192.168.0.100", user="mzramna", password="safePassword", database="sakila", port=3306,tipo=0,sql_file_pattern="containers_build/mysql default exemple.sql",logstash_data=logstash_data,level=40)
#reset
gerenciador.reset_database()

p=Paralel_thread(total_threads=total_threads,elementos=array,function=gerenciador.execute_operation_from_sqlite_no_return_with_id)
p.execute()

# gerenciador=GerenciadorDeBD(host="192.168.0.100", user="mzramna", password="safePassword", database="sakila", port=5432,tipo=1,sql_file_pattern="containers_build/postgres default exemple.sql",logstash_data=logstash_data)
# #reset
# gerenciador.reset_database()
# gerenciador.execute_operation_from_sqlite_no_return(2000, "scripts/initial_db.db")