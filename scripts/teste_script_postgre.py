import psycopg2
import sys
from os import DirEntry
from geradorDeSql import GeradorDeSql
import traceback

mydb = psycopg2.connect(
  host="192.168.0.100",
  user="mzramna",
  password="safePassword",
  database="sakila",
  port=5432
)

print(mydb)
mycursor = mydb.cursor()

# executeScriptsFromFile("containers_build/mysql default exemple.sql",mycursor)
# mycursor.execute("SHOW TABLES")

# for x in mycursor:
#   print(x)

  #logstash_data={"host":"192.168.0.116","port":5000,"username":"elastic","password":"changeme"}
#logstash_data={"host":"192.168.0.116","port":5000}
logstash_data={}

gerador=GeradorDeSql(sqlite_db="scripts/initial_db.db",sql_file_pattern="scripts/sqlitePattern.sql", log_file="scripts/geradorSQL.log",level=40,logging_pattern='%(asctime)s - %(name)s - %(levelname)s - %(message)s',logstash_data=logstash_data)

#reset
mycursor.execute(open("containers_build/postgres default exemple.sql","r").read())
mydb.commit()
for i in gerador.gernerate_lib_insertion_from_sqlite_range(2000,sql=True):
    print(i)
    #mycursor.execute(i[0],i[1])#usando o lib não funciona no momento,algo a ver com sintaxe sql incompativel
    try:
      mycursor.execute(i)
    except psycopg2.errors.ForeignKeyViolation as e:
      traceback.print_exc()
    try:
      mydb.commit()
    except:
      try:
        mycursor.fetchall()
      except:
        pass