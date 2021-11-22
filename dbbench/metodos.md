criar o arquivo ini e dividir as varias etapas dele em jobs diferentes,utilizar um arquivo csv para tirar os dados de cada requisição de cada etapa
descobrir como transformar isso em recorrencias multiplas e descobrir como gerar os dados possiveis a partir do q foi inserido no csv
existe a possibilidade de executar um request apenas para pesar o servidor com quantos requests ao mesmo tempo que quiser e q a maquina onde o teste está rodando aguentar
os parametros de um csv são dados da seguinte forma:
cada coluna equivale a uma lacuna do request,cada linha equivale a um request,ele não vai misturar linhas e colunas,até onde foi entendido
"Note that the ? syntax for parameters is an artifact of the mysql driver -- if you are using another driver, you will have to use the parameter syntax for that driver. For example, the postgres driver uses the Postgres-native ordinal markers ($1, $2, etc)."
existem metodos para se parar a execução de requests,pode ser por quantidade de execução ou por quantidade de tempo,o tempo pode ser definido de duas formas.
esse parametro pode ser util ja que pode-se utilizar o mesmo csv para todos os testes de uma mesma tabela,e incluir no meio testes que obrigatoriamente resultarão em erros,para entre outras coisas avaliar como o tempo é afetado em casos de erros
pode ser gerado um arquivo de log de querie para cada execução,apos isso esses arquivos seriam enviados para o ELK para melhorar a análize e visualização
"The file consists of an offest in microseconds (NOT milliseconds) and a query per line separated by a comma:

0,select count(*) from test_table
500,insert into test_table values (1)
2000,select count(*) from test_table"
como lidar com erros:
https://github.com/memsql/dbbench/blob/master/TUTORIAL.md#error-handling
é um pouco complexo e deve ser analizado como lidar ja que o padrão é terminar o job caso um erro ocorra

para lidar com execuções multiplas de queries existem 2 metodos:
concorrencia e taxa de execução,onde um limita quantos podem ocorrem por vez no máximo e o outro fala quantas execuções vão ser feitas por vez,onde o segundo também pode ser limitado por um parametro adicional

deve ser criado um script python para controlar o dbbench para que TUDO RELACIONADO seja padronizado e todos os dados possiveis sejam salvos em log para depois serem analizados pelo ELK
