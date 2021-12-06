from geradorDeSql import GeradorDeSql
from pprint import pprint
from random import randint, random,uniform,choice

#logstash_data={"host":"192.168.0.116","port":5000,"username":"elastic","password":"changeme"}
#logstash_data={"host":"192.168.0.116","port":5000}
logstash_data={}
gerador=GeradorDeSql(sqlite_db="scripts/initial_db.db",sql_file_pattern="scripts/sqlitePattern.sql", log_file="scripts/geradorSQL.log",level=10,logging_pattern='%(asctime)s - %(name)s - %(levelname)s - %(message)s',logstash_data=logstash_data)
#pprint.pprint(gerador.process_data_generated("1,'empregado',1,'[{'bdAssociado': 'pessoas', 'fkAssociada': 'pessoas_id', 'id associado': '1'},{'bdAssociado': 'lojas', 'fkAssociada': 'loja_id', 'id associado': '1'}]','{salario:1200,contratado:'30/12/20'}'"))
# gerador.insert_data_sqlite({"tipoOperacao":1,"nomeBD":'empregado',"idNoBD":1,"adicionais":"[{'bdAssociado': 'pessoas', 'fkAssociada': 'pessoas_id', 'id associado': '1'},{'bdAssociado': 'lojas', 'fkAssociada': 'loja_id', 'id associado': '1'}]","dados":"{salario:1200,contratado:'30/12/20'}"})
# pprint.pprint(gerador.read_operacoes())
# pprint.pprint(gerador.read_contadores())
# print(gerador.buscar_ultimo_id_cadastrado("empregado"))
# tmp=[]
# for i in range(0,10):
#     gerador.gerar_dado_insercao("city",pattern=dict({
#         "city_id":["id"],
#         "city":["cidade"],
#         "country_id":["associacao","country"],
#         "last_update":["timestamp","agora"]
#     }),select_country="en_US")
# pprint(gerador.gerador_filtro(pattern={
#         "actor_id":["id"],
#         "first_name":["primeiroNome"],
#         "last_name":["sobrenome"],
#         "last_update":["timestamp","agora"]
#     },))


#teste de geração de pesquisa filtrada
# tmp=[]
# for i in range(0,40):
#     tmp.append(gerador.create_select("actor",pattern={
#         "actor_id":["id"],
#         "first_name":["primeiroNome"],
#         "last_name":["sobrenome"],
#         "last_update":["timestamp","agora"]
#     },select_country="en_US"))
# #pprint(tmp)
# tmp2={}
# for i in tmp:
#     if len(i["adicionais"]) not in tmp2:
#         tmp2[len(i["adicionais"])]=0
#     tmp2[len(i["adicionais"])]+=1

# pprint(tmp2)
#teste de geração de pesquisa nao filtrada
# tmp=[]
# for i in range(0,400):
#     tmp.append(gerador.create_select("actor",pattern={
#         "actor_id":["id"],
#         "first_name":["primeiroNome"],
#         "last_name":["sobrenome"],
#         "last_update":["timestamp","agora"]
#     },select_country="en_US",filtro="*"))
# #pprint(tmp)

# tmp2={}
# for i in tmp:
#     if len(i["dados"]) not in tmp2:
#         tmp2[len(i["dados"])]=0
#     tmp2[len(i["dados"])]+=1

# pprint(tmp2)

#teste de geração de delecao
# tmp=[]
# for i in range(0,100):
#     tmp.append(gerador.create_update("actor",pattern={
#         "actor_id":["id"],
#         "first_name":["primeiroNome"],
#         "last_name":["sobrenome"],
#         "last_update":["timestamp","agora"]
#     },select_country="en_US"))
# pprint(tmp)

# tmp2={}
# for i in tmp:
#     if len(i["dados"]) not in tmp2:
#         tmp2[len(i["dados"])]=0
#     tmp2[len(i["dados"])]+=1

# pprint(tmp2)

# tmp=[]
# for i in range(0,100):
#     tmp.append(gerador.create_delete("actor",pattern={
#         "actor_id":["id"],
#         "first_name":["primeiroNome"],
#         "last_name":["sobrenome"],
#         "last_update":["timestamp","agora"]
#     },select_country="en_US"))
# pprint(tmp)

# tmp2={}
# for i in tmp:
#     if len(i["dados"]) not in tmp2:
#         tmp2[len(i["dados"])]=0
#     tmp2[len(i["dados"])]+=1

# pprint(tmp2)

# print(gerador.read_operacoes(filtro={"idNoBD":1,"nomeBD":"actor"}))

#gerador.gerar_todos_dados_por_json(select_country="pt_br",quantidade_ciclo=1,total_ciclos=100,quantidade_final=5000)
#gerador.gerar_dados_validos_por_json(table="actor",tipo=1,select_country="pt_br",quantidade=10)#create
#gerador.gerar_dados_validos_por_json(table="actor",tipo=2,select_country="pt_br",quantidade=10)#leitura completa
gerador.gerar_dados_validos_por_json(table="actor",tipo=3,select_country="pt_br",quantidade=10)#busca
gerador.gerar_dados_validos_por_json(table="actor",tipo=4,select_country="pt_br",quantidade=10,dado_existente=True)#busca filtrada
#gerador.gerar_dados_validos_por_json(table="actor",tipo=5,select_country="pt_br",quantidade=10,dado_existente=True)#edição
# gerador.gerar_dados_validos_por_json(table="actor",tipo=6,select_country="pt_br",quantidade=10,dado_existente=True)#deleção

#pprint(gerador.read_contadores())

dados_retornados=gerador.processamento_sqlite.read_operacoes(filtro={"nomeBD":"actor"})
dados_separados=[[] for x in range(0,7)]
for i in dados_retornados:
    dados_separados[i["tipoOperacao"]].append(i)
for i in range(1,7):
    tmp=choice(dados_separados[i])
    pprint(tmp)
    print(gerador.generate_SQL_command_from_data(data=tmp))
