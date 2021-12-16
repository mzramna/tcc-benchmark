para gerar 200 valores os dados de tempo obtidos foram:
19.87244939804077
35.53090786933899
21.681770086288452
20.14069414138794
media geração completa 24.306455373764038
media por elemento 0.12153227686882019

apos isso foi implementado um teste aditivo que testará 30 ciclos com adição de 100 em 100 e cada ciclo terá um teste de 4 sub ciclos internos,isso para ver o quanto de tempo é gasto em média para casos com muitos ou poucos dados gerados,sendo assim podendo gerar um valor de base de valor minimo gasto obrigatóriamente para cada interação
os testes dessa vez foram modificados de forma a salvar os dados em um arquivo para consulta futura,que estão em anexo,os testes dessa vez foram realizados em um pc arm64 e um amd64,os dados resultaram em valores de tempo consistente em relação a diferença de frequencias das maquinas,sendo assim se existe um valor de perda entre as arquiteturas para esse teste é um valor irrisório,sendo que o pc amd64 apresentou testes cerca de 2 vezes mais rapidos e seu clock é aproximadamente o dobro do arm64,esses valores foram dados em relação ao tempo gasto por elemento em cada interação
