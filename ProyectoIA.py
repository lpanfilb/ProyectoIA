import networkx as nx #tratamiento de grafos
import pandas as pd #hay que instalar pandas y openpyxl
import matplotlib.pyplot as plt #para representar los grafos        

Heur = pd.read_excel('Datos/datos.xlsx', 'HEURISTICA',header= 0,  index_col=0)
Dist = pd.read_excel('Datos/datos.xlsx', 'DISTANCIAS', index_col=0)

G = nx.from_pandas_adjacency(Dist, create_using=nx.Graph()) #Creacion del grafo de distancias
nx.set_node_attributes(G, {"Coste": 0, "Heuristica": 0 , "Padre" : ""})

#------------FALTA-------------
#retraso por horas puntas
#¿coste transbordos?
#¿opcion elegir con menos transbordos?

nodosAbiertos = []
nodosCerrados = []
path = []
pathWeight = []


def caminoMasCorto(inicial, final):
    nx.set_node_attributes(G, {inicial: {"Coste": 0, "Heuristica": CheckHeur(inicial,final), "Padre" : inicial}})                        #añado al primero su heuristica
    caminoMasCortoRec(inicial, final)#lo mando de forma recursiva
    path.append(final)
    checkPath(final)
    pathWeight.append(G.nodes[inicial].get("Heuristica"))#que compruebe el path
    print(path)
    print(pathWeight, "total = " , sum(pathWeight))

def caminoMasCortoRec(inicial, final):
    global nodosAbiertos
    for actual in nx.neighbors(G, inicial):
        if actual not in nodosCerrados:
            if actual not in nodosAbiertos:
                nodosAbiertos.append(actual)
        costeActual = G.nodes[inicial].get("Coste") + G.edges[inicial,actual].get("weight")
        # print(actual,costeActual)
        if G.nodes[actual].get("Coste") is None or G.nodes[actual].get("Coste") > costeActual:                                         #lo comparo por si ya tiene un camiino mas rapido                    
            nx.set_node_attributes(G, {actual: {"Coste": costeActual, "Heuristica": CheckHeur(actual, final), "Padre": inicial}})    #cambio los atributos si es necesario     
        nodosAbiertos = sorted(nodosAbiertos, key=lambda x: G.nodes[x]['Coste'])
        
    if len(nodosAbiertos) >0:       
        siguiente = nodosAbiertos.pop(0)
        nodosCerrados.append(siguiente)
        caminoMasCortoRec(siguiente, final)  
            
    
def CheckHeur(actual, final):
    return Heur.at[final,actual]                                                                        #que recorra el siguiente nodo
                                                                                 

def checkPath(final):
    Padre = G.nodes[final].get("Padre")
    Peso = G.nodes[final].get("Coste") + G.nodes[final].get("Heuristica") 
    if  Padre != final:
        path.append(Padre)
        pathWeight.append(Peso)
        checkPath(Padre)
    
def Main():
    ciudad1 = input(f"Escriba la parada de inicio: \n")
    while ciudad1 not in G.nodes:
        ciudad1 = input(f"Por favor repita la ciudad con el formato como en el ejemplo 'Madrid'\n")
        
    ciudad2 = input(f"Perfecto,comenzando desde {ciudad1}. Escriba la parada de destino\n")
    while ciudad2 not in G.nodes:
        ciudad2 = input(f"Por favor repita la ciudad con el formato como en el ejemplo 'Madrid'\n")  
    while True:
        Hora = input(f"A que hora desea ir desde {ciudad1} a {ciudad2}, Escriba la hora con el formato 13:25\n")
        if len(Hora.split(":")) == 2:
            horas, minutos = Hora.split(":")
            if horas.isdigit() and minutos.isdigit():
                horas = int(horas)
                minutos = int(minutos)
                if 0 <= horas <= 23 and 0 <= minutos <= 59:
                    break  
        print("Hora no válida. Asegúrate de introducir la hora en formato HH:MM y que los valores sean correctos.")

    Hora = (horas, minutos)
    Opcion = input(f"¿Quiere que la ruta tenga los menos transbordos posibles o que sea la mas rápida? teclee [Transbordos/Rapida]\n")
    
    while Opcion[0] != "T" and Opcion[0] != "t" and Opcion[0] != "r" and Opcion[0] != "R":
        Opcion = input(f"Por favor introduzcala con el formato 'Tansbordos'/ 'Rapida' / 'T' / 'R' / 't' / 'r' \n")
    if Opcion[0] == "T" or Opcion[0] == "t":
        Opcion = True
    else:
        Opcion = False
    caminoMasCorto(ciudad1,ciudad2)
        
Main()
             
            


 #----COMPROBACIONES GRAFO-----
print(G)
# print([a for a in G.edges(data=True)])
pos = nx.circular_layout(G)  # Layout del grafo (puedes ajustarlo según tus preferencias)
colores_n = ['lime' if nodo in path else 'thistle' for nodo in G]
nx.draw(G, pos, with_labels = True, node_size = 500, node_color= colores_n, node_shape = "s", edge_color = 'thistle', width = 2, font_size = 10)
nx.draw(G, pos, node_size = 0, edgelist = list(zip(path,path[1:])), edge_color = 'lime', width = 4, font_size = 10)
plt.show()