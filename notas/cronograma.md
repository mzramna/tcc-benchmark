<h1>16/9</h1>
fazer sistema de interação com sqlite

* --ler dados registrados--
* --inserir dados--
* --interagir com o numero de linhas em cada tabela--

<h1>17/9</h1>
gerenciar geração de comandos para filtragem

* --criar metodo de se criar os parametros de filtro,basear no de dados novos--
* --verificar os tratamentos de erro--
* --realizar testes do q foi criado hj e ontem--
* --refatorar e reorganizar texto de planejamento de acordo com o que foi modificado--

<h1>18/9</h1>
gerar metodos de edição

* --criar metodo que usa o de criação e listagem filtrada para gerar o comando de edição--
* --gerar comando que verifica se foi editado corretamente--
* --realizar testes--


<h1>20/9</h1>
criar metodo de deleção,e listagem
 * --criar metodo de gerar dado de listagem geral--
 * --criar metodo de gerar dado de busca filtrada--
 * --criar metodo de gerar dado de deleção--

 <h1>21/9</h1>
 * --criar metodo de salvar os dados de listagem geral gerados no sql --
 * --criar metodo de salvar os dados de busca filtrada gerados no sql--
 * --criar metodo de salvar os dados de deleção gerados no sql--
 * --criar tratamento de log decente--
 
<h1>22/9</h1>
converter dados para padrão do dbbench

* ler documentação
* analizar mudanças necessarias
* ver se é possivel gerar os dados de alguma forma mais simplificada
* ver se é necessário a pré produção dos comandos sql ou se apenas um json ou csv com um comando base no dbdench
* anotar todas modificações possiveis

https://github.com/memsql/dbbench/blob/master/TUTORIAL.md#running-queries-from-a-file

arquivo de queries consiste de um csv de separação por virgula sendo a primeira coluna o tempo necessário de espera entre o ultimo comando e o comando dessa linha,esse tempo pode ser padronizado como 0,de forma a ser um disparo continuo de requisições,esse valor pode ser alterado caso ambos os servidores ou a maquina de execução do script não consiga aguentar a carga demandada.
no caso de apenas um dos servidores não aguentar isso deve ser anotado e na sequencia o valor deve ser alterado,é importante tanto a conclusão da lista de execuções quanto a não execução da mesma

dessa forma eles podem ser até ser executados em paralelo
