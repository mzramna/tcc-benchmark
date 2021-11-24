from  geradorDeSql import GeradorDeSql


for i in range(3,20):
    for j in range(4000):
        try:
            analize=list(range(1, i))
            tmp=GeradorDeSql.dividir_array(analize)
            #print("array",tmp)
            for B in tmp:
                analize=[analize[k] for k in B if k<len(analize)] + [analize[k] for k in range(len(analize)) if k not in set(B)]
            if len(analize)>0:
                raise
            
        except :
            print("valor:",i,"loop:",j)
            
        finally:
            pass