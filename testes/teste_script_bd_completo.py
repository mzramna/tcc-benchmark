from gerenciadorDeBD import GerenciadorDeBD


logstash_data={"host":"192.168.0.116","port":5000,"username":"elastic","password":"changeme"}
#logstash_data={"host":"192.168.0.116","port":5000}
logstash_data={}

gerenciador=GerenciadorDeBD(host="192.168.0.100", user="mzramna", password="safePassword", database="sakila", port=3306,tipo=0,sql_file_pattern="containers_build/mysql default exemple.sql",logstash_data=logstash_data)
for i in range(30):
    print(gerenciador.get_status())
# #reset
# gerenciador.reset_database()
#gerenciador.execute_operation_from_sqlite_no_return(2000, "scripts/initial_db.db")

# gerenciador=GerenciadorDeBD(host="192.168.0.100", user="mzramna", password="safePassword", database="sakila", port=5432,tipo=1,sql_file_pattern="containers_build/postgres default exemple.sql",logstash_data=logstash_data)
#reset
# gerenciador.reset_database()
# gerenciador.execute_operation_from_sqlite_no_return(2000, "scripts/initial_db.db")

# import psycopg2
# import ctypes
# mydb=psycopg2.connect(
#                             host="192.168.0.100",
#                             user="mzramna",
#                             password="safePassword",
#                             database="sakila",
#                             port=5432
#                             )
# for i in range(30):
#     tmp=mydb.info
#     print(tmp)