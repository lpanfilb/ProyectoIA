#%%
import math
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import ipywidgets as widgets #ipyleaflet
from ipywidgets import  widgets
from IPython.display import display
import folium
from folium import plugins

Heur = pd.read_excel('Datos/datos.xlsx', 'HEURISTICA', header=0, index_col=0)
Dist = pd.read_excel('Datos/datos.xlsx', 'DISTANCIAS', index_col=0)
Tran = pd.read_excel('Datos/datos.xlsx', 'TRANSBORDOS', header=0, index_col=0)
Hor = pd.read_excel('Datos/datos.xlsx', 'HORAS', header=0, index_col=0)
Col = pd.read_excel('Datos/datos.xlsx', 'LINEAS', index_col=0)
Coords = pd.read_excel('Datos/datos.xlsx', 'HEURISTICA',header= None, index_col=0)
Coords = Coords.T


G = nx.from_pandas_adjacency(Dist, create_using=nx.Graph())  # Creacion del grafo de distancias
nx.set_node_attributes(G, {"Coste": 0, "Heuristica": 0, "Padre": ""})

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
    return Hor.at[Hora,actual]  

def CheckTran(actual):
    return Tran.at[actual, actual] 

def CheckColor(actual,final):
    return Col.at[actual, final]                                                                      

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

# # Crear un mapa centrado en las coordenadas iniciales
map = folium.Map(location=[Coords['X'].mean(), Coords['Y'].mean()], zoom_start=13)
    


# Agregar marcadores al mapa
for index, row in Coords.iterrows():
    folium.Marker(location=[row['X'], row['Y']], icon = plugins.BeautifyIcon(icon='m', border_color='black', border_width=1, background_color='red', inner_icon_style='transform: translate(0px, 30%); color:#FFFFFF'), popup=row['Coordenadas']).add_to(map)
    
for edge in G.edges():
    start_coords = Coords.loc[Coords['Coordenadas'] == edge[0], ['X', 'Y']].values.flatten().tolist()
    end_coords = Coords.loc[Coords['Coordenadas'] == edge[1], ['X', 'Y']].values.flatten().tolist()
    polyline = folium.PolyLine([start_coords, end_coords], color=CheckColor(edge[0], edge[1]), weight=3.5, opacity=1).add_to(map)
    

map.save('mapaMetro.html')     


# ------------------------------------ MAPA INTERACTIVO ------------------------------------

nodosAbiertos = []
nodosCerrados = []
path = []
path2 = []
pathWeight = []
Hora = None
inicial = None
final = None

# Función para actualizar el mapa cuando cambian los nodos de inicio y destino
def update_map(start_node, end_node, hora, button):
    global inicial, final, Hora, path, nodosAbiertos, nodosCerrados
    path =[]
    nodosAbiertos = []
    nodosCerrados = []
    inicial = start_node
    final = end_node
    Hora = hora
    caminoMasCorto()
    display_map()
    
    

# Widget de selección de nodos
start_node_dropdown = widgets.Dropdown(
    options=list(G.nodes),
    value=list(G.nodes)[0],
    description='Nodo de inicio:',
    style={'description_width': 'initial'}
)

end_node_dropdown = widgets.Dropdown(
    options=list(G.nodes),
    value=list(G.nodes)[-1],
    description='Nodo de destino:',
    style={'description_width': 'initial'}
)

hora_dropdown = widgets.Dropdown(
    options=list(range(1, 24)),
    value=1,
    description='Horas:',
    style={'description_width': 'initial'}
)

# Botón para calcular el camino
calculate_button = widgets.Button(description="Calcular Camino", button_style='success')
calculate_button.on_click(lambda btn: update_map(start_node_dropdown.value, end_node_dropdown.value, hora_dropdown.value, btn))

# Crear widget interactivo
#interact(update_map, start_node=start_node_dropdown, end_node=end_node_dropdown, hora=hora_dropdown, button=fixed(calculate_button))

# Función para mostrar el mapa actualizado
def display_map():
    global index, polyline
    # Limpiar capas antes de agregar nuevos elementos
   
    mapa = folium.Map(location=[Coords['X'].mean(), Coords['Y'].mean()], zoom_start=13)
    TotalLineas = folium.FeatureGroup(name="Metro Lyon", show=False).add_to(mapa)
    Recorrido = folium.FeatureGroup(name="Ruta Recomendada", show=True).add_to(mapa)

    def add_arrow(Recorrido, start_coords, end_coords, color='blue'):
        # Agregar la línea
        folium.PolyLine([start_coords, end_coords], color=color, weight=3.5, opacity=1).add_to(Recorrido)

        # Calcular el ángulo de la flecha
        arrow_angle = round(calculate_bearing(start_coords, end_coords), 2)
        
        arrow_middle = [0.5 * (start_coords[0] + end_coords[0]), 0.5 * (start_coords[1] + end_coords[1])]
        arrow_heading = plugins.BeautifyIcon(icon='arrow-down', icon_shape='circle', border_color=color, text_color=color, inner_icon_style='transform: rotate({0}deg);'.format(arrow_angle))

        # Agregar la "flecha"
        folium.Marker(location=arrow_middle, icon=arrow_heading).add_to(Recorrido)
    
    def calculate_bearing(start_coords, end_coords):
        start_lat, start_lon = start_coords
        end_lat, end_lon = end_coords

        delta_lon = end_lon - start_lon
        delta_lat = end_lat - start_lat

        bearing = math.atan2(delta_lon, delta_lat)
        bearing = math.degrees(bearing)
        bearing = (bearing + 360) % 360

        return bearing
    # Agregar marcadores al mapa
    for index, row in Coords.iterrows():
        folium.Marker(location=[row['X'], row['Y']], icon = plugins.BeautifyIcon(icon='m', border_color='black', border_width=1, background_color='red', inner_icon_style='transform: translate(0px, 30%); color:#FFFFFF'), popup=row['Coordenadas']).add_to(TotalLineas)
    
    for edge in G.edges():
        start_coords = Coords.loc[Coords['Coordenadas'] == edge[0], ['X', 'Y']].values.flatten().tolist()
        end_coords = Coords.loc[Coords['Coordenadas'] == edge[1], ['X', 'Y']].values.flatten().tolist()
        polyline = folium.PolyLine([start_coords, end_coords], color=CheckColor(edge[0], edge[1]), weight=3.5, opacity=1).add_to(TotalLineas)
    
    G_dirigido = nx.DiGraph()
    for i in range(len(path) - 1):
        G_dirigido.add_edge(path[i+1], path[i])

# Agregar polilíneas al mapa para representar las aristas del grafo dirigido
    for index, row in Coords.iterrows():
        if row['Coordenadas'] in path:
            folium.Marker(location=[row['X'], row['Y']],icon = plugins.BeautifyIcon(icon='m', border_color='black', border_width=1, background_color=CheckColor(row['Coordenadas'], row['Coordenadas']), inner_icon_style='transform: translate(0px, 30%); color:#FFFFFF'), popup=row['Coordenadas']).add_to(Recorrido)
 
    for edge in G_dirigido.edges():
        start_coords = Coords.loc[Coords['Coordenadas'] == edge[0], ['X', 'Y']].values.flatten().tolist()
        end_coords = Coords.loc[Coords['Coordenadas'] == edge[1], ['X', 'Y']].values.flatten().tolist()
    # Agregar la línea con "flecha"
        add_arrow(Recorrido, start_coords, end_coords, color=CheckColor(edge[0], edge[1]))

    
    # Agregar capas al mapa
    TotalLineas.add_to(mapa)
    Recorrido.add_to(mapa)
    
    folium.LayerControl().add_to(mapa)

    if inicial is not None:
        display(mapa)
        display(start_node_dropdown, end_node_dropdown, hora_dropdown, calculate_button)
    # Mostrar el mapa
display(map)
display(start_node_dropdown, end_node_dropdown, hora_dropdown, calculate_button)    
# Mostrar el mapa inicial
display_map()

# %%
