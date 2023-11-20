
#%%
#Librerias necesarias para su ejecucion

from datetime import datetime
import math
import networkx as nx
import pandas as pd
import ipywidgets as widgets #ipyleaflet
import folium
from ipywidgets import  widgets
from IPython.display import display
from folium import plugins

Heur = pd.read_excel('Datos/datos.xlsx', 'HEURISTICA', header=0, index_col=0)
Dist = pd.read_excel('Datos/datos.xlsx', 'DISTANCIAS', index_col=0)
Tran = pd.read_excel('Datos/datos.xlsx', 'TRANSBORDOS', header=0, index_col=0)
Hor = pd.read_excel('Datos/datos.xlsx', 'HORAS', header=0, index_col=0)
Col = pd.read_excel('Datos/datos.xlsx', 'LINEAS', index_col=0)
Coords = pd.read_excel('Datos/datos.xlsx', 'HEURISTICA',header= None, index_col=0)
Coords = Coords.T


G = nx.from_pandas_adjacency(Dist, create_using=nx.Graph())  # Creacion del grafo de distancias
H = G.copy()

#----------Calculo camino mas corto-------------

nodosAbiertos = []
nodosCerrados = []
path = []
Hora = None
inicial = None
final = None


def caminoMasCorto():
    global inicial, final, G
    G = H.__class__()
    G.add_nodes_from(H)
    G.add_edges_from(H.edges)  
    nx.set_node_attributes(G, {"Coste": 0, "Heuristica": 0, "Padre": ""}) 
    nx.set_node_attributes(G, {inicial: {"Coste": CheckHora(inicial) + CheckTran(inicial), "Heuristica": CheckHeur(inicial), "Padre" : inicial}})                        #añado al primero su heuristica
    caminoMasCortoRec(inicial)#lo mando de forma recursiva
    path.append(final)
    nodosCerrados.clear()
    checkPath(final)
    
def caminoMasCortoRec(nuevo):
    global nodosAbiertos
    for actual in nx.neighbors(G, nuevo):

        if actual not in nodosCerrados:
            if actual not in nodosAbiertos:
                nodosAbiertos.append(actual)

        costeActual = (G.nodes[nuevo].get("Coste") or 0) + (G.edges[nuevo, actual].get("weight") or 0)

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
    if  Padre != final:
        path.append(Padre)
        checkPath(Padre)
        
#----------Creacion Mapa------------
# Crear un mapa centrado en las coordenadas iniciales
map = folium.Map(location=[Coords['X'].mean(), Coords['Y'].mean()], zoom_start=13)
TotalLineas = folium.FeatureGroup(name="Metro Lyon").add_to(map)

# Agregar marcadores al mapa
for index, row in Coords.iterrows():
    folium.Marker(location=[row['X'], row['Y']], icon = plugins.BeautifyIcon(icon='m', border_color='black', border_width=1, background_color='red', inner_icon_style='transform: translate(0px, 30%); color:#FFFFFF'), popup=row['Coordenadas']).add_to(TotalLineas)
# Agregar aristas al mapa completo 
for edge in G.edges():
    coord_inicial = Coords.loc[Coords['Coordenadas'] == edge[0], ['X', 'Y']].values.flatten().tolist()
    coord_final = Coords.loc[Coords['Coordenadas'] == edge[1], ['X', 'Y']].values.flatten().tolist()
    polyline = folium.PolyLine([coord_inicial, coord_final], color=CheckColor(edge[0], edge[1]), weight=3.5, opacity=1).add_to(TotalLineas)     


#%%

# ------------------------------------Interfaz usuario------------------------------------

nodosAbiertos = []
nodosCerrados = []
path = []
Hora = None
inicial = None
final = None

def interfaz(correcto):
    # Desplegable nodo inicial
    start_node_dropdown = widgets.Dropdown(
        options=["Seleccione Inicio"] + list(G.nodes),
        value = "Seleccione Inicio",
        description='Nodo de inicio:',
        style={'description_width': 'initial'}
    )
    #desplegable nodo final
    end_node_dropdown = widgets.Dropdown(
        options=["Seleccione Destino"] + list(G.nodes),
        value = "Seleccione Destino",
        description='Nodo de destino:',
        style={'description_width': 'initial'}
    )
    
    #selector hora
    hora_dropdown = widgets.TimePicker(
        description='Hora',
        value = datetime.now().time(),
        disabled=False,
    )

    # Botón para calcular el camino
    calculate_button = widgets.Button(description="Calcular Camino", button_style='success')
    calculate_button.on_click(lambda btn: update_map(start_node_dropdown.value, end_node_dropdown.value, hora_dropdown.value, btn))


    calculate_button_err = widgets.Button(description="Recalcular Camino", button_style='danger', style={'button_width': 'initial'})
    calculate_button_err.on_click(lambda btn: update_map(start_node_dropdown.value, end_node_dropdown.value, hora_dropdown.value, btn))
    
    # display(clear=True)
    
    if correcto:
        display(widgets.HBox([start_node_dropdown, end_node_dropdown]),
                widgets.HBox([widgets.Box(layout=widgets.Layout(width='8px')),hora_dropdown,widgets.Box(layout=widgets.Layout(width='234px')), calculate_button]))
    else: 
        display(widgets.HTML("<p style='color:red;font-weight:bold;'>Seleccione una parada válida y una hora en el rango de 5:00 a 23:00.</p>"),
                widgets.HBox([start_node_dropdown, end_node_dropdown]),
                widgets.HBox([widgets.Box(layout=widgets.Layout(width='8px')),hora_dropdown,widgets.Box(layout=widgets.Layout(width='234px')), calculate_button_err]))
    
    

# Función para actualizar el mapa cuando cambian los nodos de inicio y destino
def update_map(start_node, end_node, hora, button):
    global inicial, final, Hora, path
    
    if start_node == "Seleccione Inicio" or end_node == "Seleccione Destino" or not (5 <= hora.hour <= 23):
        interfaz(False)
        return
    path.clear()
    inicial = start_node
    final = end_node
    Hora = hora.hour
    caminoMasCorto()
    display_map()
    
    


# Función para mostrar el mapa actualizado
def display_map():
    global index, polyline, TotalLineas
    setattr(TotalLineas, 'show', False)
   
    mapa = folium.Map(location=[Coords['X'].mean(), Coords['Y'].mean()], zoom_start=13)
    Recorrido = folium.FeatureGroup(name="Ruta Recomendada", show=True).add_to(map)
    
    
    def add_arrow(Recorrido, coord_inicial, coord_final, color='blue'):
        # Agregar la línea
        folium.PolyLine([coord_inicial, coord_final], color=color, weight=3.5, opacity=1).add_to(Recorrido)
        # Calcular el ángulo de la flecha
        arrow_angle = round(calcular_angulo(coord_inicial, coord_final), 2)
        arrow_middle = [0.5 * (coord_inicial[0] + coord_final[0]), 0.5 * (coord_inicial[1] + coord_final[1])]
        arrow_heading = plugins.BeautifyIcon(icon='arrow-down', icon_shape='circle', border_color=color, text_color=color, inner_icon_style='transform: rotate({0}deg);'.format(arrow_angle))
        # Agregar la "flecha"
        folium.Marker(location=arrow_middle, icon=arrow_heading).add_to(Recorrido)
    
    def calcular_angulo(coord_inicial, coord_final):
        lat_inicial, long_inicial = coord_inicial
        lat_final, long_final = coord_final

        delta_lon = long_final - long_inicial
        delta_lat = lat_final - lat_inicial

        angulo = math.atan2(delta_lon, delta_lat)
        angulo = math.degrees(angulo)
        angulo = (angulo + 360) % 360
        return angulo
    
    G_dirigido = nx.DiGraph()
    for i in range(len(path) - 1):
        G_dirigido.add_edge(path[i], path[i+1])
    # Agregar polilíneas al mapa para representar las aristas del grafo dirigido
    for index, row in Coords.iterrows():
        if row['Coordenadas'] in path:
            folium.Marker(location=[row['X'], row['Y']],icon = plugins.BeautifyIcon(icon='m', border_color='black', border_width=1, background_color=CheckColor(row['Coordenadas'], row['Coordenadas']), inner_icon_style='transform: translate(0px, 30%); color:#FFFFFF'), popup=row['Coordenadas']).add_to(Recorrido)
 
    for edge in G_dirigido.edges():
        coord_inicial = Coords.loc[Coords['Coordenadas'] == edge[0], ['X', 'Y']].values.flatten().tolist()
        coord_final = Coords.loc[Coords['Coordenadas'] == edge[1], ['X', 'Y']].values.flatten().tolist()
    # Agregar la línea con "flecha"
        add_arrow(Recorrido, coord_inicial, coord_final, color=CheckColor(edge[0], edge[1]))

    TotalLineas.add_to(mapa)
    Recorrido.add_to(mapa)
    
    folium.LayerControl( draggable = True).add_to(mapa)

    if inicial is not None:
        display(mapa)
        interfaz(True)
        
display(map)
interfaz(True)   
# %%
