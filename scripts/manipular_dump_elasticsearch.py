import csv,os,ast
import re,random
import manipulacao_csv
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
from altair_saver import save as saver

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
            cpu_dict={}
            for dado in range(len( tmp_dict)):
                cpu_dict[list(tmp_dict.keys())[dado]]=tmp_dict[list(tmp_dict.keys())[dado]]
                tmp_result[list(tmp_dict.keys())[dado]]=tmp_dict[list(tmp_dict.keys())[dado]]
            tmp_result["cpu_percent"]=cpu_dict
            tmp_dict=ast.literal_eval(linha["virtual_memory"])
            tmp_dict_2={}
            for dado in tmp_dict:
                tmp_dict_2[dado]=tmp_dict[dado]
            tmp_result["ram_used"]=tmp_dict_2["used"]
            tmp_result["ram_available"]=tmp_dict_2["available"]
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

def plot_graphs(arquivo_processado,jpg=True,html=True,show=True,save=True,resize=None):
    #alt.renderers.enable('mimetype')
    alt.renderers.enable('altair_viewer')
    # alt.renderers.enable('altair_saver', ['vega-lite','svg'])
    #alt.data_transformers.enable('data_server')
    # alt.data_transformers.register('custom', t)
    # alt.data_transformers.enable('custom')
    alt.renderers.enable('altair_viewer', embed_options={'renderer': 'svg'})
    alt.data_transformers.enable('json')
    alt.data_transformers.enable('default', max_rows=None)

    def pctg(total,usada):
        return (usada/total)*100
    
    df=pd.read_csv(open(arquivo_processado,"r"))#,index_col='@timestamp'
    nome_tabela=os.path.basename(arquivo_processado)[:-4]
    
    df['@timestamp'] = pd.to_datetime(df['@timestamp'])
    try:
        df['disk_write_speed']=df['sda_write_bytes'].sub(df['sda_write_bytes'].shift())
        df['disk_read_speed']=df['sda_read_bytes'].sub(df['sda_read_bytes'].shift())
    except:
        df['disk_write_speed']=df['sdb_write_bytes'].sub(df['sdb_write_bytes'].shift())
        df['disk_read_speed']=df['sdb_read_bytes'].sub(df['sdb_read_bytes'].shift())
    df['net_recive']=df['net_bytes_recv'].sub(df['net_bytes_recv'].shift())
    df['net_sent']=df['net_bytes_sent'].sub(df['net_bytes_sent'].shift())
    df["ram_pctg"]= pd.to_numeric(pctg(df["ram_available"],df["ram_used"]))
    cpus_to_list=[]
    for header in list(df.keys()):
        if "cpu_percent_" in header:
            df[header] = pd.to_numeric(df[header])
            cpus_to_list.append(header)
    if jpg==True:
        #print(df.head())
        # df.to_json(arquivo_json, orient='records')
        # df.to_csv(arquivo_processado)
        
        cpu=df.plot(x="@timestamp",figsize=(40,3),title="uso de cpu container "+nome_tabela,y=cpus_to_list)
        ram=df.plot(x="@timestamp",figsize=(40,3),title="uso de ram container "+nome_tabela,y=["ram_pctg"])
        disco=df.plot(x="@timestamp",figsize=(40,3),title="uso de disco container "+nome_tabela,y=["disk_write_speed","disk_read_speed"])
        #rede problematico devido a forma que o contador de uso do linux contabiliza quando reiniciado o container
        # rede=df.plot(x="@timestamp",figsize=(40,3),title="uso de rede container "+nome_tabela,y=["net_recive","net_sent"])
        
        if show==True:
            plt.show(block=True)
        if save==True:
            cpu.figure.savefig("uso de cpu container "+nome_tabela+".png")
            ram.figure.savefig("uso de ram container "+nome_tabela+".png")
            disco.figure.savefig("uso de disco container "+nome_tabela+".png")
            # rede.figure.savefig("uso de rede container "+nome_tabela+".png")
    arquivo_json=nome_tabela+".json"
    df.to_json(arquivo_json, orient='records')
    if html == True:
        linha_cpu=[]
        linha_disco=[]
        linha_rede=[]
        #dado_altair="file://"+arquivo_processado
        # dado_altair=arquivo_json
        dado_altair=df
        if resize == None:
            resize = alt.selection_interval(bind='scales')
        label = alt.selection_single(
            encodings=['x'], # limit selection to x-axis value
            on='mouseover',  # select on mouseover events
            nearest=True,    # select data point nearest the cursor
            empty='none'     # empty selection includes no data points
        )
        alt_global=alt.Chart(dado_altair).mark_line()
        color_layer=[
                'black', 'maroon', 'red', 'purple', 'fuchsia', 'green', 'lime', 'olive', 'navy', 'blue', 'teal', 'aqua', 'orange', 'aquamarine', 'azure', 'beige', 'bisque', 'blanchedalmond', 'blueviolet', 'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkgrey', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray', 'darkslategrey', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue', 'dimgray', 'dimgrey', 'dodgerblue', 'firebrick', 'floralwhite', 'forestgreen', 'gainsboro', 'ghostwhite', 'gold', 'goldenrod', 'greenyellow', 'grey', 'honeydew', 'hotpink', 'indianred', 'indigo', 'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen', 'lemonchiffon','lightcoral', 'linen', 'magenta', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mintcream', 'mistyrose', 'moccasin', 'navajowhite', 'oldlace', 'olivedrab', 'orangered', 'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'plum', 'powderblue', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna', 'skyblue', 'slateblue', 'slategray', 'slategrey', 'snow', 'springgreen', 'steelblue', 'tan', 'thistle', 'tomato', 'turquoise', 'violet', 'wheat', 'whitesmoke', 'yellowgreen', 'rebeccapurple'
            ]
        for cpu_ in cpus_to_list:
            radio_select = alt.selection_multi(
            fields=cpus_to_list, name=cpu_, 
            )

            color=random.choice(color_layer)
            color_layer.remove(color)
            
            linha_cpu.append(alt_global.mark_line(color=color).encode(
                alt.X("@timestamp:T",axis=alt.Axis(title="tempo")),
                alt.Y(cpu_,axis=alt.Axis(title="cpu")),
                # color=cpus_to_list
                )
            )
        alt_cpu = alt.layer(
                *linha_cpu,
                data=dado_altair
            ).interactive().add_selection(resize)
        
        alt_ram= alt_global.encode( 
        alt.X("@timestamp:T",axis=alt.Axis(title="tempo")),
        alt.Y("ram_pctg:Q",axis=alt.Axis(title="porcentagem de uso de ram")),
        ).interactive().add_selection(resize)

        for disco_ in ["disk_write_speed","disk_read_speed"]:
            radio_select = alt.selection_multi(
            fields=["disk_write_speed","disk_read_speed"], name=disco_, 
            )

            color=random.choice(color_layer)
            color_layer.remove(color)
            
            linha_disco.append(
                alt.layer(
                    alt_global.mark_line(color=color).encode(
                        alt.X("@timestamp:T",axis=alt.Axis(title="tempo")),
                        alt.Y(disco_+":Q",axis=alt.Axis(title=disco_)),
                        # color=["disk_write_speed","disk_read_speed"]
                    )
                )
            )
        alt_disco = alt.layer(
                *linha_disco,
                data=dado_altair
            ).interactive().add_selection(resize)
        
        
        for rede_ in ["net_recive","net_sent"]:
            radio_select = alt.selection_multi(
            fields=["net_recive","net_sent"], name=rede_, 
            )

            color=random.choice(color_layer)
            color_layer.remove(color)
            
            linha_rede.append(
                alt.layer(
                    alt_global.mark_line(color=color).encode(
                        alt.X("@timestamp:T",axis=alt.Axis(title="tempo")),
                        alt.Y(rede_+":Q",axis=alt.Axis(title=rede_)),
                        # color=["disk_write_speed","disk_read_speed"]
                    )
                )
            )
        #rede problematico devido a forma que o contador de uso do linux contabiliza quando reiniciado o container
        # alt_rede = alt.layer(
        #         *linha_rede,
        #         data=dado_altair
        #     ).interactive().add_selection(resize)
        alt_resultado =alt.vconcat( alt_cpu, alt_ram,alt_disco)
        if show==True:
            alt_resultado.display(renderer="svg")
            alt_resultado.show()
        if save==True:
            saver(alt_resultado,"dados do container "+nome_tabela+".html")

    if jpg == True and html ==False:
        return [cpu,ram,disco]
    elif jpg == False and html ==True:
        return alt_resultado
    else:
        return [cpu,ram],alt_resultado

if __name__ == "__main__":
    # arquivos=os.listdir("/mnt/dados/csvs/")
    # for arquivo in arquivos:
    #     if arquivo.endswith(".csv") and not arquivo.endswith("_processado.csv"):
    #         filtrar_csv_util(os.path.join("/mnt/dados/csvs/", arquivo),os.path.join("/mnt/dados/csvs/", arquivo[:-4]+"_processado.csv"))
    arquivos=os.listdir("/mnt/dados/csvs/")
    resize = alt.selection_interval(bind='scales')
    resultados=[]
    for arquivo in arquivos:
        if arquivo.endswith("_processado.csv"):
            resultados.append(plot_graphs(os.path.join("/mnt/dados/csvs/",arquivo),jpg=False,html=True,save=True,show=False,resize=resize))
    
    final=alt.hconcat(*resultados)
    final.save("dados do container concatenados.html",embed_options={'renderer':'svg'})
    saver(final,"dados do container concatenados.svg")
#colocar arquivos que serao acessados,filtrar apenas os dados usaveis,atualizar arquivos pra serem menores,fazer implementação que ja recebe do elasticsearch,limpa e salva os dados ordenados
