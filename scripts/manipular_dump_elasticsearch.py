import csv,os,ast
import re
import manipulacao_csv
import pandas as pd


def filtrar_csv_util(arquivo,saida=0):
    headers=[]
    output=[]
    with open(arquivo,"r") as csv_read:
        for linha in csv.DictReader(csv_read):
            tmp_result={}
            #tmp_result["logger_name"]=linha["logger_name"]
            tmp_result["@timestamp"]=linha["@timestamp"]
            tmp_dict=ast.literal_eval(linha["disk_io_counters"])
            for dado in tmp_dict:
                pattern = r"(\w+)=([0-9]+),"
                tmp_dict_2={}
                for m in re.findall(pattern=pattern,string= re.search(r'sdiskio\((.*)\)',tmp_dict[dado]).group(1)):
                    tmp_dict_2[dado+"_"+m[0]]=int(m[1])
                tmp_result[dado+"_read_bytes"]=tmp_dict_2[dado+"_read_bytes"]
                tmp_result[dado+"_write_bytes"]=tmp_dict_2[dado+"_write_bytes"]
                tmp_dict_2={}
            tmp_dict=ast.literal_eval(linha["cpu_percent"])
            for dado in tmp_dict:
                tmp_result[dado]=tmp_dict[dado]
            tmp_result["container_root_usage_percent"]=ast.literal_eval(linha["disk_usage"])["percent"]
            tmp_dict=ast.literal_eval(linha["net_io_counters"])
            tmp_dict_2={}
            for dado in tmp_dict:
                tmp_dict_2[dado]=tmp_dict[dado]
            tmp_result["net_bytes_recv"]=tmp_dict_2["bytes_recv"]
            tmp_result["net_bytes_sent"]=tmp_dict_2["bytes_sent"]
            output.append(tmp_result)
        headers=list(output[0].keys())
        csv_read.close()
    if saida == 0:
        return output
    with open(saida,"w") as csv_write:
        writer = csv.DictWriter(csv_write, fieldnames=headers)
        writer.writeheader()
        writer.writerows(output)
        csv_write.close()

def plot_graphs(arquivo_processado):
    df=pd.read_csv(open(arquivo_processado,"r"))
    df.head()
    cpu=df.plot(x="@timestamp",figsize=(20,3),title="uso de cpu container")
    pass

if __name__ == "__main__":
    arquivos=os.listdir("/mnt/dados/csvs/")
    # for arquivo in arquivos:
    #     if arquivo.endswith(".csv") and not arquivo.endswith("_processado.csv"):
    #         filtrar_csv_util(os.path.join("/mnt/dados/csvs/", arquivo),os.path.join("/mnt/dados/csvs/", arquivo[:-4]+"_processado.csv"))
    arquivos=os.listdir("/mnt/dados/csvs/")
    for arquivo in arquivos:
        if arquivo.endswith("_processado.csv"):
            plot_graphs(os.path.join("/mnt/dados/csvs/",arquivo))
#colocar arquivos que serao acessados,filtrar apenas os dados usaveis,atualizar arquivos pra serem menores,fazer implementação que ja recebe do elasticsearch,limpa e salva os dados ordenados