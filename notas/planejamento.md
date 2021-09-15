<h1>sobre a forma de geração de dados</h1>
dados gerados devem ser armazenados em um sqlite de forma mais otimizada possivel,de forma que a leitura de disco da maquina que está rodando os testes influencia a velocidade dos testes,isso porque queremos ter um registro o mais preciso possivel para os dados gerados,de forma que sempre saibamos o que foi escrito e o que devia ter sido escrito.<br>
os dados gerados serão feitos com a biblioteca faker do python,que gera dados verossimeis ,visto que até mesmo a manipulação de dados genericos totalmente padronizados pode gerar uma diferença plausivel no benchmark para se gerar uma diferença do uso no mundo real
<h1>sobre as imagens dos bancos de dados</h1>
os bancos de dados tiveram containers docker criados da forma mais otimizada possivel,utilizando o alpine linux,um sistema operacional criado para ser leve e sem nenhum adicional rodando em segundo plano,ele foi pensado para ser usado como base de imagens docker.<br>
as imagens estão associadas em um arquivo docker-compose de forma que o build delas é feito na maquina que irá rodar,dessa forma sempre sera o mais otimizado possivel,visto que é apenas um sistema operacional sobre o kernel de outra maquina que já roda um sistema operacional,isso também faz com que as imagens não tenham de ser criadas para cada arquitetura ou para cada situação expecífica,de forma que o mesmo processo pode ser realizado em quaisquer arquiteturas que possam ser interessantes os testes no futuro,a unica limitação para isso é que o alpine linux e os bancos de dados testados existam para essas aquiteturas no seu repositório.
<h1>sobre o teste realizado</h1>
o teste realizado consiste em primariamente 4 etapas:<br>
 *geração de dados<br>
 * geração do script usado pelo dbbench <br>
 *execução dos testes<br>
 * analize dos logs e dados
 <h1>sobre o banco de dados</h1>
 o banco de dados testado simula o sistema de uma locadora de filmes,o banco de dados base foi retirado dos exemplos do mysql workbench e modificado para ficar mais simples e mais próximo do banco de dados equivalente em varios bancos de dados

<h1>sobre o script final gerado</h1>
script de teste do dbbench deve ser criado de forma que ele não faça todas as requisições ao mesmo tempo e sim apenas algumas ,depois uma parte das sequentes e posteriormente a proxima etapa até terminarem todas as requisições<br>
fazer alguma forma de que as requisições sejam feitas recorrentemente com as escritas,buscas edições e deleções sendo executadas simultaneamente em algum momento para que seja mais plausivel o uso do servidor<br>
no pior dos casos fazer um script python usando a biblioteca previamente criada para que ele gere os dados necessários de benchmark,mas evitar ao maximo fazer isso
<h1>sobre o tratamento de erros</h1>
foram criadas algumas classes para a notificação de erro de forma mais facil de se entender,essas classes lidam com variaveis com valor inválido,cada uma de uma forma<br>
a classe pai (Valor Inválido) define quando um valor é passado de forma que não DEVE ser aceita pelo programa,como passar um string ao invés de um array,ja que ambos podem funcionar em teoria dependendo do que foi passado,mas para o funcionamento do programa isso não pode ser aceito.
uma das classes filhas é para o tratamento de tamanho de array(tamanho array errado) passada para definir se o array de input para uma função foi passado com tamanho diferente do que deveria para o programa funcionar de forma correta,por exemplo,na função de geração de dados,na parte para gerar uma data podem ser aceitos varios padroes de tamanho de array,cada tamanho chama um intervalo para o qual a data será gerada,uma totalmente aleatória,uma que gera qualquer data anterior ao momento da execução do programa,podendo ser des de uma data expecífica até o dia de execução ou até um intervalo de tempo definido(por exemplo 30 anos antes),e a ultima forma é definindo o intervalo entre 2 datas passadas,sendo também da mesma forma que o anterior.por esse motivo a classe aceita no retorno de erro varios dados diferentes para serem passados como alerta de erro.
outra das classes filhas(tipo de dado incompatível) funciona para o mesmo propósito que a classe anterior,onde podem ser aceitos varios tipos de dados diferentes de input,se o tipo dele for incompativel,como por exemplo,o string de input não seguir o padrão necessário para o funcionamento,dando ainda o exemplo da geração de dados para uma data,ela pode aceitar 2 formas para a definição de um intervalo limite para a geração,os padrões são "dia/mes/ano","dia-mes-ano" ou "-30y"esse ultimo servindo como definidor de tempo anterior/posterior ao dia da execução,onde no exemplo é passado o intervalo de 30 anos antes do dia anterior,e nesse caso,se algum input for passado ,mas ele não for do padrão necessário ele irá executar um erro então
<h1>sobre a geração de dados padronizada</h1>
os dados são gerados sempre de forma padronizada pelo padrão passado como input da função,e esse padrão é passado como um dictionary,tipo do python semelhante a um json,ele funciona da seguinte forma:<br>

~~~ json
{
    "nome da coluna:["tipo de dado que sera gerado","parametro adicional 1"...],
}
~~~

os dados passados dessa forma simplificam a generalização de geração de dados fazendo com que o mesmo metodo de geração possa ser usado para varios tipos de tabelas diferentes e varios tipos de testes onde dados gerados podem ser gerados de forma aleatória para realização de testes,a função alem desse parametro possui ainda mais outros 3 ,um dizendo o nome da tabela onde será inserido ,um dizendo o id que sera atribuido ao dado gerado para o bd,que pode simplesmente ser passado em branco e então o sistema irá gerar esse dado de forma automática e um parametro para selecionar o pais para os quais os dados serão gerados,podendo ser aleatório ou definido pelo codigo de identificação de pais,esses dados não foram passados no dict,apenas para a simplificação do processamento do dict,visto que ele foi pensado para funcionar de uma forma bem simplificada para reduzir o máximo possivel o consumo de cpu,visto que essa função possui ordem de 25n+xn no pior caso,sendo x o numero de dados cadastrados para a tabela relacionada ao dado gerado que coincidam com o dado passado,o ideal é x ser 1,mas visto que é um programa para o teste de desempenho de um banco de dados,existe a possibilidade de se testar o que acontece em situações que o banco de dados não pode aceitar e no final apresentar um erro.<br>
o codigo de geração de pais funciona gerando nomes e valores compativeis com os reais de um pais de acordo com a biblioteca faker<br>
os tipos de dados gerados estão descritos a baixo assim como seus parametros adicionais para geração quando existirem:

* nomeCompleto: gera um nome de pessoa completo,o nome será gerado no idioma vigente do pais usado
* primeiroNome: gera um nome próprio,sem sobrenome,o nome será gerado no idioma vigente do pais usado
* sobrenome: gera um sobrenome,o nome será gerado no idioma vigente do pais usado
* timestamp: gera um timestamp de banco de dado,possui alguns parametros adicionais :

~~~
precisa obrigatoriamente de 1 parametro dizendo se vai ser tudo randomico ou se vai ter um intervalo,se tiver um intervalo devem ser passados mais 2 parametros,um inicial e um final , se o final for o valor "agora" então o valor final sera o timestamp de agora do sistema operacional

para gerar com mais precisão usar o 2 parametro como: "-30y",sendo: - > significando anterior , 30 > quanto tempo , y > escala de tempo(anos) ou usando o padrão Date("dia") onde o dia deve ser passado como "1999-02-02"

o 3 parametro deve ser passado como o 2,mas não se limita apenas ao token de tempo anterior,sendo possivel um intervalo do futuro
~~~

* pais: retorna o nome do pais ao qual o codigo foi usado,o nome será gerado em inglês
 *cidade: gera um nome de uma cidade do pais ao qual o codigo foi usado ,o nome será gerado no idioma vigente do pais usado
 *endereco: gera um endereço plausivel ou não do pais ao qual o codigo foi usado ,o endereço será gerado no padrão do idioma vigente do pais usado
 *cep: gera um cep ou codigo postal plausivel do pais ao qual o codigo foi usado ,o codigo será gerado no padrão do idioma vigente do pais usado,mas não necessáriamente é real
 *telefone: gera aleatoriamente um telefone fixo ou celular,caso haja distinção no pais ao qual o codigo foi usado ,o telefone será gerado no padrão do pais usado,mas não necessáriamente é real
 *nomeCategoria: gera aleatoriamente uma palavra do idioma do pais ao qual o codigo foi usado
 *email:gera um email plausivel
 *usuario: gera um usuario de site plausivel
 *senha: gera um conjunto de caracteres equivalente a uma senha com um tamanho variavel de 8 a 32 caracteres
 *boleano: gera um valor veradeiro ou falso
 *idioma:seleciona um dos idiomas possiveis do faker
 *titulo: gera uma frase contendo de 1 a 10 palavras no idioma do pais ao qual o codigo foi usado
 *textoLongo: gera um ou dois paragrafos com palavras no idioma do pais ao qual o codigo foi usado
 *nota: gera um valor float entre 0 e 10
 *duracaoDias:gera um valor int entre 0 e 10
 *duracaoHoras: gera um valor float entre 0 e 4
 *classificacao: seleciona aleatoriamente um desses valores: 'G','PG','PG-13','R','NC-17'
 *funcaoEspecial: seleciona aleatoriamente um desses valores: 'Trailers','Commentaries','Deleted Scenes','Behind the Scenes'
 *valorPago:gera um valor float entre 0 e 50
 *associacao": gera um id de associação possivel para uma tabela definida,o valor é qualquer id entre 0 e o ultimo inserido nessa tabela
