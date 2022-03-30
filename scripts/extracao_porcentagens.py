import csv,os,pprint,math

def agrupar_porcentagem_cpu(arquivo_csv,coluna:str):
    resultados=[]
    for i in range(0,11):
        resultados.append([])
        for i in range(0,10):
            resultados[-1].append(0)
    for i in arquivo_csv:
        for j in range(0,11):
            value=float(i[coluna])
            if value > (j-1)*10 and value<(j*10):
                sub=math.trunc(value % 10)
                resultados[j-1][sub]+=1
    return resultados
    
def agrupar_porcentagem_ram(arquivo_csv):
    resultados=[]
    for i in range(0,11):
        resultados.append([])
        for i in range(0,10):
            resultados[-1].append(0)
    for i in arquivo_csv:
        for j in range(0,11):
            pct=( int(i["ram_used"])/int(i["ram_available"]))*100
            if pct > (j-1)*10 and pct<(j*10):
                sub=math.trunc(pct % 10)
                resultados[j-1][sub]+=1
    return resultados
    
def analise_de_resultado_intervalo(valores:list,campo:str):
    tmp=[]
    for linha in valores:
        tmp_2=0
        for i in linha:
            tmp_2+=i
        tmp.append(tmp_2)
    tmp_2=0
    for i in range(0,len(tmp)):
        if tmp[i]>tmp[tmp_2]:
            tmp_2=i
    valor="a faixa com mais ocorrencias de uso de "+campo+" é de "+str(10*(tmp_2+1))
    print(valor)
    return valor

def analise_de_resultado_individual(valores:list,campo:str):
    tmp=(0,0)
    for x in range(len(valores)):
        for y in range(len(valores[x])):
            if valores[x][y]>valores[tmp[0]][tmp[1]]:
                tmp=(x,y)

    valor="o valor com mais ocorrencias de uso de "+campo+" é "+str(tmp[0])+str(tmp[1])
    print(valor)
    return valor

def processar(in_,save=False,file_out=""):
    csv_file=csv.DictReader(open(in_,"r"))
    porcentagem_ram=agrupar_porcentagem_ram(csv_file)
    porcentagem_cpu=[]
    cpu_headers=[]
    for i in csv_file.fieldnames:
        if "cpu_percent_" in i:
            cpu_headers.append(i)
    porcentagem_cpu=[]
    for i in range(0,11):
        porcentagem_cpu.append([0 for i in range(10)])
    for i in cpu_headers:
        csv_file=csv.DictReader(open(in_,"r"))
        porcentagem_cpu_1=agrupar_porcentagem_cpu(csv_file,i)
        for j in range(0,11):
            for k in range(0,10):
                porcentagem_cpu[j][k]+=porcentagem_cpu_1[j][k]
    
    pprint.pprint(porcentagem_ram)
    pprint.pprint(porcentagem_cpu)
    saida_ram_intervalo=analise_de_resultado_intervalo(porcentagem_ram,"ram")
    saida_ram_individual=analise_de_resultado_individual(porcentagem_ram,"ram")
    saida_cpu_intervalo=analise_de_resultado_intervalo(porcentagem_cpu,"cpu")
    saida_cpu_individual=analise_de_resultado_individual(porcentagem_cpu,"cpu")
    if save == True:
        file_log=open(file_out,"w")
        file_log.write("uso de ram\n")
        for linha in porcentagem_ram:
            file_log.write(str(linha))
            file_log.write("\n")
        file_log.write(saida_ram_intervalo)
        file_log.write("\n")
        file_log.write(saida_ram_individual)
        [file_log.write("\n") for i in range(4)]
        file_log.write("uso de cpu\n")
        for linha in porcentagem_cpu:
            file_log.write(str(linha))
            file_log.write("\n")
        file_log.write(saida_cpu_intervalo)
        file_log.write("\n")
        file_log.write(saida_cpu_individual)
        file_log.close()

out_="z:\codigos\\tcc-benchmark\\texto\\tcc-benchmark-texto\\resultados\\"
for root, dirs, files in os.walk(out_):
    for name in files:
        if name.endswith(".csv"):
            "container_mariadb_amd_limpo"
            tmp=name[10:-9]
            arquivo=root+os.sep+name
            arquivo_out=root+os.sep+tmp+"processados.log"
            processar(arquivo,save=True,file_out=arquivo_out)

