from array import array
from os import name
from loggingSystem import loggingSystem
from processamentosqlite import ProcessamentoSqlite
from faker import Faker
from random import randint, random,uniform,choice
from sqlite3 import Error as sqliteError
from sqlite3 import OperationalError as sqliteOperationalError
import sys,re,sqlite3,json,logging
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

        def tratamento_input(self,valor,adicional:str=""):
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
                self.message+=self.listagem_valores_possiveis(valores_possiveis=self.valor_possivel)
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

        # def valores_possiveis(self,valores_possiveis=""):
        #     print(valores_possiveis)
        #     retorno=super(GeradorDeSql.TamanhoArrayErrado, self).valores_possiveis(valores_possiveis)
        #     return retorno

        # def listagem_valores_possiveis(self,valores_possiveis="",campo=""):
        #     return super(GeradorDeSql.TamanhoArrayErrado, self).listagem_valores_possiveis(valores_possiveis=valores_possiveis,campo=campo)

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

        # def valores_possiveis(self,valores_possiveis=""):
        #     return super(GeradorDeSql.TipoDeDadoIncompativel, self).valores_possiveis(valores_possiveis=valores_possiveis)

        # def listagem_valores_possiveis(self,valores_possiveis="",campo=""):
        #     return super(GeradorDeSql.TipoDeDadoIncompativel, self).listagem_valores_possiveis(valores_possiveis=valores_possiveis,campo=campo)

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
    def __init__(self,sqlite_db="./initial_db.db",sql_file_pattern="./sqlitePattern.sql", log_file="./geradorSQL.log",level:int=10,logging_pattern='%(name)s - %(levelname)s - %(message)s',logstash_data:dict={}):
        """
        classe para gerenciar arquivos csv
        :param loggin_name: nome do log que foi definido para a classe,altere apenas em caso seja necessário criar multiplas insstancias da função
        :param log_file: nome do arquivo de log que foi definido para a classe,altere apenas em caso seja necessário criar multiplas insstancias da função
        """

        self.logging = loggingSystem(name="gerador sql",arquivo=log_file,level=level,format=logging_pattern,logstash_data=logstash_data)
        #self.create_temporary_DB(local=sqlite_db,pattern=sql_file_pattern)
        self.processamento_sqlite=InteracaoSqlite(sqlite_db=sqlite_db,sql_file_pattern=sql_file_pattern,log_file=log_file,logging_pattern=logging_pattern,level=level,logstash_data=logstash_data)
        self.conn = sqlite3.connect(sqlite_db)
        logging.getLogger('faker').setLevel(logging.ERROR)
        #self.logging = self.logging.logger.getLogger("gerador sql")

#relacionado com o processamento/geração de dados
    def create_insert(self,table:str,pattern:dict,select_country:str="random",id:int=-1) -> dict:
        """cria um novo dado para ser inserido no sqlite ou ser usado em outras partes do codigo

        Args:
            table (str): nome da tabela do sql que o dado será inserido
            pattern (dict): padrão que será usado pelo gerador seguindo o padrão descrtito no json,esses padrões serão descritos a parte
            select_country (str, optional): pais do qual o padrão do faker será usado. Defaults to "random".
            id (int, optional): id do dado gerado no banco de dados,se preenchido ele será o definido,caso contrário ele será o próximo possivel no bd de acordo com os registros do sqlite. Defaults to -1.

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
        self.logging.info("create_data")
        try:
            if select_country=="random":
                fake = Faker()
                random_locale=fake.locale()
                self.logging.info(random_locale)
                fake = Faker(random_locale)#define o faker para seguir o padrão de um pais expecifico selecionado aleatoriamente dentre os disponiveis
            else:
                fake = Faker(select_country)#se for definido então o codigo usado será o do pais inserido
            dados_gerados={"nomeBD":table,"tipoOperacao":1,"dados":{},"adicionais":{}}
            if id == -1:
                id=self.processamento_sqlite.buscar_ultimo_id_cadastrado(table)+1
            dados_gerados["idNoBD"]=id
            for dado in pattern.keys():
                self.logging.debug(dado)
                if pattern[dado][0] == "nomeCompleto":
                    '''supoe-se que qualquer pessoa pode ter nascido em qq lugar e morar em qualquer outro lugar,nomes são dados pelo gerador de qualquer idioma,por isso nao foi definido um pais para a geracao'''
                    dados_gerados["dados"][dado]=fake.name()
                elif pattern[dado][0] == "primeiroNome":
                    dados_gerados["dados"][dado]=fake.first_name()
                elif pattern[dado][0] == "sobrenome":
                    dados_gerados["dados"][dado]=fake.last_name()
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
                        dados_gerados["dados"][dado]=fake.date_between(end_date=end_date).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        dados_gerados["dados"][dado]=fake.date_between_dates(start_date=start_date,end_date=end_date).strftime('%Y-%m-%d %H:%M:%S')
                elif pattern[dado][0] == "pais":
                    dados_gerados["dados"][dado]=fake.current_country()
                elif pattern[dado][0] == "cidade":
                    dados_gerados["dados"][dado]=fake.city()
                elif pattern[dado][0] == "endereco":
                    dados_gerados["dados"][dado]=fake.street_address()
                elif pattern[dado][0] == "cep":
                    dados_gerados["dados"][dado]=fake.postcode()
                elif pattern[dado][0] == "telefone":
                    if fake.boolean():
                        dados_gerados["dados"][dado]=fake.phone_number()
                    else:
                        try:
                            dados_gerados["dados"][dado]=fake.cellphone_number()
                        except:
                            dados_gerados["dados"][dado]=fake.phone_number()
                elif pattern[dado][0] == "nomeCategoria":
                    dados_gerados["dados"][dado]=fake.word()
                elif pattern[dado][0] == "email":
                    dados_gerados["dados"][dado]=fake.email()
                elif pattern[dado][0] == "usuario":
                    dados_gerados["dados"][dado]=fake.profile(fields=["username"])["username"]
                elif pattern[dado][0] == "senha":
                    dados_gerados["dados"][dado]=fake.password(length=fake.random_int(min=8,max=32))
                elif pattern[dado][0] == "boleano":
                    dados_gerados["dados"][dado]=fake.boolean()
                elif pattern[dado][0] == "idioma":
                    dados_gerados["dados"][dado]=fake.locale()
                elif pattern[dado][0] == "titulo":
                    dados_gerados["dados"][dado]=fake.sentence(nb_words=fake.random_int(min=1,max=10))
                elif pattern[dado][0] == "textoLongo":
                    dados_gerados["dados"][dado]=fake.paragraphs(nb=fake.random_int(min=1,max=2))
                elif pattern[dado][0] == "nota":
                    dados_gerados["dados"][dado]=uniform(0.0,10.0)
                elif pattern[dado][0] == "ano":
                    dados_gerados["dados"][dado]=fake.date(pattern='%Y')
                elif pattern[dado][0] == "duracaoDias":
                    dados_gerados["dados"][dado]=fake.random_int(min=1,max=10)
                elif pattern[dado][0] =="datetime":
                    dados_gerados["dados"][dado]=fake.date_time().strftime('%Y-%m-%d')
                elif pattern[dado][0] == "duracaoHoras":
                    dados_gerados["dados"][dado]=uniform(0.0,4.0)
                elif pattern[dado][0] == "naLista":
                    if not all(isinstance(n, str) for n in list(pattern[dado][0])):
                        raise self.TipoDeDadoIncompativel(pattern[dado][1],tipo_possivel="string",campo="variaveis adicionais da variavel naLista")
                    dados_gerados["dados"][dado]=fake.word(ext_word_list=pattern[dado][1:] )
                elif pattern[dado][0] == "valorPago":
                    dados_gerados["dados"][dado]=uniform(0.0,50.0)
                elif pattern[dado][0] == "associacao":
                    '''
                    parametros obrigatórios são nome da tabela e se random ou se definido
                    '''
                    if len(pattern[dado])<2:
                        raise self.TamanhoArrayErrado(valor_possivel=2,valor_inserido=len(pattern[dado]),campo="associacao")
                    if type(pattern[dado][1]) != type(""):
                        raise self.TipoDeDadoIncompativel(valor_inserido=pattern[dado][1],tipo_possivel=["string","array"],campo="associacao")
                    if pattern[dado][1]!="random":
                        dados_gerados["dados"][dado]=pattern[dado][1]
                    else:
                        total_cadastrado=self.processamento_sqlite.buscar_ultimo_id_cadastrado(pattern[dado][1])
                        if total_cadastrado>1:
                            dados_gerados["dados"][dado]=fake.random_int(min=1,max=self.processamento_sqlite.buscar_ultimo_id_cadastrado(pattern[dado][1]))
                        else:
                            dados_gerados["dados"][dado]=1
                elif pattern[dado][0] == "id":
                    dados_gerados["dados"][dado]=id
            return dados_gerados
        except self.TamanhoArrayErrado as e :
            self.logging.error(e)
        except self.ValorInvalido as e:
            self.logging.error(e)
        except self.TipoDeDadoIncompativel as e:
            self.logging.error(e)
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])

    def create_select(self,table:str,pattern:dict,select_country:str="random",id:int=-1,filtro:list=[],values:dict={}) -> dict:
        
        """função gera um dictionary variante do de create_data que contem os dados equivalentes ao comando de pesquisa para o sqlite

        Args:
            table (str): nome da tabela do sql que o dado será inserido
            pattern (dict): padrão que será usado pelo gerador seguindo o padrão descrtito no json,esses padrões serão descritos a parte
            select_country (str, optional): pais do qual o padrão do faker será usado. Defaults to "random".
            id (int, optional): id do dado gerado no banco de dados,se preenchido ele será o definido,caso contrário ele será o próximo possivel no bd de acordo com os registros do sqlite. Defaults to -1.
            filtro (list or str, optional): equivalente a coluna adicional do dado pesquisado,se for igual a "*" irá retornar todos. Defaults to [].

        Returns:
            dict: dados gerados usando faker para corresponder ao padrão necessário de uma pesquisa no bd
        """
        self.logging.info("create_select")
        pattern=pattern.copy()
        # if filtro==[]:
        filtro_=self.gerador_filtro(pattern)
        # elif filtro=="*":
        #     filtro=list(pattern.keys())
        self.logging.debug(filtro_)
        for i in filtro_:
            pattern.pop(i)
        
        created_data=self.create_insert(table=table,pattern=pattern,select_country=select_country,id=id)

        if values!={}:
            created_data["dados"]=values
        if filtro == "*":
            created_data["tipoOperacao"]=3
            created_data["adicionais"]=[]
        else:
            created_data["tipoOperacao"]=4
            created_data["adicionais"]=filtro_
        self.logging.debug(created_data)
        return created_data

    def create_update(self,table:str,pattern:dict,filtro:list=[],select_country:str="random",id:int=-1,values:dict={}) -> dict:
        """cria um novo dado para ser inserido no sqlite para a operação de update

        Args:
            table (str): nome da tabela do sql que o dado será inserido
            pattern (dict): padrão que será usado pelo gerador seguindo o padrão descrtito no json,esses padrões serão descritos a parte
            id (int, optional): id do dado gerado no banco de dados,se preenchido ele será o definido,caso contrário ele será o próximo possivel no bd de acordo com os registros do sqlite. Defaults to -1.
            filtro (list, optional): array com os nomes da colunas que não serão alterados. Defaults to [].
            select_country (str, optional): pais do qual o padrão do faker será usado. Defaults to "random".

        Returns:
            dict: dados gerados usando faker para corresponder ao padrão da operação de update
        """
        self.logging.info("create_update")
        try:
            novos_dados=self.create_select(table=table,pattern=pattern,select_country=select_country,id=id,filtro=filtro,values=values)
            self.logging.debug(novos_dados)
            dados_substitutos={}
            for i in pattern.keys():
                if i in novos_dados["adicionais"] and ("id" not in pattern[i]):
                    dados_substitutos[i]=pattern[i]
            self.logging.debug(dados_substitutos)
            novos_dados["adicionais"]=self.create_insert(table=table,pattern=dados_substitutos,select_country=select_country,id=id)["dados"]
            novos_dados["tipoOperacao"]=5
            return novos_dados
        except self.TamanhoArrayErrado as e :
            self.logging.error(e)
        except self.ValorInvalido as e:
            self.logging.error(e)
        except self.TipoDeDadoIncompativel as e:
            self.logging.error(e)
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])

    def create_delete(self,table:str,pattern:dict={},select_country:str="random",id:int=-1,values:dict={},filtro:list=[]) -> dict:
        self.logging.info("create_delete")
        try:
            novos_dados=self.create_select(table=table,pattern=pattern,select_country=select_country,id=id,filtro=filtro,values=values)
            self.logging.debug(novos_dados)
            novos_dados["tipoOperacao"]=6
            novos_dados["adicionais"]=[]
            return novos_dados
        except self.TamanhoArrayErrado as e :
            self.logging.error(e)
        except self.ValorInvalido as e:
            self.logging.error(e)
        except self.TipoDeDadoIncompativel as e:
            self.logging.error(e)
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])

    def gerador_filtro(self,pattern:dict,ignorar:list=[]) -> array:
        retorno=[]
        pattern=pattern.copy()
        for i in ignorar:
            pattern.pop(i)
        total_elementos=len(list(pattern.keys()))
        intervalo=randint(1,total_elementos)
        while intervalo>=total_elementos:
            intervalo=randint(1,total_elementos)
        for i in range(0,intervalo):
            tmp=choice(list(pattern.keys()))
            while (tmp in retorno):
                tmp=choice(list(pattern.keys()))
            pattern.pop(tmp)
            retorno.append(tmp)
        return retorno

#relacionado com a geração do sql final
    def generate_SQL_command_from_data(self,data:dict,nome_coluna_id:str="id"):
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
        command=""
        try:
            if data["tipoOperacao"]==1:#insercao
                command+="INSERT INTO "
            elif data["tipoOperacao"]==2:#leitura completa
                command+="SELECT * FROM "
            elif data["tipoOperacao"]==3:#busca
                command+="SELECT * FROM"
            elif data["tipoOperacao"]==4:#busca filtrada
                command+="SELECT ("
                for i in data['adicionais']:
                    command+= str(i["variavelRetornada"])+ ","
                if (data["idNoBD"]!=-1) and ("idNoBD" in data):
                    command+=nome_coluna_id
                command+=") FROM "
            elif data["tipoOperacao"]==5:#edicao
                command+=" UPDATE "
            elif data["tipoOperacao"]==6:#delecao
                command+="DELETE FROM "
            else:
                raise self.ValorInvalido(valor_inserido=data["tipoOperacao"])

            command+=str(data["nomeBD"])

            if data["tipoOperacao"]==1:#insercao
                command+="("
                for coluna in data["dados"].keys():
                    if type(data[coluna])==type("") or type(data[coluna])==type({}) or  type(data[coluna])==type([])  :
                        command+='"'+data[coluna].replace("\n","")+'"'
                    else:
                        command+=str(data[coluna])
                    if coluna != data["dados"].keys()[-1]:
                        command+=","
                command+=") VALUES ("
                for coluna in data["dados"].keys():
                    if type(data[coluna])==type("") or type(data[coluna])==type({}) or  type(data[coluna])==type([])  :
                        command+='"'+data[coluna].replace("\n","")+'"'
                    else:
                        command+=str(data[coluna])
                    if coluna != data["dados"].keys()[-1]:
                        command+=","
                command+=");"
            elif data["tipoOperacao"]==2:#leitura completa
                command+="; "
            elif data["tipoOperacao"] in [3,4,6]:# busca #busca filtrada #remocao
                command+=" WHERE "
                for coluna in data["dados"].keys():
                    command+=str(coluna) + " IS "+str(data["dados"][coluna])
                    if coluna != data["dados"].keys()[-1]:
                        command+=" AND "
                if (data["idNoBD"]!=-1) and ("idNoBD" in data):
                    if len(data["dados"].keys())>0:
                        command+=" AND "
                    command+=nome_coluna_id+" IS "+data["idNoBD"]
                command+=";"
            elif data["tipoOperacao"]==5:#edicao
                command+=" SET "
                for coluna in data["dados"].keys():
                    command+=str(coluna) + " = "+str(data["dados"][coluna])
                    if coluna != data["dados"].keys()[-1]:
                        command+=" , "
                command+=" WHERE "
                for coluna in data["adicionais"].keys():
                    command+=str(coluna) + " IS "+str(data["adicionais"][coluna])
                    if coluna != data["adicionais"].keys()[-1]:
                        command+=" AND "
                if (data["idNoBD"]!=-1) and ("idNoBD" in data):
                    if len(data["dados"].keys())>0:
                        command+=" AND "
                    command+=nome_coluna_id+" IS "+data["idNoBD"]
                command+=";"
        except sqliteOperationalError as e:
            print("erro operacional no sqlite")
            self.logging.error(e)
            quit()
        except sqliteError as e:
            print("erro desconhecido no sqlite")
            self.logging.error(e)
        except self.ValorInvalido as e :
            self.logging.error(e)
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])

        return command

    def gerar_dado_insercao(self,table,pattern:dict,select_country:str="random",id:int=-1):
        self.logging.info("gerando dados de insercao e inserindo em sqlite")
        data=self.create_insert(table=table,pattern=pattern,select_country=select_country,id=id)
        self.logging.debug(data)
        self.processamento_sqlite.insert_data_sqlite(data=data,table=table)
        self.processamento_sqlite.add_contador_sqlite(table=table)

    def gerar_dado_busca(self,table:str,pattern:dict,dado_existente:bool=False,id:int=-1,select_country:str="random",filtro:list=[],not_define_id=False):
        self.logging.info("gerando dados de busca e inserindo em sqlite")
        #table,id:int=-1,dados_pesquisados:dict={},filtro=[]
        if id == -1 and dado_existente:
            id=self.processamento_sqlite.random_id_cadastrado(table=table)

        dados_pesquisados=self.create_select(table=table,pattern=pattern,select_country=select_country,id=id)

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
            data=self.create_select(table=table,values=dados_pesquisados["dados"],filtro=filtro,pattern=pattern,select_country=select_country)
        else:
            data=self.create_select(table=table,values=dados_pesquisados["dados"],id=id,filtro=filtro,pattern=pattern,select_country=select_country)
        if all_filter:
            data["tipoOperacao"]=3
        self.logging.debug(data)
        self.processamento_sqlite.insert_data_sqlite(data,table=table)

    def gerar_dado_delecao(self,table:str,pattern:dict,dado_existente:bool=False,id:int=-1,select_country:str="random",not_define_id=False):
        self.logging.info("gerando dados de delecao e inserindo em sqlite")
        values={}
        if id == -1 and dado_existente:
            id=self.processamento_sqlite.random_id_cadastrado(table=table)
            dados_adiquiridos = self.processamento_sqlite.read_operacoes(filtro={"idNoBD":id,"nomeBD":table,"tipoOperacao":1})
            self.logging.debug(dados_adiquiridos[0])
            values = dados_adiquiridos[0]["dados"]
        if not_define_id:
            data=self.create_delete(table=table,pattern=pattern,select_country=select_country,values=values)
        else:
            data=self.create_delete(table=table,pattern=pattern,select_country=select_country,id=id,values=values)
        self.logging.debug(data)
        self.processamento_sqlite.insert_data_sqlite(data,table=table)

    def gerar_dado_leitura_completa(self,table:str,pattern:dict,filtro:list=[],select_country:str="random"):
        self.logging.info("gerando dados de leitura e inserindo em sqlite")

        data=self.create_select(table=table,filtro=filtro,select_country=select_country,pattern=pattern)
        self.logging.debug(data)
        self.processamento_sqlite.insert_data_sqlite(data,table=table)

    def gerar_dado_atualizacao(self,table:str,pattern:dict,dado_existente:bool=False,id:int=-1,select_country:str="random",not_define_id=False):
        self.logging.info("gerando dados de atualizacao e inserindo em sqlite")


    def gerar_dados_por_json(self,json_file,tipo:int=1,select_country:str="random",table:str="random",quantidade="random",dado_existente:bool=False):
        self.logging.info("gerando dados por json")
        def random_bool():
                    return choice([True, False])
        try:
            file=open(json_file)
            json_loaded=json.loads(file.read())
            if table == "random":
                table=random.choice(json_loaded.keys())
            if quantidade == "random":
                quantidade=randint(0, 20)
            for i in range(0,quantidade):
                
                if tipo==0:
                    tipo_execucao=randint(1,6)
                else:
                    tipo_execucao=tipo
                self.logging.info("table="+table+", pattern="+str(json_loaded[table])+", select_country="+select_country)
                filtro=self.gerador_filtro(pattern=json_loaded[table])
                if tipo_execucao == 1:#criacao
                    self.gerar_dado_insercao(table=table,pattern=json_loaded[table],select_country=select_country)
                elif tipo_execucao == 2:#leitura completa
                    self.gerar_dado_leitura_completa(table=table,filtro=filtro)
                elif tipo_execucao == 3:#busca
                    self.gerar_dado_busca(table=table,pattern=json_loaded[table],select_country=select_country,id=self.processamento_sqlite.random_id_cadastrado(table=table),filtro="*",dado_existente=dado_existente,not_define_id=random_bool())
                elif tipo_execucao ==4:#busca filtrada
                    self.gerar_dado_busca(table=table,pattern=json_loaded[table],select_country=select_country,id=self.processamento_sqlite.random_id_cadastrado(table=table),filtro=filtro,not_define_id=random_bool())
                elif tipo_execucao == 5:#edicao
                    #edicao
                    pass
                elif tipo_execucao == 6:#delecao
                    self.gerar_dado_delecao(table=table,pattern=json_loaded[table],dado_existente=dado_existente,select_country=select_country,not_define_id=random_bool())
                else:
                    raise self.ValorInvalido(campo="tipo",valor_inserido=tipo,valor_possivel="de 1 a 6")
        except self.TamanhoArrayErrado as e :
            self.logging.error(e)
        except self.ValorInvalido as e:
            self.logging.error(e)
        except self.TipoDeDadoIncompativel as e:
            self.logging.error(e)
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])
    
    def gerar_todos_dados_por_json(self,json_file,tipo:int=1,select_country:str="random",quantidade="random"):
        self.logging.info("gerando multiplos dados sqlite")
        if quantidade == "random":
            quantidade=randint(0, 20)
        file=open(json_file)
        json_loaded=json.loads(file.read())
        self.logging.debug(json_loaded)
        for table in json_loaded.keys():
            self.gerar_dados_por_json(json_file,select_country=select_country,table=table,quantidade=quantidade,tipo=tipo)

class InteracaoSqlite(ProcessamentoSqlite):
    def __init__(self,sqlite_db="./initial_db.db",sql_file_pattern="./sqlitePattern.sql", log_file="./geradorSQL.log",level:int=10,logging_pattern='%(name)s - %(levelname)s - %(message)s',logstash_data:dict={}):
        """
        classe para gerenciar arquivos csv
        :param loggin_name: nome do log que foi definido para a classe,altere apenas em caso seja necessário criar multiplas insstancias da função
        :param log_file: nome do arquivo de log que foi definido para a classe,altere apenas em caso seja necessário criar multiplas insstancias da função
        """
        
        super().__init__(sqlite_db=sqlite_db,sql_file_pattern=sql_file_pattern,log_file=log_file,logging_pattern=logging_pattern,level=level,log_name="gerador sql interacao sqlite",logstash_data=logstash_data)
        #self.create_temporary_DB(local=sqlite_db,pattern=sql_file_pattern)
        

    def buscar_ultimo_id_cadastrado(self,table:str):
        self.logging.info("ultimo id cadastrado")
        filtro={"nomeBD":table}
        query=["numeroDDadosCadastrados"]
        self.certify_if_contador_exists(table)
        retorno=self.read_data_sqlite("contadores",filtro,query)
        return int(retorno[0][0])

    def random_id_cadastrado(self,table:str) -> int:
        self.logging.info("selecionando id aleatorio")
        tmp=self.buscar_ultimo_id_cadastrado(table=table)
        tmp2=randint(1,tmp)
        self.logging.debug(str(tmp)+"  "+str(tmp2))
        return tmp2

    def add_contador_sqlite(self,table:str):
        self.logging.info("insercao contador sqlite")
        try:
            cursor = self.conn.cursor()
            self.certify_if_contador_exists(table)
            cursor.execute("UPDATE contadores SET numeroDDadosCadastrados = numeroDDadosCadastrados+1 WHERE nomeBD='"+table+"';")
            self.conn.commit()
        except sqliteOperationalError as e:
            print("erro operacional no sqlite")
            self.logging.error(e)
            quit()
        except sqliteError as e:
            print("erro desconhecido no sqlite")
            self.logging.error(e)
        except :
            self.logging.error("Unexpected error:", sys.exc_info()[0])

    def certify_if_contador_exists(self,table:str):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM contadores WHERE nomeBD is '"+table+"';")
        listagem=cursor.fetchall() 
        if listagem == []:
            cursor.execute("INSERT INTO contadores(nomeBD,numeroDDadosCadastrados) VALUES ('"+table+"',0);")

    def read_contadores(self,filtro:dict={},query="*"):
        self.logging.info("lendo sqlite contadores")
        return self.read_data_sqlite("contadores",filtro=filtro,query=query)

    def read_operacoes(self,filtro:dict={},query="*"):
        self.logging.info("lendo sqlite operacoes")
        tmp=self.read_data_sqlite("operacoes",filtro=filtro,query=query)
        self.logging.debug(tmp)
        retorno=[]
        for i in tmp:
            tmp2=self.process_data_generated(data=i,with_id=True)
            tmp2.pop("id")
            retorno.append(tmp2)
        return retorno

    def process_data_generated(self,data:list,tipo_adicional:str="dict",with_id:bool=False) -> dict:
        """processa o dado lido do sqlite para um formato de dict usavel 

        Args:
            text (str): texto gerado pelo comando de leitura do sqlite

        Returns:
            dict: dict usavel e processado do que foi lido do sqlite
        """        
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
        if not is_dict and patter_externo==r"\{(.*)\}" and pattern_interno==r"([^:]*)\:(.*)":
            patter_externo=r"\[(.*)\]"
            pattern_interno=r"(.*)"
        pattern_etapa1=patter_externo
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
                self.logging.debug(re.findall(pattern_dados_etapa2,dado))
                etapa2_dados=re.findall(pattern_dados_etapa2,dado)
                if etapa2_dados==[]:
                    break
                else:
                    etapa2_dados=etapa2_dados[0]
                if external_header_list == []:
                    dados[etapa2_dados[0].replace("'","").replace('"',"")]=etapa2_dados[1].replace("'","").replace('"',"")
                else:
                    dados[external_header_list[tmp]]=etapa2_dados[0]
                    tmp+=1
        else:
            for dado in etapa1_dados:
                etapa2_dados=re.findall(pattern_dados_etapa2,dado)[0]
                dados[tmp]=etapa2_dados[0]
                tmp+=1
        self.logging.debug(dados)
        return dados