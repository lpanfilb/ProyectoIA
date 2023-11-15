import math
import folium
import networkx as nx #tratamiento de grafos
import pandas as pd #hay que instalar pandas y openpyxl
import matplotlib.pyplot as plt #para representar los grafos        

Heur = pd.read_excel('Datos/datos.xlsx', 'HEURISTICA',header= 0, index_col=0)
Dist = pd.read_excel('Datos/datos.xlsx', 'DISTANCIAS', index_col=0)
Tran = pd.read_excel('Datos/datos.xlsx', 'TRANSBORDOS',header= 0,  index_col=0)
Hor = pd.read_excel('Datos/datos.xlsx', 'HORAS',header= 0,  index_col=0)

G = nx.from_pandas_adjacency(Dist, create_using=nx.Graph()) #Creacion del grafo de distancias
nx.set_node_attributes(G, {"Coste": 0, "Heuristica": 0 , "Padre" : ""})


#-----------------------------------------------PRUEBAS--------------------------------------------

df = pd.read_excel('Datos/datos.xlsx', 'HEURISTICA',header= None, index_col=0)  # No usar la primera fila como encabezado

# Transponer el DataFrame para que las columnas representen nodos, X, Y
df = df.T



# Convertir las columnas X e Y a números
df['X'] = pd.to_numeric(df['X'], errors='coerce')
df['Y'] = pd.to_numeric(df['Y'], errors='coerce')

# Crear un mapa centrado en las coordenadas iniciales
mapa = folium.Map(location=[df['X'].mean(), df['Y'].mean()], zoom_start=12)

# Agregar marcadores al mapa
for index, row in df.iterrows():
    folium.Marker(location=[row['X'], row['Y']], popup=row['Coordenadas']).add_to(mapa)

# Guardar el mapa como un archivo HTML
mapa.save('mapa_con_puntos.html')
#-----------------------------------------------PRUEBAS--------------------------------------------


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
    nx.set_node_attributes(G, {inicial: {"Coste": CheckHora(inicial) + CheckTran(inicial), "Heuristica": CheckHeur(inicial), "Padre" : inicial}})                        #añado al primero su heuristica
    caminoMasCortoRec(inicial)#lo mando de forma recursiva
    path.append(final)
    path2.append(final)
    checkPath(final)
    pathWeight.append(G.nodes[inicial].get("Heuristica") + G.nodes[inicial].get("Coste"))#que compruebe el path
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
                                                                                 
            nx.set_node_attributes(G, {actual: {"Coste": costeActual + CheckHora(actual) + CheckTran(actual), "Heuristica": CheckHeur(actual), "Padre": nuevo}})    #cambio los atributos si es necesario     
        nodosAbiertos = sorted(nodosAbiertos, key=lambda x: G.nodes[x]['Coste'])
    if len(nodosAbiertos) >0:       
        siguiente = nodosAbiertos.pop(0)
        nodosCerrados.append(siguiente)
        caminoMasCortoRec(siguiente)  
            
    
def CheckHeur(actual):
    global final                                                                   
    radio_tierra = 6371.0

    lat1 = math.radians(Heur[actual]['X'])
    lon1 = math.radians(Heur[actual]['Y'])
    
    lat2 = math.radians(Heur[final]['X'])
    lon2 = math.radians(Heur[final]['Y'])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distancia = radio_tierra * c
    return round((distancia+1000)/7,917) 
    
def CheckHora(actual):
    global Hora
    return round(Hor.at[Hora,actual])  

def CheckTran(actual):
    return round(Tran.at[actual, actual])                                                                             

def checkPath(final):
    Padre = G.nodes[final].get("Padre")
    Peso = G.nodes[final].get("Coste") + CheckTran(final) + G.nodes[final].get("Heuristica") 
    if  Padre != final:
        if CheckTran(Padre) == 0:
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
        
    caminoMasCorto()


        
Main()
             

import networkx as nx
import matplotlib.pyplot as plt

# Supongamos que ya tienes un grafo existente 'G'

# Crear un grafo dirigido 'G_dirigido' a partir de un camino en 'G'
G_dirigido = nx.DiGraph()


for i in range(len(path) - 1):
    G_dirigido.add_edge(path[i], path[i + 1])

# Crear una figura con dos subgráficos
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

# Calcular un diseño de posiciones (layout) para ambos grafos basado en el grafo original 'G'
pos = nx.spring_layout(G)

# Dibujar el grafo original 'G' en el primer subgráfico
nx.draw(G, pos=pos, with_labels=True, node_size=500, node_color="lightblue", ax=ax1)
ax1.set_title("Mapa Completo")

# Dibujar el grafo dirigido 'G_dirigido' en el segundo subgráfico con las mismas posiciones
nx.draw(G_dirigido, pos=pos, with_labels=True, node_size=500, node_color="lightblue", ax=ax2)
ax2.set_title("Camino mas rápido")

for nodo in G_dirigido.nodes:
    if CheckTran(nodo) != 0:
        nx.draw_networkx_nodes(G_dirigido, pos, nodelist=[nodo], node_color="red", node_size=500)

legend_labels = {"Nodos": "Transbordos", "Aristas": "Aristas", "Transbordos": "Transbordos"}
legend_lines = [plt.Line2D([0], [0], marker='o', color='w', markersize=20, markerfacecolor='lightblue'), plt.Line2D([0], [0],color='black',lw=2), plt.Line2D([0], [0], marker='o', color='w', markersize=20, markerfacecolor='red')]
ax2.legend(legend_lines, legend_labels.values(), loc='upper right')


# Mostrar la figura
plt.show()

# # Crear un mapa centrado en las coordenadas iniciales
# mapa = folium.Map(location=[df['X'].mean(), df['Y'].mean()], zoom_start=12)

# # Agregar marcadores al mapa
# for index, row in df.iterrows():
#     folium.Marker(location=[row['X'], row['Y']], popup=row['Coordenadas']).add_to(mapa)

# # Agregar polilíneas al mapa para representar las aristas del grafo dirigido
# for edge in G_dirigido.edges():
#     start_coords = df.loc[df['Nombre'] == edge[0], ['X', 'Y']].values.flatten().tolist()
#     end_coords = df.loc[df['Nombre'] == edge[1], ['X', 'Y']].values.flatten().tolist()
#     polyline = folium.PolyLine([start_coords, end_coords], color="blue", weight=2.5, opacity=1).add_to(mapa)

# # Guardar el mapa como un archivo HTML
# mapa.save('mapa_con_grafo_dirigido.html')     



# #  #----COMPROBACIONES GRAFO Y PLOT-----
# print(G)
# # print([a for a in G.edges(data=True)])
# pos = nx.circular_layout(G)  # Layout del grafo (puedes ajustarlo según tus preferencias)
# colores_n = ['lime' if nodo in path else 'thistle' for nodo in G]
# nx.draw(G, pos, with_labels = True, node_size = 500, node_color= colores_n, node_shape = "s", edge_color = 'thistle', width = 2, font_size = 10)
# nx.draw(G, pos, node_size = 0, edgelist = list(zip(path,path[1:])), edge_color = 'lime', width = 4, font_size = 10)
# plt.show()