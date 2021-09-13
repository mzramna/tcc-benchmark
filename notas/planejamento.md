<h1>sobre a forma de geração de dados</h1>
dados gerados devem ser armazenados em um sqlite de forma mais otimizada possivel,de forma que a leitura de disco da maquina que está rodando os testes influencia a velocidade dos testes,isso porque queremos ter um registro o mais preciso possivel para os dados gerados,de forma que sempre saibamos o que foi escrito e o que devia ter sido escrito.<br>
os dados gerados serão feitos com a biblioteca faker do python,que gera dados verossimeis ,visto que até mesmo a manipulação de dados genericos totalmente padronizados pode gerar uma diferença plausivel no benchmark para se gerar uma diferença do uso no mundo real
<h1>sobre as imagens dos bancos de dados</h1>
os bancos de dados tiveram containers docker criados da forma mais otimizada possivel,utilizando o alpine linux,um sistema operacional criado para ser leve e sem nenhum adicional rodando em segundo plano,ele foi pensado para ser usado como base de imagens docker.<br>
as imagens estão associadas em um arquivo docker-compose de forma que o build delas é feito na maquina que irá rodar,dessa forma sempre sera o mais otimizado possivel,visto que é apenas um sistema operacional sobre o kernel de outra maquina que já roda um sistema operacional,isso também faz com que as imagens não tenham de ser criadas para cada arquitetura ou para cada situação expecífica,de forma que o mesmo processo pode ser realizado em quaisquer arquiteturas que possam ser interessantes os testes no futuro,a unica limitação para isso é que o alpine linux e os bancos de dados testados existam para essas aquiteturas no seu repositório.
<h1>sobre o teste realizado</h1>
o teste realizado consiste em primariamente 4 etapas:<br>
 - geração de dados<br>
 - geração do script usado pelo dbbench <br>
 - execução dos testes<br>
 - analize dos logs e dados
 <h1>sobre o banco de dados</h1>
 o banco de dados testado simula o sistema de uma locadora de filmes,o banco de dados base foi retirado dos exemplos do mysql workbench e modificado para ficar mais simples e mais próximo do banco de dados equivalente em varios bancos de dados

<h1>sobre o script final gerado</h1>
script de teste do dbbench deve ser criado de forma que ele não faça todas as requisições ao mesmo tempo e sim apenas algumas ,depois uma parte das sequentes e posteriormente a proxima etapa até terminarem todas as requisições<br>
fazer alguma forma de que as requisições sejam feitas recorrentemente com as escritas,buscas edições e deleções sendo executadas simultaneamente em algum momento para que seja mais plausivel o uso do servidor<br>
no pior dos casos fazer um script python usando a biblioteca previamente criada para que ele gere os dados necessários de benchmark,mas evitar ao maximo fazer isso