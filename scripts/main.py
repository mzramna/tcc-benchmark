from geradorDeSql import GeradorDeSql
from pprint import pprint
gerador=GeradorDeSql(sqlite_db="scripts/initial_db.db",sql_file_pattern="scripts/sqlitePattern.sql", log_file="scripts/geradorSQL.log",level=10,logging_pattern='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
gerador.logging.debug("begin")
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



#print(gerador.read_operacoes(filtro={"idNoBD":1,"nomeBD":"actor"}))
gerador.gerar_todos_dados_por_json(json_file="./scripts/padroes.json",select_country="en_US",quantidade=10)
gerador.gerar_dados_por_json(json_file="./scripts/padroes.json",table="actor",tipo=3,select_country="en_US",quantidade=10)
gerador.gerar_dados_por_json(json_file="./scripts/padroes.json",table="actor",tipo=3,select_country="en_US",quantidade=10,dado_existente=True)
# gerador.gerar_todos_dados_por_json(json_file="./scripts/padroes.json",select_country="en_US",quantidade=3,)

#pprint(gerador.read_contadores())
gerador.logging.debug("end")

