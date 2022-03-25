import csv,os,ast
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
from altair_saver import save as saver
from interacaoSqlite import InteracaoSqlite

def save_img(values,nome_tabela,path="./",img_unificada:bool=False):
    try:
        array_img_separada=(type(values[0]) == type([]) and img_unificada==False)
    except:
        array_img_separada=False
    array_img_junta= (type(values) == type([]) and img_unificada==True)
    if array_img_separada or array_img_junta:
        for i in range(len(values)):
            save_img(values[i],nome_tabela+str(i),path=path,img_unificada=img_unificada)
    else:
        if img_unificada == False:
            values[0].figure.savefig(path+"uso de cpu container "+nome_tabela+".svg", format="svg")
            values[1].figure.savefig(path+"uso de ram container "+nome_tabela+".svg", format="svg")
            values[2].figure.savefig(path+"uso de disco container "+nome_tabela+".svg", format="svg")
        else:
            values.figure.savefig(path+"uso do container "+nome_tabela+".svg", format="svg")
   
def save_html(values,nome_tabela,path="./"):
    #alt.renderers.enable('mimetype')
    alt.renderers.enable('altair_viewer')
    # alt.renderers.enable('altair_saver', ['vega-lite','svg'])
    #alt.data_transformers.enable('data_server')
    # alt.data_transformers.register('custom', t)
    # alt.data_transformers.enable('custom')
    alt.renderers.enable('altair_viewer', embed_options={'renderer': 'svg'})
    alt.data_transformers.enable('json')
    alt.data_transformers.enable('default', max_rows=None)
    try:
        if type(values) ==type([]):
            for i in range(len(values)):
                save_html(values[i],nome_tabela+str(i),path=path)
        else:
            saver(values,path+"dados do container "+nome_tabela+".html")
    except KeyError as e:
        saver(values,path+"dados do container "+nome_tabela+".html")

if __name__ == "__main__":
    path="/media/mzramna/Novo volume/"
    intervalo=5000
    arquivo_sqlite="/home/mzramna/Downloads/initial_db.db"
    arquivo_csv_extraido=path+"quantidades_operacoes.csv"
    processar_sqlite=False
    if processar_sqlite ==True:
        contadores=[0,0,0,0,0,0]
        contador_final=[]
        sqlite=InteracaoSqlite(sqlite_db=arquivo_sqlite,level=50)
        for i in range(1,5000000,intervalo):
            contador_final.append({"operacao_1":0,"operacao_2":0,"operacao_3":0,"operacao_4":0,"operacao_5":0,"operacao_6":0})
            for j in range(i,i+intervalo):
                operacoes=sqlite.read_operacoes(filtro="tipoOperacao",query={"id":j},tipo_adicional="none_dados")
                for operacao in operacoes:
                    contadores[operacao["tipoOperacao"]-1]+=1
                    contador_final[-1]["operacao_"+str(operacao["tipoOperacao"])]+=1
            #print(contadores)
            #print(sum(contadores))
        file_=open(arquivo_csv_extraido,"w")
        csv_save=csv.DictWriter(file_,fieldnames=list(contador_final[-1].keys()))
        csv_save.writerows(contador_final)
        file_.close()
    file_=open(arquivo_csv_extraido,"r")
    csv_read=csv.DictReader(file_,fieldnames=["operacao_1","operacao_2","operacao_3","operacao_4","operacao_5","operacao_6"])
    max_value=0
    min_value=100
    for line in csv_read:
        print(line)
        elementos=[]
        labels=[]
        for i in list(line.items()):
            elementos.append(int(i[1]))
            percent=str("%.2f" % ((int(i[1])/5000)*100))
            if ((int(i[1])/5000)*100)>max_value and i[0] !="operacao_1":
                max_value=((int(i[1])/5000)*100)
            if ((int(i[1])/5000)*100)<min_value and i[0] !="operacao_5":
                min_value=((int(i[1])/5000)*100)
            labels.append(i[0]+"   "+percent+"%")
        pie=plt.pie(elementos,labels=labels)
        plt.show(block=False)
        plt.pause(0.00000001)
        plt.clf()
    print(max_value,min_value)
    file_.close()