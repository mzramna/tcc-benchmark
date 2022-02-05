import psycopg2

con=psycopg2.connect(host='192.168.0.10', database='sakila',port=5432,
user='ibd4bhkjpyi4hx', password='mls83mfbsdnvte')

mensagens=["INSERT INTO country (country,last_update) VALUES ('Brazil','2001-04-08 00:00:00'); ", 
           "INSERT INTO country (country,last_update) VALUES ('Brazil','2016-03-10 00:00:00'); ",
           "INSERT INTO category (name,last_update) VALUES ('fugit','2016-03-10 00:00:00'); ", "INSERT INTO country (country,last_update) VALUES ('Brazil','2005-05-01 00:00:00'); ", 
           "INSERT INTO category (name,last_update) VALUES ('molestias','1997-05-29 00:00:00'); ",
           "INSERT INTO country (country,last_update) VALUES ('Brazil','1997-05-29 00:00:00'); ", 
           "INSERT INTO category (name,last_update) VALUES ('maiores','2015-06-24 00:00:00'); ", 
           "INSERT INTO country (country,last_update) VALUES ('Brazil','2020-05-26 00:00:00'); ",
           "INSERT INTO category (name,last_update) VALUES ('exercitationem','1992-08-22 00:00:00'); ", 
           "INSERT INTO country (country,last_update) VALUES ('Brazil','2004-06-24 00:00:00'); ", 
           "INSERT INTO category (name,last_update) VALUES ('adipisci','2011-10-19 00:00:00'); ",
           "INSERT INTO country (country,last_update) VALUES ('Brazil','2015-06-24 00:00:00'); ", 
           "INSERT INTO category (name,last_update) VALUES ('aliquid','2018-03-16 00:00:00'); ", 
           "INSERT INTO actor (first_name,last_name,last_update) VALUES ('Marcelo','Nogueira','1997-05-29 00:00:00'); "]
    


for elemento in mensagens:
    try:
        cur = con.cursor()
        cur.execute(elemento)
        con.commit()
        
    except BaseException as e:
        con.rollback()
        print(e)
    cur.close()
con.close()