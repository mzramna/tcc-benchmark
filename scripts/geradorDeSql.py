from array import array
from os import name,DirEntry
from loggingSystem import loggingSystem
from processamentosqlite import ProcessamentoSqlite
from faker import Faker
from random import randint, random,uniform,choice,sample
from sqlite3 import Error as sqliteError
from sqlite3 import OperationalError as sqliteOperationalError
import sys,re,sqlite3,json,logging,csv
from typing import Union

class GeradorDeSql:
#tratamento de erro
    class ValorInvalido(Exception):
        """classe de exceção customizada base,feita de forma a dar mensagem de erro base para a classe,essa mensagem de erro é genérica, e é usado para avisar se alguma variavel foi preenchida de forma que o algoritimo não aceita,essa mensagem de erro é altamente customizável
        """        
        def __init__(self, valor_inserido="",mensagem_principal_replace=False,mensage_adicional="",campo="",valor_possivel="") :
            """
                    construtor 
            Args:
                valor_inserido (str, optional):valor que foi passado que gerou o erro. Defaults to "".
                mensagem_principal_replace (bool, optional): se verdadeiro substitui todos os dados da mensagem de erro pelo conteudo do parametro mensagem adicional. Defaults to False.
                mensage_adicional (str, optional): mensagem adicional a ser inserida no final da mensagem de erro. Defaults to "".
                campo (str, optional): nome do campo que foi preenchido de forma errada. Defaults to "".
                valor_possivel ({str , array}, optional): valores possiveis de serem inseridos na variavel,podendo ser tipo ou valor mesmo no caso de ser algum valor dinamico. Defaults to "".
            """            
            self.valor_inserido=str(valor_inserido)
            self.valor_possivel=valor_possivel
            self.mensage_adicional=mensage_adicional
            self.mensagem_principal_replace=mensagem_principal_replace
            self.campo=campo
            self.construir_mensagem()
            super().__init__(self.message)

        def listagem_valores_possiveis(self,valores_possiveis="",campo=""):
            """ formata a entrada de valores possiveis para uma forma mais legivel os valores possiveis caso seja um array e se for um string ele será inserido direto no campo de valor inserido,também adiciona o nome do campo que foi inserido e faz a formulação do nome do campo se ele existir

            Args:
                valores_possiveis ({str , array}, optional): valores possiveis de serem inseridos na variavel,podendo ser tipo ou valor mesmo no caso de ser algum valor dinamico. Defaults to ""
                campo (str, optional): nome do campo que foi preenchido de forma errada. Defaults to "".

            Returns:
                string: mensagem parcialmente formatada da mensagem de erro
            """            
            if valores_possiveis !="":
                if  type("")==type(valores_possiveis):
                    self.message+=" o valor possivel "
                    if campo!="":
                        self.message+="no campo "+str(campo)+" "
                    self.message+="é "
                elif  type("")==type(valores_possiveis):
                    self.message+=" os valores possiveis "
                    if campo!="":
                        self.message+="no campo "+str(campo)+" "
                    self.message+="são "+str(valores_possiveis)
                return self.valores_possiveis(valores_possiveis)

        def valores_possiveis(self,valores_possiveis=""):
            """formata a entrada de valores possiveis para uma forma mais legivel os valores possiveis caso seja um array e se for um string ele será inserido direto no campo de valor inserido

            Args:
                valores_possiveis ({str , array}, optional): valores possiveis de serem inseridos na variavel,podendo ser tipo ou valor mesmo no caso de ser algum valor dinamico. Defaults to ""

            Returns:
                string: string formatado de forma mais legivel o conteudo da variavel valores possiveis
            """            
            retorno=""
            if type(valores_possiveis)==type([]) or type(valores_possiveis)==type({}):
                for valor in valores_possiveis:
                    if type(valor)==type(""):
                        retorno+=valor
                    else:
                        retorno+=str(valor) 
                    if valor == valores_possiveis[-2]:
                        retorno+=" ou "
                    elif valor not in valores_possiveis[-2:]:
                        retorno+=","
            elif type(valores_possiveis)==type(""):
                    retorno+=valores_possiveis
            else:
                retorno+=str(valores_possiveis)
            return retorno

        def tratamento_input(self,valor,adicional:str="") -> str:
            """processa o dado inserido para formular melhor a mensagem de erro

            Args:
                valor ([str,list]): lista de valores ou valor que serão formatados
                adicional (str, optional): valores adicionais para um campo. Defaults to

            Returns:
                str: texto formatado para usar na construção da resposta
            """
            retorno=""
            if adicional!="":
                if type(valor) == type(""):
                    retorno+=" no  "+adicional+" "
                elif type(valor) == type([]):
                    retorno+=" nos "+adicional+" "
                else:
                    retorno+=" no  "+adicional+" "
            if type(valor) == type(""):
                retorno+= valor
            elif type(valor) == type([]):
                retorno+= self.valores_possiveis(valores_possiveis=valor)
            else:
                retorno+= str(valor)
            return retorno

        def construir_mensagem(self,mensage_adicional=""):
            """ gera a mensagem de erro e formata com o uso das outras funções a classe
            e se substitui a mensagem de erro pela mensagem adicional caso a seja passada a variavel mensagem_principal_replace como verdadeira na construção da classe

            Args:
                mensage_adicional (str, optional): mensagem de erro adicional a ser inserido no final ou ssubstituir a mensagem completa. Defaults to "".
            """            
            if not self.mensagem_principal_replace:
                self.message="um valor inserido foi inserido de forma errada\no valor "
                self.message+=self.tratamento_input(self.valor_inserido)
                self.message+=" é invalido ou foi inserido de forma errada"
                self.message+=self.tratamento_input(self.campo,"campo")
                self.message+="\n"
                self.message+=str(self.listagem_valores_possiveis(valores_possiveis=self.valor_possivel))
                self.message+="\n"
            if mensage_adicional == "":
                self.message+=str(self.mensage_adicional)
            else:
                self.message+=mensage_adicional

        def __str__(self):
            return self.message
    
    class TamanhoArrayErrado(ValorInvalido):
        def __init__(self,valor_inserido,valor_possivel="",campo="") :
            super(GeradorDeSql.ValorInvalido, self).__init__()
            self.valor_inserido=str(valor_inserido)
            self.valor_possivel=valor_possivel
            self.campo=campo
            self.valor_inserido=valor_inserido
            self.mensagem_principal_replace=True
            self.construir_mensagem()

        def construir_mensagem(self):
            self.message="o tamanho para o array passado "
            self.message+=self.tratamento_input(self.campo,"campo")
            self.message+="é invalido\n"
            if self.valor_possivel != "":
                self.message+=" o tamanho esperado era de "
                self.message+=self.valores_possiveis(self.valor_inserido)
                self.message+=" programa não pode continuar"
            
            #super(GeradorDeSql.TamanhoArrayErrado, self).construir_mensagem(self.message)

        def __str__(self):
            return self.message

    class TipoDeDadoIncompativel(ValorInvalido):
        def __init__(self,valor_inserido,tipo_possivel="",campo="") :
            super(GeradorDeSql.ValorInvalido, self).__init__()
            self.valor_inserido=valor_inserido
            self.tipo_possivel=tipo_possivel
            self.mensagem_principal_replace=True
            self.campo=campo
            self.construir_mensagem()

        def construir_mensagem(self):
            self.message="o tipo da variavel passada "
            self.message+=self.tratamento_input(self.campo,"campo")
            self.message+="é invalido\n"
            if self.tipo_possivel != "":
                self.message+=" o tipo esperado era de "
                self.message+=self.valores_possiveis(self.tipo_possivel)
                self.message+=" programa não pode continuar"
                self.message+=" mas foi inserido"
                self.message+=str(self.valor_inserido)
            #self.construir_mensagem(self.message)

        def __str__(self):
            return self.message

#inicialização
    def __init__(self,sqlite_db:str="./initial_db.db",sql_file_pattern:str="./sqlitePattern.sql",json_file:str="./scripts/padroes.json", log_file="./geradorSQL.log",level:int=10,logging_pattern='%(name)s - %(levelname)s - %(message)s',logstash_data:dict={}):
        """
        classe para gerar dados de teste para bancos de dados
        json_file ([type]): arquivo do qual os dados de padrão serão carregados
        :param loggin_name: nome do log que foi definido para a classe,altere apenas em caso seja necessário criar multiplas insstancias da função
        :param log_file: nome do arquivo de log que foi definido para a classe,altere apenas em caso seja necessário criar multiplas insstancias da função
        """

        self.logging = loggingSystem(name="gerador sql",arquivo=log_file,level=level,format=logging_pattern,logstash_data=logstash_data)
        #self.create_temporary_DB(local=sqlite_db,pattern=sql_file_pattern)
        self.processamento_sqlite=InteracaoSqlite(sqlite_db=sqlite_db,sql_file_pattern=sql_file_pattern,log_file=log_file,logging_pattern=logging_pattern,level=level,logstash_data=logstash_data)
        self.conn = sqlite3.connect(sqlite_db)
        
        file=open(json_file)
        self.json_loaded=json.loads(file.read())
        self.logging.debug(self.json_loaded)
        logging.getLogger('faker').setLevel(logging.ERROR)
        #self.logging = self.logging.logger.getLogger("gerador sql")

    def dict_all_string(self,entrada:dict)-> dict:
        """converte todos valores de um dict para string

        Args:
            entrada (dict): dict que deve ser processado

        Returns:
            dict: dict convertido
        """
        
        retorno={}
        for i in entrada.keys():
            if type(i)==type(""):
                retorno[i]=entrada[i]
            else:
                retorno[i]=str(entrada[i])
        return retorno

    def process_id(self,data:dict,pattern:dict,id:int) -> int:
        """define o id que sera usado baseado no pattern e no dado gerado

        Args:
            data (dict): dict com dado gerado onde o id sera pesquisado
            pattern (dict): padrão correspondente ao dado inserido
            id (int): id inserido por parametro,é analizado para definir se é pra ser inserido diretamente ele ou se deve ser pesquisado

        Returns:
            int:id processado
        """        
        if data == None:
            return -1
        if id == -1:
            for campo,valor in pattern.items():
                if "id" in valor:
                    if campo in data:
                        return data[campo]
                    else:
                        return -1
        return id

    def create_data(self,table:str,pattern:dict,select_country:str="random",id:int=-1,not_define_id=False,lista_restritiva:list=[]) -> dict:
        """gera os dados baseados nos parametros e padrões passados 

        Args:
            table (str): nome da tabela que será gerada
            pattern (dict): padrão usado para a geração de dado
            select_country (str, optional): padrão de localização para definir o idioma no qual os dados serão gerados,se random sera definido randomicamente. Defaults to "random".
            id (int, optional): id definido para o dado que será gerado,se for -1 ele será escolhido randomicamente entre os previamente gerados caso o parametro not_defined_id seja falso. Defaults to -1.
            not_define_id (bool, optional): define se o id ira existir na saida do dado,caso ele seja verdadeiro o id não será nem gerado nem passado para a saida de dado. Defaults to False.
            lista_restritiva (list, optional): lista que define os dados que serão gerados dentro do padrão inserido. Defaults to [].

        Raises:
            self.TipoDeDadoIncompativel: caso o dado não tenha o tipo necessário esse erro será chamado
            self.TamanhoArrayErrado: caso o array dentro do padrão não possua o tamanho necessario para a geração deste dado o erro sera chamado
            self.TipoDeDadoIncompativel: caso o dado não tenha o tipo necessário esse erro será chamado
            self.TipoDeDadoIncompativel: caso o dado não tenha o tipo necessário esse erro será chamado
            self.TipoDeDadoIncompativel: caso o dado não tenha o tipo necessário esse erro será chamado
            self.TamanhoArrayErrado: caso o array dentro do padrão não possua o tamanho necessario para a geração deste dado o erro sera chamado
            self.TipoDeDadoIncompativel: caso o dado não tenha o tipo necessário esse erro será chamado
            self.ValorInvalido: [description]
            self.ValorInvalido: [description]
            self.ValorInvalido: [description]

        Returns:
            dict: dado gerado seguindo o padrão inserido
        """
        self.logging.info("create_data",extra=locals())
        self.logging.debug("rastreio create_data",extra={"rastreio":loggingSystem.full_inspect_caller()})
        try:
            if select_country=="random":
                fake = Faker()
                random_locale=fake.locale()
                self.logging.info("selecionada localização aleatoria",extra={"locale":random_locale})
                fake = Faker(random_locale)#define o faker para seguir o padrão de um pais expecifico selecionado aleatoriamente dentre os disponiveis
            else:
                fake = Faker(select_country)#se for definido então o codigo usado será o do pais inserido
                self.logging.info("selecionada localização definida",extra={"locale":select_country})
            dados_gerados={}
            if id == -1:
                id=self.processamento_sqlite.buscar_ultimo_id_cadastrado(table)+1
            dados_geraveis=list(pattern.keys())
            if lista_restritiva !=[]:
                for i in list(pattern.keys()):
                    if i not in lista_restritiva:
                        dados_geraveis.remove(i)
                        
            for dado in dados_geraveis:
                if type(pattern[dado][0]) != type(""):
                        raise self.TipoDeDadoIncompativel(valor_inserido=pattern[dado][0],tipo_possivel="string",campo="nome do campo")
                if pattern[dado][0] == "nomeCompleto":
                    '''supoe-se que qualquer pessoa pode ter nascido em qq lugar e morar em qualquer outro lugar,nomes são dados pelo gerador de qualquer idioma,por isso nao foi definido um pais para a geracao'''
                    dados_gerados[dado]=fake.name()
                elif pattern[dado][0] == "primeiroNome":
                    dados_gerados[dado]=fake.first_name()
                elif pattern[dado][0] == "sobrenome":
                    dados_gerados[dado]=fake.last_name()
                elif pattern[dado][0] == "timestamp":
                    '''precisa obrigatoriamente de 1 parametro dizendo se vai ser tudo randomico ou se vai ter um intervalo,se tiver um intervalo devem ser passados mais 2 parametros,um inicial e um final , se o final for o valor "agora" então o valor final sera o timestamp de agora do sistema operacional

                    para gerar com mais precisão usar o 2 parametro como: "-30y",sendo: - > significando anterior , 30 > quanto tempo , y > escala de tempo(anos) ou usando o padrão Date("dia") onde o dia deve ser passado como "1999-02-02"

                    o 3 parametro deve ser passado como o 2,mas não se limita apenas ao token de tempo anterior,sendo possivel um intervalo do futuro
                    '''
                    if len(pattern[dado])<2:
                        raise self.TamanhoArrayErrado(valor_possivel=[2,3],valor_inserido=len(pattern[dado]),campo="timestamp")
                    regex1=r'[\+,\-][0-9]*[d,m,y]'
                    regex2=r'[0-9]{4}[\/,\-][0-9]{2}[\/,\-][0-9]{2}'
                    if len(pattern[dado])>=2:
                        match1=re.match(regex1,pattern[dado][1])
                        match2=re.match(regex2,pattern[dado][1])
                        if type(pattern[dado][1] )!=type("") or ((not match1 and not match2 and (match1 != None or match2 != None)) and pattern[dado][1] != "agora"):
                            if type(pattern[dado][1] ) != type(""):
                                print("tipo")
                            if (not match1 and not match2 and type(match1) != None):
                                print("regex")
                                print(match1)
                                print(match2)
                            if pattern[dado][1]!="agora":
                                print("string especial")
                            raise self.TipoDeDadoIncompativel(pattern[dado][1],tipo_possivel="string com padrão -30y ou 1999-02-02 ou 1999/02/02",campo="campo 1 adicional em timestamp")
                    if len(pattern[dado])>=3:
                        match1=re.match(regex1,pattern[dado][2])
                        match2=re.match(regex2,pattern[dado][2])
                        if type(pattern[dado][2] )!=type("") or ((not match1 and not match2 and (match1 != None or match2 != None)) and pattern[dado][2] != "agora") :
                            raise self.TipoDeDadoIncompativel(pattern[dado][2],tipo_possivel="string com padrão -30y ou 1999-02-02 ou 1999/02/02",campo="campo 2 adicional em timestamp")
                    start_date=""
                    end_date=""
                    if pattern[dado][1] == "agora" :#se true é tudo randomico
                        end_date="today"
                    else:
                        end_date=pattern[dado][1]
                        if len(pattern[dado])>2:
                            start_date=end_date
                            if pattern[dado][2] == "agora":
                                end_date="today"
                    if start_date == "" :
                        dados_gerados[dado]=fake.date_between(end_date=end_date).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        dados_gerados[dado]=fake.date_between_dates(start_date=start_date,end_date=end_date).strftime('%Y-%m-%d %H:%M:%S')
                elif pattern[dado][0] == "pais":
                    dados_gerados[dado]=fake.current_country()
                elif pattern[dado][0] == "cidade":
                    dados_gerados[dado]=fake.city()
                elif pattern[dado][0] == "endereco":
                    dados_gerados[dado]=fake.street_address()
                elif pattern[dado][0] == "cep":
                    dados_gerados[dado]=fake.postcode()
                elif pattern[dado][0] == "telefone":
                    if fake.boolean():
                        dados_gerados[dado]=fake.phone_number()
                    else:
                        try:
                            dados_gerados[dado]=fake.cellphone_number()
                        except AttributeError as e :
                            dados_gerados[dado]=fake.phone_number()
                            self.logging.exception("tipo celular nao existe")
                elif pattern[dado][0] == "nomeCategoria":
                    dados_gerados[dado]=fake.word()
                elif pattern[dado][0] == "email":
                    dados_gerados[dado]=fake.email()
                elif pattern[dado][0] == "usuario":
                    dados_gerados[dado]=fake.profile(fields=["username"])["username"]
                elif pattern[dado][0] == "senha":
                    dados_gerados[dado]=fake.password(length=fake.random_int(min=8,max=32))
                elif pattern[dado][0] == "boleano":
                    dados_gerados[dado]=fake.boolean()
                elif pattern[dado][0] == "idioma":
                    dados_gerados[dado]=fake.locale()
                elif pattern[dado][0] == "titulo":
                    dados_gerados[dado]=fake.sentence(nb_words=fake.random_int(min=1,max=10))
                elif pattern[dado][0] == "textoLongo":
                    dados_gerados[dado]=fake.paragraphs(nb=fake.random_int(min=1,max=2))
                elif pattern[dado][0] == "nota":
                    dados_gerados[dado]=uniform(0.0,10.0)
                elif pattern[dado][0] == "ano":
                    dados_gerados[dado]=fake.date(pattern='%Y')
                elif pattern[dado][0] == "duracaoDias":
                    dados_gerados[dado]=fake.random_int(min=1,max=10)
                elif pattern[dado][0] =="datetime":
                    dados_gerados[dado]=fake.date_time().strftime('%Y-%m-%d')
                elif pattern[dado][0] == "duracaoHoras":
                    dados_gerados[dado]=uniform(0.0,4.0)
                elif pattern[dado][0] == "naLista":
                    if not all(isinstance(n, str) for n in list(pattern[dado][0])):
                        raise self.TipoDeDadoIncompativel(pattern[dado][1],tipo_possivel="string",campo="variaveis adicionais da variavel naLista")
                    dados_gerados[dado]=fake.word(ext_word_list=pattern[dado][1:] )
                elif pattern[dado][0] == "valorPago":
                    dados_gerados[dado]=uniform(0.0,50.0)
                elif pattern[dado][0] == "associacao":
                    '''
                    parametros obrigatórios é nome da tabela e se random ou se definido é adicional,caso não seja definido obrigatoriamente é random
                    '''
                    if len(pattern[dado])<2:
                        raise self.TamanhoArrayErrado(valor_possivel=[2,3],valor_inserido=len(pattern[dado]),campo="associacao")
                    if type(pattern[dado][1]) != type(""):
                        raise self.TipoDeDadoIncompativel(valor_inserido=pattern[dado][1],tipo_possivel=["string","array"],campo="associacao")
                    if len(pattern[dado])>2:
                        if pattern[dado][2]!="random":
                            dados_gerados[dado]=pattern[dado][2]
                        else:
                            total_cadastrado=self.processamento_sqlite.buscar_ultimo_id_cadastrado(pattern[dado][1])
                            if total_cadastrado>1:
                                dados_gerados[dado]=fake.random_int(min=1,max=self.processamento_sqlite.buscar_ultimo_id_cadastrado(pattern[dado][1]))
                            else:
                                raise self.ValorInvalido(valor_inserido=pattern[dado][1],campo="associacao",valor_possivel="maior que 0",mensage_adicional="não existe dado cadastrado nessa tabela")
                    else:
                        total_cadastrado=self.processamento_sqlite.buscar_ultimo_id_cadastrado(pattern[dado][1])
                        if total_cadastrado>0:
                            dados_gerados[dado]=fake.random_int(min=1,max=self.processamento_sqlite.buscar_ultimo_id_cadastrado(pattern[dado][1]))
                        else:
                            quantidade_tabelas_sqlite=self.processamento_sqlite.read_data_sqlite(table="contadores")
                            if len(quantidade_tabelas_sqlite)==len(self.json_loaded.keys()):
                                raise self.ValorInvalido(valor_inserido=(pattern[dado][1],0),campo="associacao",valor_possivel="maior que 0",mensage_adicional="não existe dado cadastrado nessa tabela") # arrumar forma de criar a tabela necessária
                            else:
                                return {}
                            
                            #dados_gerados[dado]=fake.random_int(min=1,max=self.processamento_sqlite.buscar_ultimo_id_cadastrado(pattern[dado][1]))
                elif pattern[dado][0] == "id" :
                    if not not_define_id:
                        dados_gerados[dado]=id
                    elif len(dados_geraveis) <2 and  lista_restritiva[0] == dado :
                        dados_gerados[dado]=id
            if dados_gerados=={}:
                raise self.ValorInvalido(valor_inserido=dados_gerados,mensage_adicional="o valor não pode ser vazio",campo="dados_gerados")
            self.logging.debug("dado gerado por create_data",extra=dados_gerados)
            return dados_gerados
        except self.TamanhoArrayErrado as e :
            self.logging.exception(e)
        except self.ValorInvalido as e:
            self.logging.exception(e)
            if e.campo== "dados_gerados":
                return self.create_data(table=table,pattern=pattern,select_country=select_country,id=id) 
            elif e.campo=="associacao":
                chamadas=loggingSystem.full_inspect_caller()
                if chamadas.count(chamadas[0])>5:
                    return None
                self.gerar_dado_insercao(table=pattern[dado][1],pattern=self.json_loaded[pattern[dado][1]],select_country=select_country)
                return self.create_data(table=table,pattern=pattern,select_country=select_country,id=id) 
        except self.TipoDeDadoIncompativel as e:
            self.logging.exception(e)
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])

    def gerador_filtro(self,pattern:dict,pesquisa_pre=[],retorno_pre=[],max:int=-1,completo=False) -> array:
        """ 
            gera um conjunto de elementos para serem usados como filtro,eles são gerados a partir do pattern inserido,ignorando os elementos da lista desejada
        Args:
            pattern (dict): padrão do qual serão retiradas as keys para gerar a lista de filtro
            pesquisa_pre (list, optional): lista de keys pre definidas para serem usadas no campo equivalente a pesquisa. Defaults to [].
            retorno_pre (list, optional): lista de keys pre definidas para serem usadas no campo equivalente ao retorno. Defaults to [].
            max (int, optional): valor maximo de retorno ,se for definido ele define quantos elementos a menos que o tamanho total de elementos o retorno deve ser. Defaults to -1.
            completo (bool,optional): retorna apenas valores para o array de pesquisa.Defaults to False
        Returns:
            array: lista de keys gerada randomicamente para serem usadas como filtro
        """        
        self.logging.info("gerador_filtro",extra=locals())
        retorno=[]
        if pesquisa_pre =="*":
            pesquisa_pre=[]
        if retorno_pre =="*":
            retorno_pre=[]
        try:
            if len(list(pattern.keys()))-len(pesquisa_pre)-len(retorno_pre)<= 0 :
                if list(pattern.keys())==pesquisa_pre:
                    raise self.ValorInvalido(valor_inserido=pesquisa_pre,mensage_adicional="pesquisa_pre não pode ser igual a pattern",campo="pesquisa_pre")
                elif list(pattern.keys())==retorno_pre:
                    raise self.ValorInvalido(valor_inserido=retorno_pre,mensage_adicional="retorno_pre não pode ser igual a pattern",campo="retorno_pre")
                elif list(pattern.keys())>pesquisa_pre:
                    raise self.ValorInvalido(valor_inserido=pesquisa_pre,mensage_adicional="pesquisa_pre não pode ser maior que o total de elementos de pattern",campo="pesquisa_pre")
                elif list(pattern.keys())>retorno_pre:
                    raise self.ValorInvalido(valor_inserido=retorno_pre,mensage_adicional="retorno_pre não pode ser maior que o total de elementos de pattern",campo="retorno_pre")
            elif len(list(pattern.keys()))-len(pesquisa_pre)<1:
                raise self.ValorInvalido(valor_inserido=pesquisa_pre,mensage_adicional="pesquisa_pre não pode ser tão grande",campo="pesquisa_pre")
            elif len(list(pattern.keys()))-len(retorno_pre)<1:
                raise self.ValorInvalido(valor_inserido=retorno_pre,mensage_adicional="retorno_pre não pode ser tão grande",campo="retorno_pre")
            array_para_trabalho=list(pattern.keys())
            retorno = self.dividir_array(array=array_para_trabalho,max=max,pesquisa_pre=pesquisa_pre,retorno_pre=retorno_pre)
            
            if retorno == None :
                raise self.TamanhoArrayErrado(valor_inserido=retorno,valor_possivel="maior que 1",campo="retorno")
            
            if not completo:
                retorno = retorno[0]
        except self.ValorInvalido as e:
            self.logging.exception(e)
        except self.TamanhoArrayErrado as e:
            self.logging.exception(e)
            retorno = self.gerador_filtro(pattern=pattern,pesquisa_pre=pesquisa_pre,retorno_pre=retorno_pre,max=max,completo=completo)
        finally:
            self.logging.debug("dado gerado por gerador_filtro",extra={"filtro":retorno})
            return retorno

    def dividir_array(self,array:list,max:int=0,pesquisa_pre=[],retorno_pre=[]) -> array :
        """divide um array em 3 outros arrays de tamanhos aleatorios

        Args:
            array : array q sera dividido
            max (int, optional): quando definido é o tamanho do primeiro subarray,se for maior qe o tamanho do array dado menos 1 não vai funcionar,se for menor que 1 ele será ignorado. Defaults to 0.
            pesquisa_pre (list, optional): lista de keys pre definidas para serem usadas no campo equivalente a pesquisa. Defaults to [].
            retorno_pre (list, optional): lista de keys pre definidas para serem usadas no campo equivalente ao retorno. Defaults to [].

        Returns:
            array: matriz composta de 3 subarrays de tamanho minimo 1 - 1 - 0
        """        
        def tamanhos_arrays(max:int,max_first:int=0,pesquisa_pre=[],retorno_pre=[]):
            """gera tamanhos randomicos para dividir um array para sub arrays,seguindo a regra de minimo 1-1-0

            Args:
                max (int): total de elementos do array que será dividido no final
                max_first (int, optional): tamanho máximo que será definido para o primeiro array,ele tem que ser obrigatoriamente menor que o tamanho do array original menos 1. Defaults to 0.

            Returns:
                array: tres elementos inteiros ,sendo o primeiro um valor randomico entre 1 e max-1,o segundo sendo entre 1 e restante e o 3 o restante que sobrar,podendo ser vazio
            """            
            if max<2 or max_first>(max-1):
                return None
            #fazer retorno e pesquisa pre definirem automaticamente nos locais certos,verificar se eles existem no pattern e se são possiveis
            
            retorno=[]
            max_tmp=max
            if pesquisa_pre ==[]:
                if max_tmp >0:
                    retorno.append(randint(1,max_tmp-1))
                else:
                    retorno.append(randint(1,max_first))
            else:
                retorno.append(len(pesquisa_pre))
            # while max_tmp-retorno[-1] <1:
            #     retorno[-1]=randint(1,max_tmp-1)
            max_tmp=max_tmp-retorno[-1]
            if retorno_pre==[]:
                retorno.append(randint(1,max_tmp))
            else:
                retorno.append(len(retorno_pre))
            # while max_tmp-retorno[-1] <1:
            #     retorno[-1]=randint(1,max_tmp)
            max_tmp=max_tmp-retorno[-1]
            retorno.append( max_tmp )
            if sum(retorno)!=max:
                return tamanhos_arrays(max=max,max_first=max_first,pesquisa_pre=pesquisa_pre,retorno_pre=retorno_pre)
            else:
                return retorno
            
        try:
            if len(set(retorno_pre).difference(array))>0 and retorno_pre !=[]:
                raise self.ValorInvalido(valor_inserido=retorno_pre,mensage_adicional="retorno_pre precisa estar contido no array",campo="retorno_pre")
            elif len(set(pesquisa_pre).difference(array))>0 and pesquisa_pre !=[] :
                raise self.ValorInvalido(valor_inserido=pesquisa_pre,mensage_adicional="pesquisa_pre precisa estar contido no array",campo="pesquisa_pre")
            tamanhos=tamanhos_arrays(len(array),max_first=max,pesquisa_pre=pesquisa_pre,retorno_pre=retorno_pre)
            if tamanhos==None:
                return None
            array_tmp=array
            retorno=[]
            
            for i in range(3):
                if pesquisa_pre !=[] and i == 0:
                    retorno.append(pesquisa_pre)
                elif retorno_pre !=[] and i == 1:
                    retorno.append(retorno_pre)
                else:
                    retorno.append(sample(array_tmp,tamanhos[i]))
                for y in retorno[-1]:
                    array_tmp.remove(y)

            return retorno
        except self.ValorInvalido as e:
            self.logging.exception(e)
        except self.TamanhoArrayErrado as e:
            self.logging.exception(e)

#relacionado com o processamento/geração de dados
    def create_insert(self,table:str,pattern:dict,select_country:str="random",id:int=-1,values:dict={},not_define_id=False) -> dict:
        
        """cria um novo dado para ser inserido no sqlite ou ser usado em outras partes do codigo

        Args:
            table (str): nome da tabela do sql que o dado será inserido
            pattern (dict): padrão que será usado pelo gerador seguindo o padrão descrtito no json,esses padrões serão descritos a parte
            select_country (str, optional): pais do qual o padrão do faker será usado. Defaults to "random".
            id (int, optional): id do dado gerado no banco de dados,se preenchido ele será o definido,caso contrário ele será o próximo possivel no bd de acordo com os registros do sqlite. Defaults to -1.
            values (dict,optional): valores de substituição para os dados gerados,se não for default,nenhum dado randomico será gerado,serão utilizados os dados inseridos nessa variavel . Defaults to {}.
            not_define_id (bool, optional): define se o id ira existir na saida do dado,caso ele seja verdadeiro o id não será nem gerado nem passado para a saida de dado. Defaults to False.

        Raises:
            self.TamanhoArrayErrado: array usado no pattern não possui o tamanho correto de acordo com o 
            self.TipoDeDadoIncompativel: dado inserido atravez do pattern não é compativel com o necessário para o funcionamento
        Returns:
            [dict]: dados gerados usando faker para corresponder ao padrão necessário
        """        
        '''
            pattern deve ser dado da seguinte forma:
            {
                "nome da coluna no bd":["tipo de dado gerado","dado adicional necessario"], #sempre desve ser passado como um array cada indice do dict,ja que alguns tipos de dados precisam mais do que apenas um dado para funcionar
                ...
            }


            o padrão de saida deve ser semelhante ao padrão do sqlite:
            {
            "tipoOperacao":1 #sempre será 1 já que apenas são gerados dados para inserção por padrão,caso seja necessário algo diferente,deve ser modificado em outra função
            "nomeBD": # nome do bd q será realizado a operação
            "adicionais": {} ou []# vazio por padrão,caso seja necessário deversá ser tratado externamente em outra função
            "dados"{
                "nome da coluna":"dado", #nome da coluna deve ser passado no input e dado é gerado pela função
                ...
            }
            }
        '''
        self.logging.info("create_insert",extra=locals())
        self.logging.debug("rastreio create_insert",extra={"rastreio":loggingSystem.full_inspect_caller()})
        if values=={}:
            values=self.create_data(table=table,pattern=pattern,select_country=select_country,id=id,not_define_id=not_define_id)
        dados_gerados={"nomeBD":table,"tipoOperacao":1,"dados":values,"adicionais":{}}
        _id=self.process_id(data=dados_gerados["dados"],pattern=pattern,id=id)
        if not not_define_id and _id !=-1:
            dados_gerados["idNoBD"]=_id
        
        self.logging.debug("dado gerado por create_insert",extra=self.dict_all_string(dados_gerados))
        return dados_gerados
        
    def create_select(self,table:str,pattern:dict,select_country:str="random",id:int=-1,filtro_pesquisa:list=[],values_pesquisa:dict={},filtro_retorno:list=[],not_define_id:bool=False) -> dict:
        
        """função gera um dictionary variante do de create_data que contem os dados equivalentes ao comando de pesquisa para o sqlite

        Args:
            table (str): nome da tabela do sql que o dado será inserido
            pattern (dict): padrão que será usado pelo gerador seguindo o padrão descrtito no json,esses padrões serão descritos a parte
            select_country (str, optional): pais do qual o padrão do faker será usado. Defaults to "random".
            id (int, optional): id do dado gerado no banco de dados,se preenchido ele será o definido,caso contrário ele será o próximo possivel no bd de acordo com os registros do sqlite. Defaults to -1.
            filtro_pesquisa (list or str, optional): equivalente a coluna adicional do dado pesquisado,se for igual a "*" irá retornar todos,se for default o filtro será gerado randomicamente. Defaults to [].
            values_pesquisa (dict,optional): valores de substituição para os dados gerados,se não for default,nenhum dado randomico será gerado,serão utilizados os dados inseridos nessa variavel . Defaults to {}.
            filtro_retorno (list or str, optional): equivalente a coluna adicional do dado retorno,se for igual a "*" irá retornar todos,se for default o filtro será gerado randomicamente. Defaults to [].
            values_retorno (dict,optional): valores de substituição para os dados gerados,se não for default,nenhum dado randomico será gerado,serão utilizados os dados inseridos nessa variavel . Defaults to {}.
            not_define_id (bool, optional): define se o id ira existir na saida do dado,caso ele seja verdadeiro o id não será nem gerado nem passado para a saida de dado. Defaults to False.
        Returns:
            dict: dados gerados usando faker para corresponder ao padrão necessário de uma pesquisa no bd
        """
        self.logging.info("create_select",extra=locals())
        self.logging.debug("rastreio create_select",extra={"rastreio":loggingSystem.full_inspect_caller()})
        try:
            dados_gerados={"nomeBD":table}
            pattern=pattern.copy()

            if values_pesquisa !={}:
                filtro_pesquisa=list(values_pesquisa.keys())

            if filtro_pesquisa == "*":
                dados_gerados["tipoOperacao"]=3
            else:
                dados_gerados["tipoOperacao"]=4
            arrays=self.gerador_filtro(pattern,pesquisa_pre=filtro_pesquisa,retorno_pre=filtro_retorno,completo=True)
            filtro_pesquisa=arrays[0]
            filtro_retorno=arrays[1]
            
            dados_gerados["adicionais"]=filtro_retorno#arrays[1]

            if values_pesquisa == {}:
                for value_pattern in list(pattern.keys()):
                    if pattern[value_pattern]=="id":
                        not_define_id=False
                values_pesquisa=self.create_data(table=table,pattern=pattern,select_country=select_country,id=id,not_define_id=not_define_id,lista_restritiva=filtro_pesquisa)
            dados_gerados["dados"]=values_pesquisa
            
            for campo,valor in pattern.items():
                    if "id" in valor:
                        if campo in filtro_pesquisa:
                            not_define_id=False

            _id=self.process_id(data=dados_gerados["dados"],pattern=pattern,id=id)
            if not not_define_id and _id !=-1:
                dados_gerados["idNoBD"]=_id

            self.logging.debug("dado gerado por create_select",extra=self.dict_all_string(dados_gerados))
            
            dados_gerados["dados"]=values_pesquisa
            if  dados_gerados["dados"]== {} or dados_gerados["dados"]== None or "dados" not in list(dados_gerados.keys()):
                raise self.ValorInvalido(valor_inserido=dados_gerados["dados"],campo="dados",valor_possivel="não ser vazio")
            
        except self.ValorInvalido as e:
            self.logging.exception(e)
            chamadas=loggingSystem.full_inspect_caller()
            if chamadas.count(chamadas[0])>5:
                return None
            filtro_pesquisa=self.gerador_filtro(pattern,completo=True)[0]
            dados_gerados=self.create_select(table=table,pattern=pattern,select_country=select_country,id=id,filtro_pesquisa=filtro_pesquisa,values_pesquisa=values_pesquisa,not_define_id=not_define_id)
        finally:
            return dados_gerados

    def create_update(self,table:str,pattern:dict,filtro_pesquisa:list=[],filtro_update:list=[],select_country:str="random",id:int=-1,values_pesquisa:dict={},values_update:dict={},not_define_id:bool=False) -> dict:
        """cria um novo dado para ser inserido no sqlite para a operação de update

        Args:
            table (str): nome da tabela do sql que o dado será inserido
            pattern (dict): padrão que será usado pelo gerador seguindo o padrão descrtito no json,esses padrões serão descritos a parte
            id (int, optional): id do dado gerado no banco de dados,se preenchido ele será o definido,caso contrário ele será o próximo possivel no bd de acordo com os registros do sqlite. Defaults to -1.
            filtro_pesquisa (list, optional): array com os nomes da colunas que serão pesquisadas se for default elas serão geradas randomicamente. Defaults to []
            filtro_update (list, optional): array com os nomes da colunas que serão atualizadas se for default elas serão geradas randomicamente. Defaults to []
            select_country (str, optional): pais do qual o padrão do faker será usado. Defaults to "random".
            values_pesquisa (dict,optional): valores de substituição para os dados gerados na pesquisa,se não for default,nenhum dado randomico será gerado,serão utilizados os dados inseridos nessa variavel . Defaults to {}.
            values_update (dict,optional): valores de substituição para os dados gerados na atualização,se não for default,nenhum dado randomico será gerado,serão utilizados os dados inseridos nessa variavel . Defaults to {}.
            not_define_id (bool, optional): define se o id ira existir na saida do dado,caso ele seja verdadeiro o id não será nem gerado nem passado para a saida de dado. Defaults to False.

        Returns:
            dict: dados gerados usando faker para corresponder ao padrão da operação de update
        """
        self.logging.info("create_update",extra=locals())
        self.logging.debug("rastreio create_update",extra={"rastreio":loggingSystem.full_inspect_caller()})
        try:
            dados_gerados={"nomeBD":table}
            pattern=pattern.copy()

            dados_gerados["tipoOperacao"]=5

            arrays=self.gerador_filtro(pattern,pesquisa_pre=filtro_pesquisa,retorno_pre=filtro_update,completo=True)
            _filtro_update=arrays[1]
            _filtro_pesquisa=arrays[0]

            if values_pesquisa == {}:
                for value_pattern in list(pattern.keys()):
                    if pattern[value_pattern]=="id":
                        not_define_id=False
                values_pesquisa=self.create_data(table=table,pattern=pattern,select_country=select_country,id=id,not_define_id=not_define_id,lista_restritiva=_filtro_pesquisa)
            dados_gerados["dados"]=values_pesquisa

            if values_update == {}:
                for value_pattern in list(pattern.keys()):
                    if pattern[value_pattern]=="id":
                        not_define_id=False
                values_update=self.create_data(table=table,pattern=pattern,select_country=select_country,id=id,not_define_id=not_define_id,lista_restritiva=_filtro_update)
            dados_gerados["adicionais"]=values_update

            for campo,valor in pattern.items():
                    if "id" in valor:
                        if campo in filtro_pesquisa:
                            not_define_id=False

            _id=self.process_id(data=dados_gerados["dados"],pattern=pattern,id=id)
            if not not_define_id and _id !=-1:
                dados_gerados["idNoBD"]=_id

            self.logging.debug("dado gerado por create_select",extra=self.dict_all_string(dados_gerados))

            if  dados_gerados["dados"]== {} or dados_gerados["dados"]== None or "dados" not in list(dados_gerados.keys()): # pesquisa
                raise self.TamanhoArrayErrado(valor_inserido=dados_gerados["dados"],valor_possivel="não vazio",campo="pesquisa")
            if  dados_gerados["adicionais"]== {} or dados_gerados["adicionais"]== None or "adicionais" not in list(dados_gerados.keys()): # update
                raise self.TamanhoArrayErrado(valor_inserido=dados_gerados["adicionais"],valor_possivel="não vazio",campo="update")

            self.logging.debug("dado gerado por create_update",extra=self.dict_all_string(dados_gerados))
        except self.TamanhoArrayErrado as e:
            self.logging.exception(e)
            chamadas=loggingSystem.full_inspect_caller()
            if chamadas.count(chamadas[0])>5:
                return None
            elif e.campo== "pesquisa":
                filtro_pesquisa=self.gerador_filtro(pattern,completo=True,retorno_pre=filtro_update)[0]
                dados_gerados=self.create_update(table=table,pattern=pattern,filtro_pesquisa=filtro_pesquisa,select_country=select_country,id=id,filtro_update=filtro_update,not_define_id=not_define_id)
            elif e.campo== "update":
                filtro_update=self.gerador_filtro(pattern,completo=True,pesquisa_pre=filtro_pesquisa)[1]
                dados_gerados=self.create_update(table=table,pattern=pattern,filtro_pesquisa=filtro_pesquisa,select_country=select_country,id=id,filtro_update=filtro_update,not_define_id=not_define_id)
        finally:
            return dados_gerados

    def create_delete(self,table:str,pattern:dict={},select_country:str="random",id:int=-1,values:dict={},filtro:list=[],not_define_id:bool=False) -> dict:
        """cria um novo dado para ser inserido no sqlite para a operação de delete

        Args:
            table (str): nome da tabela do sql que o dado será inserido
            pattern (dict): padrão que será usado pelo gerador seguindo o padrão descrtito no json,esses padrões serão descritos a parte
            id (int, optional): id do dado gerado no banco de dados,se preenchido ele será o definido,caso contrário ele será o próximo possivel no bd de acordo com os registros do sqlite. Defaults to -1.
            filtro (list, optional): array com os nomes da colunas que serão pesquisadas se for default elas serão geradas randomicamente. Defaults to [].
            select_country (str, optional): pais do qual o padrão do faker será usado. Defaults to "random".
            values (dict,optional): valores de substituição para os dados gerados,se não for default,nenhum dado randomico será gerado,serão utilizados os dados inseridos nessa variavel . Defaults to {}.
            not_define_id (bool, optional): define se o id ira existir na saida do dado,caso ele seja verdadeiro o id não será nem gerado nem passado para a saida de dado. Defaults to False.

        Returns:
            dict: [description]
        """        
        self.logging.info("create_delete",extra=locals())
        self.logging.debug("rastreio create_delete",extra={"rastreio":loggingSystem.full_inspect_caller()})
        try:
            dados_gerados={"nomeBD":table}
            pattern=pattern.copy()
            dados_gerados["tipoOperacao"]=6
            dados_gerados["adicionais"]=[]
            
            if values == {}:
                arrays=self.gerador_filtro(pattern,pesquisa_pre=filtro,completo=True)
            
                for value_pattern in list(pattern.keys()):
                        if pattern[value_pattern]=="id" and value_pattern in arrays[0] :
                            not_define_id=False
                values=self.create_data(table=table,pattern=pattern,select_country=select_country,id=id,not_define_id=not_define_id,lista_restritiva=arrays[0])
            dados_gerados["dados"]=values

            _id=self.process_id(data=dados_gerados["dados"],pattern=pattern,id=id)
            if not not_define_id and _id !=-1:
                dados_gerados["idNoBD"]=_id

            if  len(dados_gerados["dados"]) == 0 or "dados" not in list(dados_gerados.keys()):
                raise self.ValorInvalido(valor_inserido=dados_gerados["dados"],campo="dados",valor_possivel="não ser vazio")
        except self.ValorInvalido as e:
            self.logging.exception(e)
            chamadas=loggingSystem.full_inspect_caller()
            if chamadas.count(chamadas[0])>5:
                return None
            filtro=self.gerador_filtro(pattern,completo=True)[0]
            dados_gerados=self.create_delete(table=table,pattern=pattern,select_country=select_country,id=id,filtro=filtro,values=values,not_define_id=not_define_id)
        finally:
            self.logging.debug("dado gerado por create_delete",extra=dados_gerados)
            return dados_gerados

#relacionado com a geração do sql final
    def generate_SQL_command_from_data(self,data:dict):
        '''
                tipo de operação:int #1:insersão,2:leitura,3:busca,4:edição,5:deleção
                bd:string # banco de dados en que será inserido
                os dados a baixo estão definidos para uma insercao:
                    associações: #text  IGNORADO
                    outros dados do bd: #text
                    {
                        nome da variavel:conteudo da variavel #string:string  #nome do tipo da variavel do bd e o conteudo dela
                    }

                os dados para uma leitura completa apenas são os basicos,todo o restante será ignorado,quando uma leitura é feita 
                os dados a baixo estão definidos para uma busca:
                    associações: #text     IGNORADO
                    outros dados do bd: #text
                    {
                        nome da variavel:conteudo da variavel #string:string  #nome da coluna e valor a ser pesquisado,podem ser multiplos
                    }
                os dados a baixo são associados com uma busca fitrada
                    associações: #text    
                    [{variavelRetornada:variavel}]  # inserir o termo"variavelRetornada"(nome pode ser alterado,apenas serve para referencia,mas deve ser editado no codigo também) seguido pelo nome da coluna que deseja realmente retornar,cada variavel deve ser colocada em um dictionary com apenas ela,devido a necessidade para compatibilidade com todos os outros comandos
                    outros dados do bd: #text
                    {
                        nome da variavel:conteudo da variavel #string:string  #nome da coluna e valor a ser pesquisado,podem ser multiplos
                    }
            '''
        self.logging.info("generate_SQL_command_from_data",extra=locals())
        command=""
        try:
            if data["tipoOperacao"]==1:#insercao
                command+="INSERT INTO "
            elif data["tipoOperacao"] in [2,3]:#leitura completa,#busca
                command+="SELECT * FROM "
            elif data["tipoOperacao"] == 4:#busca filtrada
                command+="SELECT "
                for i in data['adicionais']:
                    command+= str(i["adicionais"])
                    if command != data["adicionais"][-1]:
                        command+= ","
                # if (data["idNoBD"]>0 and data["idNoBD"] != None) and ("idNoBD" in data ):
                #     if len(data['adicionais'])>0:
                #         command+=" , "
                #     for campo,valor in self.json_loaded[data["nomeBD"]].items():
                #         if "id" in valor:
                #             if campo in data:
                #                 command+= data[campo]
                #                 break
                command+=" FROM "
            elif data["tipoOperacao"]==5:#edicao
                command+=" UPDATE "
            elif data["tipoOperacao"]==6:#delecao
                command+="DELETE FROM "
            else:
                raise self.ValorInvalido(valor_inserido=data["tipoOperacao"])

            command+=str(data["nomeBD"])

            if data["tipoOperacao"] == 1:#insercao
                command+=" ("
                for coluna in data["dados"].keys():
                    command+=coluna
                    if coluna != list(data["dados"].keys())[-1]:
                        command+=","
                command+=") VALUES ("
                for coluna in data["dados"].keys():
                    if type(data["dados"][coluna])==type("") or type(data["dados"][coluna])==type({}) or  type(data["dados"][coluna])==type([])  :
                        command+='"'+data["dados"][coluna].replace("\n","")+'"'
                    else:
                        command+=str(data["dados"][coluna])
                    if coluna != list(data["dados"].keys())[-1]:
                        command+=","
                command+=")"
            #elif data["tipoOperacao"]==2:#leitura completa
            if data["tipoOperacao"] == 5:#edicao
                command+=" SET "
                for coluna in data["dados"].keys():
                    if type("")==type(data["dados"][coluna]):
                        command+=coluna + " = "+data["dados"][coluna]
                    else:
                        command+=coluna + " = "+str(data["dados"][coluna])
                    if coluna != list(data["dados"].keys())[-1]:
                        command+=" , "
            if data["tipoOperacao"] in [3,4,6,5]:# busca #busca filtrada #remocao
                command+=" WHERE "
                for coluna in data["dados"].keys():
                    if type("")==type(data["dados"][coluna]):
                        command+=coluna + " IS "+data["dados"][coluna]
                    else:
                        command+=coluna + " IS "+str(data["dados"][coluna])
                    if coluna != list(data["dados"].keys())[-1]:
                        command+=" AND "
                if data["idNoBD"] != None and "idNoBD" in data :
                    if len(data["dados"].keys())>0 and data["idNoBD"]>0:
                        command+=" AND "
                    for campo,valor in self.json_loaded[data["nomeBD"]].items():
                        if "id" in valor:
                            if campo in data:
                                command+= data[campo]
                                break
                    command+=" IS "+str(data["idNoBD"])
            # elif data["tipoOperacao"]==5:#edicao
            #     command+=" WHERE "
            #     for coluna in data["adicionais"].keys():
            #         command+=str(coluna) + " IS "+str(data["adicionais"][coluna])
            #         if coluna != data["adicionais"].keys()[-1]:
            #             command+=" AND "
            #     if (data["idNoBD"]!=-1) and ("idNoBD" in data):
            #         if len(data["dados"].keys())>0:
            #             command+=" AND "
            #         command+=nome_coluna_id+" IS "+data["idNoBD"]
            command+="; "
        except sqliteOperationalError as e:
            print("erro operacional no sqlite")
            self.logging.exception(e)
            quit()
        except sqliteError as e:
            print("erro desconhecido no sqlite")
            self.logging.exception(e)
        except self.ValorInvalido as e :
            self.logging.exception(e)
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])
        finally:
            return command

    def generate_SQL_from_sqlite_id(self,id:int)->str:
        """retorna um comando sql a partir de um id de operação do sqlite

        Args:
            id (int): id de operação do sqlite

        Raises:
            self.ValorInvalido: se o valor de id inserido for maior que o total de operações cadastradas no sqlite

        Returns:
            str: comando sql gerado a partir do elemento cadastrado no sqlite
        """        
        max_id=self.processamento_sqlite.total_operacoes()
        try:
            if id>max_id:
                raise self.ValorInvalido(valor_inserido=id,campo="id",valor_possivel="não pode ser maior que "+max_id)
            return self.generate_SQL_command_from_data(data=self.processamento_sqlite.get_operacao_by_id(id))

        except self.ValorInvalido as e:
            self.logging.exception(e)
            return None
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])
            return None

    def gernerate_SQL_from_sqlite_range(self,amount:int)->list:
        """gera um raio de elementos,a partir do primeiro até o informado,de comandos sql a partir do sqlite

        Args:
            amount (int): total de elementos que serão gerados a partir do sqlite

        Returns:
            list: comandos sql gerados a partir do sqlite
        """
        retorno=[]
        for i in range(1,amount+1):
            elemento=self.generate_SQL_from_sqlite_id(i)
            if elemento == None:
                break
            else:
                retorno.append(elemento)
        return retorno

#geradores sqlite

    def gerar_dado_insercao(self,table,pattern:dict,select_country:str="random",id:int=-1):
        """função que chama funções anteriormente descritas para gerar dados para o dado de inserção e cadastrar elas direto no sqlite

        Args:
            table ([type]): tabela para a qual o dado será gerado
            pattern (dict):padrão do dado que será gerado
            select_country (str, optional): pais do qual o padrão do faker será usado. Defaults to "random".
            id (int, optional): id do dado gerado no banco de dados,se preenchido ele será o definido,caso contrário ele será o próximo possivel no bd de acordo com os registros do sqlite. Defaults to -1.
        """        
        self.logging.info("gerar_dado_insercao",extra=locals())
        data=self.create_insert(table=table,pattern=pattern,select_country=select_country,id=id)
        overflow_treat=0
        while data["dados"]=={} or data["dados"]==None :
            data=self.create_insert(table=table,pattern=pattern,select_country=select_country,id=id)
            overflow_treat+=1
            if overflow_treat==5:
                return None
        self.processamento_sqlite.insert_data_sqlite(data=data,table=table)
        self.processamento_sqlite.add_contador_sqlite(table=table)

    def gerar_dado_busca(self,table:str,pattern:dict,dado_existente:bool=False,id:int=-1,select_country:str="random",filtro:list=[],not_define_id:bool=False):
        """função que chama funções anteriormente descritas para gerar dados para o dado de busca e cadastrar elas direto no sqlite

        Args:
            table ([type]): tabela para a qual o dado será gerado
            pattern (dict):padrão do dado que será gerado
            dado_existente (bool, optional): se for verdadeiro o dado gerado deve ser compativel com um dado existente previamente na tabela . Defaults to False.
            select_country (str, optional): pais do qual o padrão do faker será usado. Defaults to "random".
            id (int, optional): id do dado gerado no banco de dados,se preenchido ele será o definido,caso contrário ele será o próximo possivel no bd de acordo com os registros do sqlite. Defaults to -1.
            filtro (list, optional): o filtro de dado que será filtrado,se ele for default ele será gerado randomicamente,se for "*" ele listará todos. Defaults to [].
            not_define_id (bool, optional): se True ele não retornará o id na consulta gerada. Defaults to False.
        """
        self.logging.info("gerar_dado_busca",extra=locals())
        #table,id:int=-1,dados_pesquisados:dict={},filtro=[]
        if id == -1 and dado_existente:
            id=self.processamento_sqlite.random_id_cadastrado(table=table)

        dados_pesquisados=self.create_select(table=table,pattern=pattern,select_country=select_country,id=id,not_define_id=not_define_id)

        if id !=-1 and dado_existente:
            dados_adiquiridos = self.processamento_sqlite.read_operacoes(filtro={"idNoBD":id,"nomeBD":table,"tipoOperacao":1})
            self.logging.debug(dados_adiquiridos[0])
            dados_pesquisados["dados"] = dados_adiquiridos[0]["dados"]
        
        all_filter=False
        if filtro == "*":
            all_filter=True
            filtro=self.gerador_filtro(pattern=pattern)
        self.logging.debug(filtro)
        self.logging.debug(dados_pesquisados["dados"])
        for i in filtro:
            if i in dados_pesquisados["dados"]:
                dados_pesquisados["dados"].pop(i)
        self.logging.debug(dados_pesquisados["dados"])
        if not_define_id:
            data=self.create_select(table=table,values_pesquisa=dados_pesquisados["dados"],filtro_pesquisa=filtro,pattern=pattern,select_country=select_country)
        else:
            data=self.create_select(table=table,values_pesquisa=dados_pesquisados["dados"],id=id,filtro_pesquisa=filtro,pattern=pattern,select_country=select_country)
        if all_filter:
            data["tipoOperacao"]=3
        self.logging.debug("dado gerado gerar_dado_busca",extra=self.dict_all_string(data))
        self.processamento_sqlite.insert_data_sqlite(data,table=table)

    def gerar_dado_delecao(self,table:str,pattern:dict,dado_existente:bool=False,id:int=-1,select_country:str="random",not_define_id:bool=False):
        """função que chama funções anteriormente descritas para gerar dados para o dado de deleção e cadastrar elas direto no sqlite

        Args:
            table ([type]): tabela para a qual o dado será gerado
            pattern (dict):padrão do dado que será gerado
            dado_existente (bool, optional): se for verdadeiro o dado gerado deve ser compativel com um dado existente previamente na tabela . Defaults to False.
            select_country (str, optional): pais do qual o padrão do faker será usado. Defaults to "random".
            id (int, optional): id do dado gerado no banco de dados,se preenchido ele será o definido,caso contrário ele será o próximo possivel no bd de acordo com os registros do sqlite. Defaults to -1.
            filtro (list, optional): o filtro de dado que será filtrado,se ele for default ele será gerado randomicamente,se for "*" ele listará todos. Defaults to [].
            not_define_id (bool, optional): se True ele não retornará o id na consulta gerada. Defaults to False.
        """
        self.logging.info("gerar_dado_delecao",extra=locals())
        values={}
        if id == -1 and dado_existente:
            id=self.processamento_sqlite.random_id_cadastrado(table=table)
            dados_adiquiridos = self.processamento_sqlite.read_operacoes(filtro={"idNoBD":id,"nomeBD":table,"tipoOperacao":1})
            self.logging.debug(dados_adiquiridos[0])
            values = dados_adiquiridos[0]["dados"]
        if not_define_id:
            data=self.create_delete(table=table,pattern=pattern,select_country=select_country,values=values,not_define_id=not_define_id)
        else:
            data=self.create_delete(table=table,pattern=pattern,select_country=select_country,id=id,values=values,not_define_id=not_define_id)
        self.logging.debug("gerar_dado_delecao",extra=self.dict_all_string(data))
        self.processamento_sqlite.insert_data_sqlite(data,table=table)

    def gerar_dado_leitura_completa(self,table:str,pattern:dict,filtro:list=[],select_country:str="random",not_define_id:bool=False):
        """função que chama funções anteriormente descritas para gerar dados para o dado de leitura e cadastrar elas direto no sqlite

        Args:
            table ([type]): tabela para a qual o dado será gerado
            pattern (dict):padrão do dado que será gerado
            dado_existente (bool, optional): se for verdadeiro o dado gerado deve ser compativel com um dado existente previamente na tabela . Defaults to False.
            select_country (str, optional): pais do qual o padrão do faker será usado. Defaults to "random".
            id (int, optional): id do dado gerado no banco de dados,se preenchido ele será o definido,caso contrário ele será o próximo possivel no bd de acordo com os registros do sqlite. Defaults to -1.
            filtro (list, optional): o filtro de dado que será filtrado,se ele for default ele será gerado randomicamente,se for "*" ele listará todos. Defaults to [].
            not_define_id (bool, optional): se True ele não retornará o id na consulta gerada. Defaults to False.
        """
        self.logging.info("gerando dados de leitura e inserindo em sqlite")

        data=self.create_select(table=table,filtro_pesquisa=filtro,select_country=select_country,pattern=pattern,not_define_id=not_define_id,values_pesquisa={"":""})
        data["dados"]={}
        data["tipoOperacao"]=2
        self.logging.debug("gerar_dado_leitura_completa",extra=self.dict_all_string(data))
        self.processamento_sqlite.insert_data_sqlite(data,table=table)

    def gerar_dado_atualizacao(self,table:str,pattern:dict,dado_existente:bool=False,id:int=-1,select_country:str="random",not_define_id=False,values_pesquisa:dict={},values_update:dict={}):
        """função que chama funções anteriormente descritas para gerar dados para o dado de atualização e cadastrar elas direto no sqlite

        Args:
            table ([type]): tabela para a qual o dado será gerado
            pattern (dict):padrão do dado que será gerado
            dado_existente (bool, optional): se for verdadeiro o dado gerado deve ser compativel com um dado existente previamente na tabela . Defaults to False.
            select_country (str, optional): pais do qual o padrão do faker será usado. Defaults to "random".
            id (int, optional): id do dado gerado no banco de dados,se preenchido ele será o definido,caso contrário ele será o próximo possivel no bd de acordo com os registros do sqlite. Defaults to -1.
            filtro (list, optional): o filtro de dado que será filtrado,se ele for default ele será gerado randomicamente,se for "*" ele listará todos. Defaults to [].
            not_define_id (bool, optional): se True ele não retornará o id na consulta gerada. Defaults to False.
        """
        self.logging.info("gerando dados de atualizacao e inserindo em sqlite")        #table,id:int=-1,dados_pesquisados:dict={},
        

        if id !=-1 and dado_existente:
            id=self.processamento_sqlite.random_id_cadastrado(table=table)
            dados_adiquiridos = self.processamento_sqlite.read_operacoes(filtro={"idNoBD":id,"nomeBD":table,"tipoOperacao":1})
            self.logging.debug(dados_adiquiridos[0])
            values_pesquisa = dados_adiquiridos[0]["dados"]
        
        data=self.create_update(table=table,pattern=pattern,select_country=select_country,id=id,not_define_id=not_define_id,values_pesquisa=values_pesquisa,values_update=values_update)
        
        self.logging.debug("gerar_dado_busca",extra=self.dict_all_string(data))
        self.processamento_sqlite.insert_data_sqlite(data,table=table)

#dbbench

    def generate_dbbench_data_row(self,data:dict):
        '''
                tipo de operação:int #1:insersão,2:leitura,3:busca,4:edição,5:deleção
                bd:string # banco de dados en que será inserido
                os dados a baixo estão definidos para uma insercao:
                    associações: #text  IGNORADO
                    outros dados do bd: #text
                    {
                        nome da variavel:conteudo da variavel #string:string  #nome do tipo da variavel do bd e o conteudo dela
                    }

                os dados para uma leitura completa apenas são os basicos,todo o restante será ignorado,quando uma leitura é feita 
                os dados a baixo estão definidos para uma busca:
                    associações: #text     IGNORADO
                    outros dados do bd: #text
                    {
                        nome da variavel:conteudo da variavel #string:string  #nome da coluna e valor a ser pesquisado,podem ser multiplos
                    }
                os dados a baixo são associados com uma busca fitrada
                    associações: #text    
                    [{variavelRetornada:variavel}]  # inserir o termo"variavelRetornada"(nome pode ser alterado,apenas serve para referencia,mas deve ser editado no codigo também) seguido pelo nome da coluna que deseja realmente retornar,cada variavel deve ser colocada em um dictionary com apenas ela,devido a necessidade para compatibilidade com todos os outros comandos
                    outros dados do bd: #text
                    {
                        nome da variavel:conteudo da variavel #string:string  #nome da coluna e valor a ser pesquisado,podem ser multiplos
                    }
            '''
        self.logging.info("generate_dbbench_data_row",extra=locals())
        command=[]
        try:
            if data["tipoOperacao"] == 4:#busca filtrada
                for i in data['adicionais']:
                    command.append(str(i["adicionais"]))
            command.append(str(data["nomeBD"]))

            if data["tipoOperacao"] == 1:#insercao
                for coluna in data["dados"].keys():
                    command.append(str(coluna))
                for coluna in data["dados"].keys():
                    if type(data["dados"][coluna])==type(""):
                        command.append(data["dados"][coluna].replace("\n",""))
                    else:
                        command.append(str(data["dados"][coluna]))
            #elif data["tipoOperacao"]==2:#leitura completa
            if data["tipoOperacao"] == 5:#edicao
                for coluna in data["dados"].keys():
                    if type("")==type(data["dados"][coluna]):
                        command.append(str(coluna + " = "+data["dados"][coluna]))
                    else:
                        command.append(str(coluna + " = "+str(data["dados"][coluna])))
            if data["tipoOperacao"] in [3,4,6,5]:# busca #busca filtrada #remocao
                for coluna in data["dados"].keys():
                    if type("")==type(data["dados"][coluna]):
                        command.append(str(coluna + " IS "+data["dados"][coluna]))
                    else:
                        command.append(str(coluna + " IS "+str(data["dados"][coluna])))
                    for campo,valor in self.json_loaded[data["nomeBD"]].items():
                        if "id" in valor:
                            if campo in data:
                                command.append(str(data[campo])+" IS "+str(data["idNoBD"]))
                                break
            return command
        except sqliteOperationalError as e:
            print("erro operacional no sqlite")
            self.logging.exception(e)
            quit()
        except sqliteError as e:
            print("erro desconhecido no sqlite")
            self.logging.exception(e)
        except self.ValorInvalido as e :
            self.logging.exception(e)
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])

    def generate_dbbench_file_from_datas(self,datas:list,file_path: DirEntry):
        """gera arquivo de dados para o dbbench a partir de um array de dados gerados pelos outros metodos da classe

        Args:
            datas (list): array de dados lidos do sqlite
            file_path (DirEntry): diretorio de saida do arquivo do dbbench
        """        
        self.logging.info("generate_dbbench_file_from_datas",extra=locals())
        try:
            file=open(file_path,"a")
            writer = csv.writer(file)
            for data in datas:
                command=self.generate_dbbench_data_row(data=data)
                if command != None:
                    writer.writerow(command)
            file.close()
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])

    def generate_dbbench_all_data_from_database(self,table:str,file_path:DirEntry="./",default_name_pre:str="teste_geracao_dbbench_tipo",default_file_type:str="csv",tipos:list=[]):
        try:
            dados_retornados=self.processamento_sqlite.read_operacoes(filtro={"nomeBD":table})
            
            if tipos==[]:
                dados_separados=[[] for x in range(0,7)]
            else:
                for i in tipos:
                    if i>6 or i<=0:
                        raise self.ValorInvalido(valor_inserido=tipos,campo="tipos",valor_possivel="não ser nem maior que 6 nem menor que 1")
                dados_separados=[[] for x in tipos]
            for i in dados_retornados:
                dados_separados[i["tipoOperacao"]].append(i)
            for i in range(1,7):
                #tmp=choice(dados_separados[i])
                #pprint(dados_separados[i])
                arquivo=str(file_path+default_name_pre+"_"+str(i)+"."+default_file_type)
                self.generate_dbbench_file_from_datas(datas=dados_separados[i],file_path=arquivo)
        except self.ValorInvalido:
            self.logging.exception(e)
        except:
            self.logging.error("Unexpected error:", sys.exc_info()[0])

    def generate_all_dbbench_data(self,file_path:DirEntry="./",default_name_pre:str="teste_geracao_dbbench_tipo",default_file_type:str="csv",tipos:list=[],table_name_in_file:bool=False):
        for i in list(self.json_loaded.keys()):
            if table_name_in_file:
                _default_name_pre=default_name_pre+"_"+i
            else:
                _default_name_pre=default_name_pre
            self.generate_dbbench_all_data_from_database(table=i,file_path=file_path,default_name_pre=_default_name_pre,default_file_type=default_file_type,tipos=tipos)

#gerador json

    def gerar_dados_validos_por_json(self,tipo:int=0,select_country:str="random",table:str="random",quantidade="random",dado_existente:bool=False):
        """gera uma sequencia de dados para serem inseridos no sqlite,esses dados são aleatórios,cada execução dessa função corresponde a um ciclo de geração de dado

        Args:
            tipo (int, optional): tipo de dado  que será gerado,se é uma inserção,listagem,busca,busca filtrada,atualização ou deleção,se default será escolhido randomicamente. Defaults to 1.
            select_country (str, optional): pais do qual o padrão do faker será usado. Defaults to "random".
            table (str, optional): nome da tabela no qual os serão gerados,se default será escolhido randomicamente entre os existentes dentro do arquivo json. Defaults to "random".
            quantidade (str, optional): quantidade de dados gerados desta tabela selecionada. Defaults to "random".
            dado_existente (bool, optional): verifica se o dado é compativel com os previamente existenes no bd cadastrado. Defaults to False.
        """
        self.logging.info("gerar_dados_por_json",extra=locals())
        try:
            
            if table == "random":
                table=random.choice(self.json_loaded.keys())
            if quantidade == "random":
                quantidade=randint(0, 20)
            self.logging.debug("dados gerados automaticamente",extra={"quantidade":str(quantidade)})
            for i in range(0,quantidade):
                self.ciclo_geracao_dados_json(tipo=tipo,select_country=select_country,table=table,dado_existente=dado_existente)
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])

    #TODO gerar dados de erro por json

    def  ciclo_geracao_dados_json(self,tipo:list=[],select_country:str="random",table:str="random",dado_existente:bool=False):
        """gera uma das possiveis operações para a tebala definida 

        Args:
            tipo (list, optional): tipo de dado  que será gerado,se é uma inserção,listagem,busca,busca filtrada,atualização ou deleção,se default será escolhido randomicamente. Defaults to [].
            select_country (str, optional): pais do qual o padrão do faker será usado. Defaults to "random".
            table (str, optional): nome da tabela no qual os serão gerados,se default será escolhido randomicamente entre os existentes dentro do arquivo json. Defaults to "random".
            dado_existente (bool, optional): verifica se o dado é compativel com os previamente existenes no bd cadastrado. Defaults to False.
        """        
        def random_bool():
                    return choice([True, False])
        self.logging.info("ciclo_geracao_dados_json",extra=locals())
        try:
            if tipo==[]:
                tipo_execucao=[randint(1,6)]
            else:
                tipo_execucao=tipo
            tracking_data=locals()
            tracking_data["tipo_execucao"]=tipo_execucao
            self.logging.info("ciclo_geracao_dados_json",extra=self.dict_all_string(tracking_data))
            filtro=self.gerador_filtro(pattern=self.json_loaded[table])
            self.logging.debug("ultimo id cadastrado",extra={"id":self.processamento_sqlite.buscar_ultimo_id_cadastrado(table=table)})
            ultimo_id=self.processamento_sqlite.buscar_ultimo_id_cadastrado(table=table)
            for _tipo_execucao in tipo_execucao:
                if _tipo_execucao == 1:#criacao
                    self.gerar_dado_insercao(table=table,pattern=self.json_loaded[table],select_country=select_country)
                elif _tipo_execucao == 2 and ultimo_id != 0:#leitura completa
                    self.gerar_dado_leitura_completa(table=table,pattern=self.json_loaded[table],filtro=filtro,select_country=select_country)
                elif _tipo_execucao == 3 and ultimo_id != 0:#busca
                    self.gerar_dado_busca(table=table,pattern=self.json_loaded[table],select_country=select_country,id=self.processamento_sqlite.random_id_cadastrado(table=table),filtro="*",dado_existente=dado_existente,not_define_id=random_bool())
                elif _tipo_execucao == 4 and ultimo_id != 0:#busca filtrada
                    self.gerar_dado_busca(table=table,pattern=self.json_loaded[table],select_country=select_country,id=self.processamento_sqlite.random_id_cadastrado(table=table),filtro=filtro,not_define_id=random_bool())
                elif _tipo_execucao == 5 and ultimo_id != 0:#edicao
                    self.gerar_dado_atualizacao(table=table,pattern=self.json_loaded[table],dado_existente=dado_existente,select_country=select_country,not_define_id=random_bool())
                elif _tipo_execucao == 6 and ultimo_id != 0:#delecao
                    self.gerar_dado_delecao(table=table,pattern=self.json_loaded[table],dado_existente=dado_existente,select_country=select_country,not_define_id=random_bool())
                elif ultimo_id == 0:
                    raise self.ValorInvalido(campo="quantidade de valores cadastrados",valor_inserido=tipo,valor_possivel="maior que 0")
                else:
                    raise self.ValorInvalido(campo="tipo",valor_inserido=tipo,valor_possivel="de 1 a 6")
        except self.TamanhoArrayErrado as e :
            self.logging.exception(e)
        except self.ValorInvalido as e:
            self.logging.exception(e)
            if e.campo =="quantidade de valores cadastrados" and tipo == 0:
                self.ciclo_geracao_dados_json(tipo=1,select_country=select_country,table=table,dado_existente=dado_existente)
                self.ciclo_geracao_dados_json(tipo=tipo_execucao,select_country=select_country,table=table,dado_existente=dado_existente)
        except self.TipoDeDadoIncompativel as e:
            self.logging.exception(e)

    def gerar_todos_dados_por_json(self,tipo:list=[],select_country:str="random",quantidade_ciclo="random",total_ciclos="random",quantidade_final:int=0):
        """gera os dados de acordo com o arquivo json e quantidades definidas

        Args:
            json_file ([type]): arquivo do qual os dados de padrão serão carregados
            tipo (int, optional): tipo de dado  que será gerado,se é uma inserção,listagem,busca,busca filtrada,atualização ou deleção,se default será escolhido randomicamente. Defaults to 1.
            select_country (str, optional): pais do qual o padrão do faker será usado. Defaults to "random".
            quantidade_ciclo (str, optional): quantidade de dados que serão gerados a cada ciclo. Defaults to "random".
            total_ciclos (str, optional): quantidade de ciclos de dados que serão gerados. Defaults to "random".
            quantidade_final (int, optional): se definido os dados serão gerados de forma automática até atingir a quantidade de dados cadastrados ,ignorando o total de ciclos. Defaults to 0.
        """
        self.logging.info("gerar_todos_dados_por_json",extra=locals())
        if quantidade_ciclo == "random":
            quantidade_ciclo=randint(0, 20)
        if total_ciclos == "random":
            total_ciclos=randint(0, 20)
        
        if quantidade_final==0:
            for i in range(0,total_ciclos):
                cadastrados=self.processamento_sqlite.total_operacoes()
                self.logging.debug("total cadastrado",extra={"cadastrados":cadastrados})
                table = choice(list(self.json_loaded.keys()))
                self.gerar_dados_validos_por_json(select_country=select_country,table=table,quantidade=quantidade_ciclo,tipo=tipo)
        elif quantidade_final>0:
            cadastrados=self.processamento_sqlite.total_operacoes()
            while cadastrados <quantidade_final:
                cadastrados=self.processamento_sqlite.total_operacoes()
                self.logging.debug("total cadastrado",extra={"cadastrados":cadastrados})
                table = choice(list(self.json_loaded.keys()))
                self.gerar_dados_validos_por_json(select_country=select_country,table=table,quantidade=quantidade_ciclo,tipo=tipo)

class InteracaoSqlite(ProcessamentoSqlite):
    def __init__(self,sqlite_db="./initial_db.db",sql_file_pattern="./sqlitePattern.sql", log_file="./geradorSQL.log",level:int=10,logging_pattern='%(name)s - %(levelname)s - %(message)s',logstash_data:dict={}):
        """
        classe para gerenciar arquivos csv
        :param loggin_name: nome do log que foi definido para a classe,altere apenas em caso seja necessário criar multiplas insstancias da função
        :param log_file: nome do arquivo de log que foi definido para a classe,altere apenas em caso seja necessário criar multiplas insstancias da função
        """
        
        super().__init__(sqlite_db=sqlite_db,sql_file_pattern=sql_file_pattern,log_file=log_file,logging_pattern=logging_pattern,level=level,log_name="gerador sql interacao sqlite",logstash_data=logstash_data)
        #self.create_temporary_DB(local=sqlite_db,pattern=sql_file_pattern)
        
    def buscar_ultimo_id_cadastrado(self,table:str)->int:
        """musca o ultimo id cadastrado de uma tabela expecifica

        Args:
            table (str): [nome da tabela que sera pesquisada]

        Returns:
            int:ultimo id cadastrado da tabela informada
        """        
        self.logging.info("buscar_ultimo_id_cadastrado",extra=locals())
        query={"nomeBD":table}
        filtro=["numeroDDadosCadastrados"]
        self.certify_if_contador_exists(table)
        retorno=self.read_data_sqlite(table="contadores",query=query,filtro=filtro)
        self.logging.debug("ultimo id cadastrado",extra={"retorno":retorno[0][0]})
        return int(retorno[0][0])

    def random_id_cadastrado(self,table:str) -> int:
        """um id aleatorio dentre os cadastrados numa tabela definida

        Args:
            table (str): nome da tabela que sera usada

        Returns:
            int: um id aleatorio de um bd
        """        
        self.logging.info("random_id_cadastrado",extra=locals())
        tmp=self.buscar_ultimo_id_cadastrado(table=table)
        tmp2=randint(1,tmp)
        self.logging.debug("",extra={"ultimo id":str(tmp),"valor escolhido":str(tmp2)})
        return tmp2

    def add_contador_sqlite(self,table:str):
        """aumenta em um o total de elementos cadastrados em uma tabela expecifica

        Args:
            table (str): nome da tabela
        """        
        self.logging.info("add_contador_sqlite",extra=locals())
        try:
            cursor = self.conn.cursor()
            self.certify_if_contador_exists(table)
            cursor.execute("UPDATE contadores SET numeroDDadosCadastrados = numeroDDadosCadastrados+1 WHERE nomeBD='"+table+"';")
            self.conn.commit()
            self.logging.debug("adicionado contador")
        except sqliteOperationalError as e:
            print("erro operacional no sqlite")
            self.logging.exception(e)
            quit()
        except sqliteError as e:
            print("erro desconhecido no sqlite")
            self.logging.exception(e)
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])

    def total_operacoes(self)->int:
        """total de elementos cadastrados na tabela de operações

        Returns:
            int: total de elementos cadastrados na tabela de operações
        """        
        self.logging.info("buscar_ultimo_id_cadastrado",extra=locals())
        read_command="SELECT id FROM operacoes ORDER BY id DESC LIMIT 1;"
        cursor = self.conn.cursor()
        self.logging.info(read_command)
        cursor.execute(read_command)
        self.conn.commit()
        saida=cursor.fetchall()
        
        if saida == []:
            self.logging.debug("total de operacoes",extra={"total":saida})
            return 0
        else:
            self.logging.debug("total de operacoes",extra={"total":saida[0][0]})
            return int(saida[0][0])
        
    def certify_if_contador_exists(self,table:str):
        """verifica e corrige se um contador não existir na tabela de contadores

        Args:
            table (str): nome da tabela que será verificada se existe o contador
        """        
        self.logging.info("certify_if_contador_exists",extra=locals())
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM contadores WHERE nomeBD is '"+table+"';")
        listagem=cursor.fetchall() 
        if listagem == []:
            cursor.execute("INSERT INTO contadores(nomeBD,numeroDDadosCadastrados) VALUES ('"+table+"',0);")

    def read_contadores(self,filtro:dict={},query:Union[str,dict]="*")->list:
        """consulta e le um elemento ou varios da tabela de contadores

        Args:
            filtro (dict, optional): elementos que serão retornados dos elementos . Defaults to {}.
            query (str, optional): elementos de pesquisa que serão usados . Defaults to "*".

        Returns:
            list: lista de todos elementos que foram reconhecidos pela query
        """        
        self.logging.info("read_contadores",extra=locals())
        return self.read_data_sqlite("contadores",filtro=filtro,query=query)

    def read_operacoes(self,filtro:Union[str,dict]="*",query:Union[str,dict]="*")->list:
        """consulta e le um elemento ou varios da tabela de operações

        Args:
            filtro (dict, optional): elementos que serão retornados dos elementos . Defaults to {}.
            query (str, optional): elementos de pesquisa que serão usados . Defaults to "*".

        Returns:
            list: lista de todos elementos que foram reconhecidos pela query
        """        
        self.logging.info("read_operacoes",extra=locals())
        tmp=self.read_data_sqlite("operacoes",filtro=filtro,query=query)
        self.logging.debug(tmp)
        retorno=[]
        for i in tmp:
            tmp2=self.process_data_generated(data=i,with_id=True)
            tmp2.pop("id")
            retorno.append(tmp2)
        return retorno

    def get_operacao_by_id(self,id:int)->dict:
        """pesquisa um elemento na tabela de operações pelo id

        Args:
            id (int): id que será pesquisado

        Returns:
            dict: elemento retornado
        """        
        retornos=self.read_operacoes(query={"id":id})
        for i in retornos:
            return i

    def process_data_generated(self,data:list,tipo_adicional:str="dict",with_id:bool=False) -> dict:
        """processa o dado lido do sqlite para um formato de dict usavel 

        Args:
            text (str): texto gerado pelo comando de leitura do sqlite

        Returns:
            dict: dict usavel e processado do que foi lido do sqlite
        """        
        self.logging.info("process_data_generated",extra=locals())
        etapa1_operacoes=data
        self.logging.debug(etapa1_operacoes)
        output={}
        if with_id:
            output["id"]=etapa1_operacoes[0]
            output["tipoOperacao"]=etapa1_operacoes[1]
            output["nomeBD"]=etapa1_operacoes[2]
            output["idNoBD"]=etapa1_operacoes[3]
            output["adicionais"]=etapa1_operacoes[4]
            output["dados"]=etapa1_operacoes[5]
        else:
            output["tipoOperacao"]=etapa1_operacoes[0]
            output["nomeBD"]=etapa1_operacoes[1]
            output["idNoBD"]=etapa1_operacoes[2]
            output["adicionais"]=etapa1_operacoes[3]
            output["dados"]=etapa1_operacoes[4]
        self.logging.debug(output)
        if tipo_adicional=="dict":
            adicionais=self.string_to_dict(output["adicionais"])
        elif tipo_adicional=="dict_array":
            pattern_adicionais=r"\[\{(.*)\}\]"
            adicionais=[]
            for dado in re.findall(pattern_adicionais, output["adicionais"])[0].split("},{"):
                adicionais.append(self.string_to_dict(dado,patter_externo=r"(.*)"))
        elif tipo_adicional == "array":
            adicionais=self.string_to_dict(output["adicionais"],is_dict=False)
        self.logging.debug(adicionais)
        output["adicionais"]=adicionais
        output["dados"]=self.string_to_dict(output["dados"])
        return output
    
    def string_to_dict(self,text:str,patter_externo=r"\{(.*)\}",pattern_interno=r"([^:]*)\:(.*)",external_header_list:list=[],is_dict=True) -> dict:
        """converte string legivel em dict usavel a partir de um string

        Args:
            text (str): texto de entrada
            patter_externo (regexp, optional): expressão regular usado para processar os dados inseridos,para separar a parte mais externa do string. Defaults to r"\{(.*)}".
            pattern_interno (regexp, optional): expressão regular usado para processar os dados inseridos,para processar a parte mais interna do string. Defaults to r"([^:]*)\:(.*)".
            external_header_list (list, optional): header do dict final. Defaults to [].
            is_dict (boolean): defini se o retorno é um dictionary ou um array
        Returns:
            (dict,list): dictionary ou array com o conteudo usavel do retorno de uma consulta no sqlite
        """        
        self.logging.info("string_to_dict",extra=locals())
        if not is_dict and patter_externo==r"\{(.*)\}" and pattern_interno==r"([^:]*)\:\ (.*)":
            patter_externo=r"\[(.*)\]"
            pattern_interno=r"(.*)"
        pattern_etapa1=patter_externo
        if type(text) == type(None):
            text="{}"
        etapa1_dados=re.findall(pattern_etapa1,text)
        if etapa1_dados == [''] or etapa1_dados == [] :
            if is_dict:
                return {}
            else:
                return []
        etapa1_dados=etapa1_dados[0].split(",")
        pattern_dados_etapa2=pattern_interno
        if is_dict:
            dados={}
        else:
            dados=[]
        tmp=0
        if is_dict:
            for dado in etapa1_dados:
                etapa2_dados=re.findall(pattern_dados_etapa2,dado)
                if etapa2_dados==[]:
                    break
                else:
                    etapa2_dados=etapa2_dados[0]
                if external_header_list == []:
                    #fazer metodo q identifica tipo e converte de string para o tipo certo
                    value=etapa2_dados[1].replace("'","").replace('"',"")[1:]
                    dados[etapa2_dados[0].replace("'","").replace('"',"")]=value
                else:
                    dados[external_header_list[tmp]]=etapa2_dados[0]
                    tmp+=1
        else:
            for dado in etapa1_dados:
                etapa2_dados=re.findall(pattern_dados_etapa2,dado)[0]
                dados[tmp]=etapa2_dados[0]
                tmp+=1
        self.logging.debug("string_to_dict",extra=self.dict_all_string(dados))
        return dados