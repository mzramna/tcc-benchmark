import mysql.connector
import sys
from os import DirEntry
from geradorDeSql import GeradorDeSql
def executeScriptsFromFile(filename:DirEntry,cursor:mysql.connector.connection_cext.CMySQLConnection):
    """[executa arquivos sql em bd mariqdb ou mysql]

    Args:
        filename (DirEntry): [diretorio onde está o arquivo sql]
        cursor (mysql.connector.connection_cext.CMySQLConnection): [connector do mysql]
    """    
    fd = open(filename, 'r')
    sqlFile = fd.read()
    fd.close()
    sqlCommands = sqlFile.split(';')

    for command in sqlCommands:
        try:
            if command.strip() != '':
                cursor.execute(command)
        except IOError as msg:
            print ("Command skipped: ", msg)

mydb = mysql.connector.connect(
  host="192.168.0.100",
  user="mzramna",
  password="safePassword",
  database="sakila",
  port=3306
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
executeScriptsFromFile("containers_build/mysql default exemple.sql" , mycursor)

for i in gerador.gernerate_lib_insertion_from_sqlite_range(50,sql=True):
    print(i)
    #mycursor.execute(i[0],i[1])#usando o lib não funciona no momento,algo a ver com sintaxe sql incompativel
    mycursor.execute(i)
    mydb.commit()