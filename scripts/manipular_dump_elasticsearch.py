import csv,os,ast
import re,random
import manipulacao_csv
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
from altair_saver import save as saver

def save_jpg(values,nome_tabela,path="./"):
    try:
        if type(values[0]) == list:
            for i in range(len(values)):
                save_jpg(values[i],nome_tabela+str(i),path=path)
        else:
            values[0].figure.savefig(path+"uso de cpu container "+nome_tabela+".png")
            values[1].figure.savefig(path+"uso de ram container "+nome_tabela+".png")
            values[2].figure.savefig(path+"uso de disco container "+nome_tabela+".png")
    except KeyError as e:
        values[0].figure.savefig(path+"uso de cpu container "+nome_tabela+".png")
        values[1].figure.savefig(path+"uso de ram container "+nome_tabela+".png")
        values[2].figure.savefig(path+"uso de disco container "+nome_tabela+".png")
        
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
        
def filtrar_csv_util(arquivo,saida=0):
    headers=[]
    output=[]
    n_linha=0
    with open(arquivo,"r") as csv_read:
        for linha in csv.DictReader(csv_read):
            n_linha+=1
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

def process_dataframe(arquivo_processado,criar_json=True,return_name=False):
    def pctg(total,usada):
        return (usada/total)*100
    
    df=pd.read_csv(arquivo_processado)#,index_col='@timestamp'
    nome_tabela=arquivo_processado.name[:-4]
    
    df['@timestamp'] = pd.to_datetime(df['@timestamp'])
    try:
        df['disk_write_speed']=df['sda_write_bytes'].sub(df['sda_write_bytes'].shift())
        df['disk_read_speed']=df['sda_read_bytes'].sub(df['sda_read_bytes'].shift())
    except KeyError as e:
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
    if criar_json == True:
        arquivo_json=nome_tabela+".json"
        df.to_json(arquivo_json, orient='records')
    if return_name==True:
        return df,nome_tabela
    else:
        return df

def split_csv_files(arquivo_processado,temporary_name_prefix:str="/tmp/tmp",column:str="net_bytes_sent"):
    csv_reader = list(csv.DictReader(arquivo_processado, delimiter=','))
    file_lines=[]
    created_files=[]
    line_num=0
    temporary_file_counter=0
    for row in range(len(csv_reader)):
        line_num+=1
        analize_row=csv_reader[row][column]
        if line_num>1 and int(analize_row)< int(csv_reader[row-1][column]):
            with open(str(temporary_name_prefix+"_"+str(temporary_file_counter)+".csv"),mode="w") as write_file:
                csv_writer=csv.DictWriter(write_file,fieldnames=list(csv_reader[row].keys()))
                csv_writer.writeheader()
                csv_writer.writerows(file_lines)
                write_file.close()
                created_files.append(str(temporary_name_prefix+"_"+str(temporary_file_counter)+".csv"))
            temporary_file_counter+=1
            file_lines=[csv_reader[row]]
        else:
            file_lines.append(csv_reader[row])
    with open(str(temporary_name_prefix+"_"+str(temporary_file_counter)+".csv"),mode="w") as write_file:
        csv_writer=csv.DictWriter(write_file,fieldnames=list(csv_reader[row].keys()))
        csv_writer.writeheader()
        csv_writer.writerows(file_lines)
        write_file.close()
        created_files.append(str(temporary_name_prefix+"_"+str(temporary_file_counter)+".csv"))
    print(str(temporary_file_counter)+" files crated")
    return created_files

def create_interval_dataframes(arquivo_processado,total_testes=20,nome_tabela:str="tmp",temporary_name_prefix_folder:str="/tmp"):
    csv_files=split_csv_files(arquivo_processado,temporary_name_prefix=str(temporary_name_prefix_folder+"/"+nome_tabela))
    test_counter=0
    groups=[]
    for i in csv_files:
        if test_counter % total_testes == 0:
            groups.append([])
        test_counter+=1
        file_=open(i,'r')
        groups[-1].append(process_dataframe(file_,criar_json=False))
        file_.close()
    df_groups=[]
    for group in groups:
        dfs = pd.DataFrame()
        for i in group:
            dfs=pd.concat([dfs,i])
        df_groups.append(dfs)
        del dfs
    # for i in df_groups:
    #     print(len(i))
    return df_groups
    
def file_to_graph(arquivo_processado,split=0,jpg=True,html=True,show=True,save=True,resize=None,temporary_name_prefix_folder:str="/tmp",path="./"):
    arquivo=open(arquivo_processado,"r")
    nome_tabela=os.path.basename(arquivo_processado)[:-4]
    if split==0:
        df=process_dataframe(arquivo)
        result=plot_graphs(df,jpg=jpg,html=html,show=show,save=False,resize=resize,nome_tabela=nome_tabela)
    else:
        dfs=create_interval_dataframes(arquivo,total_testes=split,nome_tabela=nome_tabela,temporary_name_prefix_folder=temporary_name_prefix_folder)
        result=[[],[]]
        for df in dfs:
            tmp=plot_graphs(df,jpg=jpg,html=html,show=show,save=False,resize=resize,nome_tabela=nome_tabela)
            result[0].append(tmp[0])
            result[1].append(tmp[1])

    if save==True:
        if jpg == True and html == True:
            save_jpg(result[0],nome_tabela,path=path)
            save_html(result[1],nome_tabela,path=path)
        elif html == True and jpg==False:
            save_html(result,nome_tabela,path=path)
        elif jpg == True and html==False:
            save_jpg(result,nome_tabela,path=path)
    return result

def plot_graphs(df,jpg=True,html=True,show=True,save=True,resize=None,nome_tabela=""):
    #alt.renderers.enable('mimetype')
    alt.renderers.enable('altair_viewer')
    # alt.renderers.enable('altair_saver', ['vega-lite','svg'])
    #alt.data_transformers.enable('data_server')
    # alt.data_transformers.register('custom', t)
    # alt.data_transformers.enable('custom')
    alt.renderers.enable('altair_viewer', embed_options={'renderer': 'svg'})
    alt.data_transformers.enable('json')
    alt.data_transformers.enable('default', max_rows=None)
    
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
        #rede=df.plot(x="@timestamp",figsize=(40,3),title="uso de rede container "+nome_tabela,y=["net_recive","net_sent"])
        
        if show==True:
            plt.show(block=True)
        if save==True:
            save_jpg([cpu,ram,disco],nome_tabela)
            # cpu.figure.savefig("uso de cpu container "+nome_tabela+".png")
            # ram.figure.savefig("uso de ram container "+nome_tabela+".png")
            # disco.figure.savefig("uso de disco container "+nome_tabela+".png")
            #rede.figure.savefig("uso de rede container "+nome_tabela+".png")
    
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
            save_html(alt_resultado,nome_tabela)
            #saver(alt_resultado,"dados do container "+nome_tabela+".html")

    if jpg == True and html ==False:
        return [cpu,ram,disco]
    elif jpg == False and html ==True:
        return alt_resultado
    else:
        return [cpu,ram,disco],alt_resultado

if __name__ == "__main__":
    path="/media/mzramna/Novo volume/"
    filtrar=False
    jpg=True
    html=True
    save=True
    show=False
    split=20
    arquivos=os.listdir(path)
    for arquivo in arquivos:
        #print(arquivo)
        if (arquivo.endswith(".csv") and not arquivo.endswith("_processado.csv") ) and filtrar==True:
            filtrar_csv_util(os.path.join(path, arquivo),os.path.join(path, arquivo[:-4]+"_processado.csv"))
    arquivos=os.listdir(".")
    resize = alt.selection_interval(bind='scales')
    resultados=[]
    for arquivo in arquivos:
        if arquivo.endswith("_limpo.csv"):
            resultados.append(file_to_graph(os.path.join(path,arquivo),split=split,jpg=jpg,html=html,save=save,show=show,resize=resize,path=path))
    if split >0 and html == True:
        if jpg == True:
            tmp=[]
            for resultado in resultados:
                tmp.append(resultado[1])
            resultados =tmp
        tmp=[]
        for i in range(len(resultados[0])):
            tmp.append([resultados[0][i],resultados[1][i],resultados[2][i],resultados[3][i]])
        for i in range(len(tmp)):
            final=alt.hconcat(*tmp[i])
            final.save(str(path+"dados do container concatenados_"+str(i)+".html"),embed_options={'renderer':'svg'})
            try:
                saver(final,path+"dados do container concatenados_"+i+".svg")
            except:
                pass
    elif jpg==False and html == True:
        final=alt.hconcat(*resultados)
        final.save(path+"dados do container concatenados.html",embed_options={'renderer':'svg'})
        saver(final,path+"dados do container concatenados.svg")
    else:
        pass
#colocar arquivos que serao acessados,filtrar apenas os dados usaveis,atualizar arquivos pra serem menores,fazer implementação que ja recebe do elasticsearch,limpa e salva os dados ordenados
