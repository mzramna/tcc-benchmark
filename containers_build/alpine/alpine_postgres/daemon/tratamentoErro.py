#tratamento de erro
class ValorInvalido(Exception):
    """classe de exceção customizada base,feita de forma a dar mensagem de erro base para a classe,
    essa mensagem de erro é genérica, e é usado para avisar se alguma variavel foi preenchida de forma que o algoritimo não aceita,
    essa mensagem de erro é altamente customizável
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
        self.valor_inserido=valor_inserido
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
        retorno=""
        if valores_possiveis !="":
            if  type("")==type(valores_possiveis):
                retorno+="o valor possivel "
                if campo!="":
                    retorno+="no campo "+str(campo)+" "
                retorno+="é "
            elif  type("")==type(valores_possiveis):
                retorno+=" os valores possiveis "
                if campo!="":
                    retorno+="no campo "+str(campo)+" "
                retorno+="são "+str(valores_possiveis)
            retorno+= self.valores_possiveis(valores_possiveis)
            return retorno

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
        super(TamanhoArrayErrado, self).__init__()
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
        
        #super(TamanhoArrayErrado, self).construir_mensagem(self.message)

    def __str__(self):
        return self.message

class TipoDeDadoIncompativel(ValorInvalido):
    def __init__(self,valor_inserido,tipo_possivel="",campo="") :
        super(TipoDeDadoIncompativel, self).__init__()
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
