import networkx as nx #tratamiento de grafos
import pandas as pd #hay que instalar pandas y openpyxl
import matplotlib.pyplot as plt #para representar los grafos        

Heur = pd.read_excel('Datos/datos.xlsx', 'HEURISTICA',header= 0,  index_col=0)
Dist = pd.read_excel('Datos/datos.xlsx', 'DISTANCIAS', index_col=0)
Tran = pd.read_excel('Datos/datos.xlsx', 'TRANSBORDOS',header= 0,  index_col=0)
Hor = pd.read_excel('Datos/datos.xlsx', 'HORAS',header= 0,  index_col=0)

G = nx.from_pandas_adjacency(Dist, create_using=nx.Graph()) #Creacion del grafo de distancias
nx.set_node_attributes(G, {"Coste": 0, "Heuristica": 0 , "Padre" : ""})

#------------FALTA-------------
#¿coste transbordos?
#¿opcion elegir con menos transbordos?

nodosAbiertos = []
nodosCerrados = []
path = []
path2 = []
pathWeight = []
Hora = None
inicial = None
final = None

def caminoMasCorto():
    global inicial
    global final
    nx.set_node_attributes(G, {inicial: {"Coste": CheckHora(inicial), "Heuristica": CheckHeur(inicial), "Padre" : inicial}})                        #añado al primero su heuristica
    caminoMasCortoRec(inicial)#lo mando de forma recursiva
    path.append(final)
    path2.append(final)
    checkPath(final)
    pathWeight.append(G.nodes[inicial].get("Heuristica"))#que compruebe el path
    print(path2)
    print(pathWeight, "total = " , sum(pathWeight))

def caminoMasCortoRec(nuevo):
    global nodosAbiertos
    for actual in nx.neighbors(G, nuevo):

        if actual not in nodosCerrados:
            if actual not in nodosAbiertos:
                nodosAbiertos.append(actual)

        costeActual = G.nodes[nuevo].get("Coste") + G.edges[nuevo,actual].get("weight")

        if G.nodes[actual].get("Coste") is None or G.nodes[actual].get("Coste") > costeActual: 
                                                                                 
            nx.set_node_attributes(G, {actual: {"Coste": costeActual + CheckHora(actual) + CheckTran(nuevo, actual), "Heuristica": CheckHeur(actual), "Padre": nuevo}})    #cambio los atributos si es necesario     
        nodosAbiertos = sorted(nodosAbiertos, key=lambda x: G.nodes[x]['Coste'])
    if len(nodosAbiertos) >0:       
        siguiente = nodosAbiertos.pop(0)
        nodosCerrados.append(siguiente)
        caminoMasCortoRec(siguiente)  
            
    
def CheckHeur(actual):
    global final
    return Heur.at[final,actual]                                                                       

def CheckHora(actual):
    global Hora
    return Hor.at[Hora,actual]  

def CheckTran(actual, final):
    return Tran.at[final,actual]                                                                             

def checkPath(final):
    Padre = G.nodes[final].get("Padre")
    Peso = G.nodes[final].get("Coste") + CheckTran(final, Padre) + G.nodes[final].get("Heuristica") 
    if  Padre != final:
        if CheckTran(final,Padre) == 0:
            Padre2 = Padre 
        else:
            Padre2 = "Transbordo a " + Padre 
        path.append(Padre)
        path2.append(Padre2)
        pathWeight.append(Peso)
        checkPath(Padre)
    
def Main():
    global Hora
    global inicial
    global final
    inicial = input(f"Escriba la parada de inicio: \n")
    while inicial not in G.nodes:
        inicial = input(f"Por favor repita la ciudad con el formato como en el ejemplo 'Madrid'\n")
        
    final = input(f"Perfecto,comenzando desde {inicial}. Escriba la parada de destino\n")
    while final not in G.nodes:
        final = input(f"Por favor repita la ciudad con el formato como en el ejemplo 'Madrid'\n")  
    while True:
        Hora = input(f"A que hora desea ir desde {inicial} a {final}, Escriba la hora con el formato HH:MM de 24 horas\n")
        if len(Hora.split(":")) == 2:
            horas, minutos = Hora.split(":")
            if horas.isdigit() and minutos.isdigit():
                horas = int(horas)
                minutos = int(minutos)
                if 5 <= horas <= 23 and 0 <= minutos <= 59:
                    break  
                else:
                    if horas <=4 and 0 <= minutos <= 59:
                        print("El metro permanece cerrado desde las 00:00 hasta las 05:00, selecciona otra hora por favor.")
                    else:
                        print("Hora no válida. Asegúrate de introducir la hora en formato HH:MM y que los valores sean correctos.")
            else:
                print("Hora no válida. Asegúrate de introducir la hora en formato HH:MM y que los valores sean correctos.")
        else:
            print("Hora no válida. Asegúrate de introducir la hora en formato HH:MM y que los valores sean correctos.")

    Hora = horas
    Opcion = input(f"¿Quiere que la ruta tenga los menos transbordos posibles o que sea la mas rápida? teclee [Transbordos/Rapida]\n")
    
    while Opcion[0] != "T" and Opcion[0] != "t" and Opcion[0] != "r" and Opcion[0] != "R":
        Opcion = input(f"Por favor introduzcala con el formato 'Tansbordos'/ 'Rapida' / 'T' / 'R' / 't' / 'r' \n")
    if Opcion[0] == "T" or Opcion[0] == "t":
        Opcion = True
    else:
        Opcion = False
        
    caminoMasCorto()
        
Main()
             
            


 #----COMPROBACIONES GRAFO Y PLOT-----
print(G)
# print([a for a in G.edges(data=True)])
pos = nx.circular_layout(G)  # Layout del grafo (puedes ajustarlo según tus preferencias)
colores_n = ['lime' if nodo in path else 'thistle' for nodo in G]
nx.draw(G, pos, with_labels = True, node_size = 500, node_color= colores_n, node_shape = "s", edge_color = 'thistle', width = 2, font_size = 10)
nx.draw(G, pos, node_size = 0, edgelist = list(zip(path,path[1:])), edge_color = 'lime', width = 4, font_size = 10)
plt.show()