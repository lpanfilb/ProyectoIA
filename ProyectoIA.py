import networkx as nx #tratamiento de grafos
import pandas as pd #hay que instalar pandas y openpyxl
import matplotlib.pyplot as plt #para representar los grafos        

Heur = pd.read_excel('Datos/datos.xlsx', 'HEURISTICA',header= 0,  index_col=0)
Dist = pd.read_excel('Datos/datos.xlsx', 'DISTANCIAS', index_col=0)

G = nx.from_pandas_adjacency(Dist, create_using=nx.Graph()) #Creacion del grafo de distancias
nx.set_node_attributes(G, {"Coste": 0, "Heuristica": 0 , "Padre" : ""})


nodosAbiertos = []
nodosCerrados = []
path = []


def caminoMasCorto(inicial, final):
    nx.set_node_attributes(G, {inicial: {"Coste": 0, "Heuristica": CheckHeur(inicial,final), "Padre" : inicial}})                        #añado al primero su heuristica
    caminoMasCortoRec(inicial, final)#lo mando de forma recursiva
    path.append(final)
    checkPath(final)                                                                                               #que compruebe el path
    print(path)

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
    
    if  Padre != final:
        path.append(Padre)
        checkPath(Padre)
    
    

caminoMasCorto('A Coruña','Barcelona')             
            


 #----COMPROBACIONES GRAFO-----
print(G)
# print([a for a in G.edges(data=True)])
pos = nx.circular_layout(G)  # Layout del grafo (puedes ajustarlo según tus preferencias)
colores_n = ['lime' if nodo in path else 'thistle' for nodo in G]
nx.draw(G, pos, with_labels = True, node_size = 500, node_color= colores_n, node_shape = "s", edge_color = 'thistle', width = 2, font_size = 10)
nx.draw(G, pos, node_size = 0, edgelist = list(zip(path,path[1:])), edge_color = 'lime', width = 4, font_size = 10)
plt.show()