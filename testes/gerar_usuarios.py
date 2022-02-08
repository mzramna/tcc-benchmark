import json
from random import choice
import string
from os import DirEntry
def gerador_usuarios(arquivo:DirEntry,quantidade:int,tamanho:int=10):
    valores = string.ascii_lowercase + string.digits
    usuarios_cadastrados=json.loads(open(arquivo).read())
    for q in range(quantidade+1):
        if q<len(usuarios_cadastrados.keys()):
            pass
        else:
            tmp={"usuario":"","senha":""}
            for j in ["usuario","senha"]:
                gerado = ''
                for i in range(tamanho):
                    gerado += choice(valores)
                tmp[j]=gerado
            usuarios_cadastrados["usuario"+str(q)]=tmp
    json.dump(usuarios_cadastrados,open(arquivo,"w"))
            
            
print(len(json.loads(open("scripts/usuarios.json").read()).keys()))
gerador_usuarios("scripts/usuarios.json",20)
print(len(json.loads(open("scripts/usuarios.json").read()).keys()))