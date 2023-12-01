
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

#Seleccionamos los datos del excel (heuristica, distancias, transbordos, etc.) que necesitaremos para construir el algoritmo

Heur = pd.read_excel('Datos/datos.xlsx', 'HEURISTICA', header=0, index_col=0)
Dist = pd.read_excel('Datos/datos.xlsx', 'DISTANCIAS', index_col=0)
Tran = pd.read_excel('Datos/datos.xlsx', 'TRANSBORDOS', header=0, index_col=0)
Hor = pd.read_excel('Datos/datos.xlsx', 'HORAS', header=0, index_col=0)
Col = pd.read_excel('Datos/datos.xlsx', 'LINEAS', index_col=0)
Coords = pd.read_excel('Datos/datos.xlsx', 'HEURISTICA',header= None, index_col=0)
Coords = Coords.T


G = nx.from_pandas_adjacency(Dist, create_using=nx.Graph())  # Creacion del grafo de distancias
H = G.copy()                                                 # Creamos tambien una copia para poder trabajar y tener un "reset" del grafo disponible si es necesario

#----------Calculo camino mas corto-------------

#Inicializamos todas las variables necesarias (lista de nodos abiertos y cerrados, camino recorrido, etc.)
nodosAbiertos = []
nodosCerrados = []
path = []
pathAux = []                                                                                                                                     #pathAux sera un camino auxiliar que tiene 3 elementos por entrada: parada salida, parada siguiente y color de la linea
Hora = None
inicial = None
final = None


def caminoMasCorto():
    global inicial, final, G
    G = H.__class__()                                                                                                                             #Reseteamos el grafo a la copia (es el mapa inicial sin ningun camino resuelto)
    G.add_nodes_from(H)                                                                                                                           #Añadimos sus nodos
    G.add_edges_from(H.edges)                                                                                                                     #Añadimos sus aristas
    nx.set_node_attributes(G, {"Coste": 0, "Heuristica": 0, "Padre": ""})                                                                         #Seteamos las variables para iniciar el camino (el coste, la heuristica y el nodo padre del que procedemos)
    nx.set_node_attributes(G, {inicial: {"Coste": CheckHora(inicial) + CheckTran(inicial), "Heuristica": CheckHeur(inicial), "Padre" : inicial}}) #Añadimos al primero su heuristica, coste y marcamos que es el padre del que viene a continuacion
    caminoMasCortoRec(inicial)                                                                                                                    #Lo mandamos de forma recursiva
    path.append(final)                                                                                                                            #Al volver ya tendriamos el camino hecho, por lo que añadimos (append) el nodo final (destino)
    nodosCerrados.clear()                                                                                                                         #Vaciamos la lista de nodos vacios
    checkPath(final)                                                                                                                              #Construimos el camino (comprobamos el camino final -> inicio para ver si esta bien)
    pathAux.append([final,final , CheckColor(final,final)])                                                                                       #Añadimos a pathAux el camino final-final con el color de la linea tambien


    
def caminoMasCortoRec(nuevo): #Bucle recursivo que trata la pila de nodos abiertos y cerrados a la vez que añade al grafo G el camino que debemos seguir, recibe un nodo como entrada y lo trata segun este en el grafo (la primera vez recibe el nodo inicial)
    global nodosAbiertos
    for actual in nx.neighbors(G, nuevo):                                                                                                                           #Actual es el iterable de los nodos en el grafo al que estamos apuntando

        if actual not in nodosCerrados:                                                                                                                             #Si no esta en nodos abiertos ni cerrados
            if actual not in nodosAbiertos:                                                                                                                         
                nodosAbiertos.append(actual)                                                                                                                        #Lo añadimos a la lista de nodos abiertos

        costeActual = (G.nodes[nuevo].get("Coste") or 0) + (G.edges[nuevo, actual].get("weight") or 0)                                                              #Calculamos el coste con el peso de la arista y lo guardamos en costeActual

        if G.nodes[actual].get("Coste") is None or G.nodes[actual].get("Coste") > costeActual:                                                                      #Si el coste es 0 o mayor que el coste calculado en la anterior instruccion
                                                                                 
            nx.set_node_attributes(G, {actual: {"Coste": costeActual + CheckHora(actual) + CheckTran(actual), "Heuristica": CheckHeur(actual), "Padre": nuevo}})    #Cambiamos los atributos por los calculados en costeActual    
        
        nodosAbiertos = sorted(nodosAbiertos, key=lambda x: G.nodes[x]['Coste'])                                                                                    #Cargamos la lista de nodos abiertos en nodosAbiertos
    if len(nodosAbiertos) >0:                                                                                                                                       #Si hay nodos abiertos <- CASO BASE DE LA RECURSION AQUI ES DONDE SALTARA CUANDO HAYA LLEGADO AL FINAL
        siguiente = nodosAbiertos.pop(0)                                                                                                                            #Cargamos el nodo siguiente (será el primero de la pila de nodosAbiertos)
        nodosCerrados.append(siguiente)                                                                                                                             #Y lo metemos en la lista de nodos cerrados
        caminoMasCortoRec(siguiente)                                                                                                                                #Llamamos a la recursiva con las listas de nodos actualizadas
            
def CheckHeur(actual): #Funcion que transforma las coordenadas de la heuristica en distancia para la funcion H del algoritmo
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
    
def CheckHora(actual): #Devuelve la hora que se ha seleccionado
    global Hora
    return Hor.at[Hora,actual]  

def CheckTran(actual): #Devuelve si hay transbordo en el nodo que se ha seleccionado
    return Tran.at[actual, actual] 

def CheckColor(actual,final): #Devuelve el color de la linea que conecta los nodos pasados como parametro (deben ser nodos contiguos)
    return Col.at[actual, final]                                                                      

def checkPath(final): #Completa la ruta (comprueba el camino llamando a la recursiva haciendo final -> inicial)
    Padre = G.nodes[final].get("Padre")
    if  Padre != final:                                                                                                                                             #Si un nodo es su mismo padre es que es el inicial, por lo que habremos acabado
        path.append(Padre)                                                                                                                                          #Si no, añadimos el nodo al path
        checkPath(Padre)                                                                                                                                            #Y llamamos a la recursiva con ese nodo (padre del que teniamos)
    else:
        pathAux.append([Padre, path[len(path)-2] , CheckColor(final,final)])                                                                                        #Si hemos acabado añadimos al pathAux donde estan los caminos a seguir con los colores de las lineas el camino Padre con el penultimo del path (el anterior al final)

    if CheckColor(Padre, Padre) is not CheckColor(final, final):                                                                                                    #Y si los colores de las lineas no son el mismo, añadimos un ultimo camino final-final con el color de la linea en la que nos encontremos
        pathAux.append([Padre, final, CheckColor(final, final)])   


#----------Creacion Mapa------------

# Crear un mapa centrado en las coordenadas iniciales
map = folium.Map(location=[Coords['X'].mean(), Coords['Y'].mean()], zoom_start=13)
TotalLineas = folium.FeatureGroup(name="Metro Lyon").add_to(map)

# Agregar marcadores al mapa
for index, row in Coords.iterrows():
    color = CheckColor(row['Coordenadas'], row['Coordenadas'])
    texto = row['Coordenadas']
            
    html_unico = f'''
    <div style="text-align: center; margin: 0; padding: 0;">
        <div class="ovalo" style="width: 100px; height: 50px; border-radius: 50%; margin: 20px auto; display: flex; align-items: center; justify-content: center; color: white; font-size: 40px; font-weight: bold; text-transform: uppercase; background-color: {color};">M</div>
        <div class="linea" style="display: inline-block; padding: 0 0; font-size: 36px;font-style: normal;font-weight: 400;">{texto}</div>
    </div>
    '''

    popupParada = folium.Popup(html = html_unico, show=False, max_width=2650)
    folium.Marker(location=[row['X'], row['Y']], icon = plugins.BeautifyIcon(icon='m', border_color='black', border_width=1, background_color='red', inner_icon_style='transform: translate(0px, 30%); color:#FFFFFF'), popup=popupParada).add_to(TotalLineas)

# Agregar aristas al mapa completo 
for edge in G.edges():
    coord_inicial = Coords.loc[Coords['Coordenadas'] == edge[0], ['X', 'Y']].values.flatten().tolist()
    coord_final = Coords.loc[Coords['Coordenadas'] == edge[1], ['X', 'Y']].values.flatten().tolist()
    polyline = folium.PolyLine([coord_inicial, coord_final], color=CheckColor(edge[0], edge[1]), weight=3.5, opacity=1).add_to(TotalLineas)     


#%%

# ------------------------------------Interfaz usuario------------------------------------

#Inicializamos otra vez las variables
nodosAbiertos = []
nodosCerrados = []
path = []
pathAux = []
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

    #Botón para calcular el camino
    calculate_button = widgets.Button(description="Calcular Camino", button_style='success')
    calculate_button.on_click(lambda btn: update_map(start_node_dropdown.value, end_node_dropdown.value, hora_dropdown.value, btn))

    #Botón de error para cuando nos pasan un input no válido
    calculate_button_err = widgets.Button(description="Recalcular Camino", button_style='danger', style={'button_width': 'initial'})
    calculate_button_err.on_click(lambda btn: update_map(start_node_dropdown.value, end_node_dropdown.value, hora_dropdown.value, btn))

    #Botón que muestra la ruta resumida cuando el camino es correcto
    boton_camino = widgets.Button(description="Ruta simplificada", button_style='info')
    boton_camino.on_click(lambda btn: caminosimple())
    
    #Distintas interfaces segun sea el caso (el menu de error no es igual que el inicial ni igual al de camino correcto)
    if inicial is None:
        display(map)
        if correcto:
            display(widgets.HBox([start_node_dropdown, end_node_dropdown]),
                    widgets.HBox([widgets.Box(layout=widgets.Layout(width='8px')),hora_dropdown,widgets.Box(layout=widgets.Layout(width='234px')), calculate_button]))
        else: 
            display(widgets.HTML("<p style='color:red;font-weight:bold;'>ERROR: Seleccione una parada válida y una hora en el rango de 5:00 a 23:00.</p>"),
                    widgets.HBox([start_node_dropdown, end_node_dropdown]),
                    widgets.HBox([widgets.Box(layout=widgets.Layout(width='8px')),hora_dropdown,widgets.Box(layout=widgets.Layout(width='234px')), calculate_button_err]))
    
    else:
        
            display(widgets.HBox([start_node_dropdown, end_node_dropdown]),
                    widgets.HBox([widgets.Box(layout=widgets.Layout(width='8px')),hora_dropdown,widgets.Box(layout=widgets.Layout(width='234px')), calculate_button, boton_camino]))
        
        
def caminosimple(): #Muestra la ruta simplificada, el codigo es html/css ya que es lo que usamos para mostrar por pantalla el resultado
    html_code = """
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            align-items: left;
        }

        .parada {
            margin: 0;
            padding: 0;
            
            display: inline-block;
            text-align: left;
            border-radius: 10px;
        }

        .dots-container {
            display: flex;
            margin: 0;
            align-items: center;
            height: 100%;
            width: 100%;
        }

        .dot {
            height: 10px;
            width: 10px;
            margin-right: 10px;
            border-radius: 10px;
            animation: pulse 2s infinite ease-in-out;
        }

        .punto {
            width: 8px;
            height: 8px;
            background-color: white;
            border: 2px solid black;
            margin-right: 10px;
            margin-left: 0px;
            border-radius: 50%;
        }

        .posicion1 {
            animation-delay: -0.3s;
        }
        
        posicion2{
            animation-delay: -0.1s;
        }
        
        posicion3{
            animation-delay: 0.1s;
        }

        @keyframes pulse {
            0% {
                transform: scale(0.8);
                box-shadow: 0 0 0 0 rgba(178, 212, 252, 0.7);
                filter: brightness(100%);
                
            }

            50% {
                transform: scale(1.2);
                box-shadow: 0 0 0 0 rgba(178, 212, 252, 0);
                filter: brightness(100%);
                
            }

            100% {
                transform: scale(0.8);
                box-shadow: 0 0 0 0 rgba(178, 212, 252, 0.7);
                filter: brightness(100%);
            }
        }

        .linea {
            display: inline-block;
            padding: 0 0;
            border-radius: 5px;
            font-weight: bold;
            
        }

        .linea-green {
            background-color: #008000; /* Verde */
            
        }

        .linea-blue {
            background-color: #0000fb; /* Azul */
            
        }

        .linea-yellow {
            background-color: #ffff00; /* Amarilla */
            
        }

        .linea-red {
            background-color: #f80000; /* Roja */
            
        }
    </style>
    <div>
    """

    for parada in pathAux: #Para cada parada del pathAux creamos las divs o sections necesarias (en pathAux esta la parada inicial, la siguiente parada (direccion en la que ir) y color de la linea a seguir)
        if(parada[0]!=parada[1]): #Como el ultimo elemento del pathAux es final-final, colorfinal es un caso especial (va al else)
            html_code += """
            <div class="parada">
                    <section class="dots-container">
                        <div class="punto"></div>
                        <div class="linea">{linea}</div>
                    </section>
                    <div class="dot linea-{color} posicion1"></div>
                    <section class="dots-container">
                        <div class="dot linea-{color} posicion2"></div>
                        <div class="linea">En dirección {otra_linea}</div>
                    </section>
                    <div class="dot linea-{color} posicion3"></div>
                    
            
            """.format(linea=parada[0], otra_linea=parada[1], color = parada[2])
        else:   #CASO ESPECIAL FINAL
            html_code += """
                    <section class="dots-container">
                        <div class="punto"></div>
                        <div class="linea">{linea}</div>
                    </section>
            """.format(linea=parada[0])
    html_code += "</div></div>"
    display(widgets.HTML(html_code))

# Función para actualizar el mapa cuando cambian los nodos de inicio y destino
def update_map(start_node, end_node, hora, button):
    global inicial, final, Hora, path
    
    if start_node == "Seleccione Inicio" or end_node == "Seleccione Destino" or not (5 <= hora.hour <= 23):                     #Comprobamos que los datos sean correctos (paradas seleccionadas y hora en la que el metro esta abierto)
        inicial = None
        display(clear=True)
        interfaz(False)                                                                                                         #Si son incorrectos enviamos interfaz(false) que es nuestro marcador de error
        return                                                                                                                  #Y salimos de la ejecucion
    path.clear()                                                                                                                #Reseteamos todas las variables
    pathAux.clear()                                                                                                             #Y seleccionamos el nodo inicial y final con los elegidos en el las cajas de seleccion
    inicial = start_node
    final = end_node
    Hora = hora.hour                                                                                                            #Asignamos tambien la hora
    caminoMasCorto()                                                                                                            #Lo mandamos a calcular el camino
    display_map()                                                                                                               #Y lo mostramos en la interfaz
    
    


# Función para mostrar el mapa actualizado
def display_map():
    global index, polyline, TotalLineas
    setattr(TotalLineas, 'show', False)
   
    mapa = folium.Map(location=[Coords['X'].mean(), Coords['Y'].mean()], zoom_start=13)                                         #Cargamos el mapa completo
    Recorrido = folium.FeatureGroup(name="Ruta Recomendada", show=True).add_to(map)                                             #Cargamos el camino
    
    
    def add_arrow(Recorrido, coord_inicial, coord_final, color, ini, fina):                                                     #Añadimos las flechas (elemento que se encuentra entre los nodos que indica la direccion del camino)
        
        
        # Agregar la línea
        folium.PolyLine([coord_inicial, coord_final], color=color, weight=3.5, opacity=1).add_to(Recorrido)
        
        # Calcular el ángulo de desviacion de la flecha (para que apunte correctamente)
        arrow_angle = round(calcular_angulo(coord_inicial, coord_final), 2)
        arrow_middle = [0.5 * (coord_inicial[0] + coord_final[0]), 0.5 * (coord_inicial[1] + coord_final[1])]
        arrow_heading = plugins.BeautifyIcon(icon='arrow-down', icon_shape='circle', border_color=color, text_color=color, inner_icon_style='transform: rotate({0}deg);'.format(arrow_angle))
       
        # Agregar la "flecha" con los estilos css que le definimos
        html_flechas = """
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }

            .parada {
                margin: 10px;
                padding: 10px;
                
                display: inline-block;
                border-radius: 10px;
            }

            .dots-container {
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100%;
                width: 100%;
            }

            .dot {
                height: 10px;
                width: 10px;
                margin-right: 10px;
                border-radius: 10px;
                animation: pulse 1.5s infinite ease-in-out;
            }

            .dot:nth-child(1) {
                animation-delay: -0.3s;
            }

            .dot:nth-child(2) {
                animation-delay: -0.1s;
            }

            .dot:nth-child(3) {
                animation-delay: 0.1s;
            }
            .dot:nth-child(4) {
                animation-delay: 0.3s;
            }
            

            @keyframes pulse {
                0% {
                    transform: scale(0.8);
                    box-shadow: 0 0 0 0 rgba(178, 212, 252, 0.7);
                    filter: brightness(40%);
                    
                }

                50% {
                    transform: scale(1.2);
                    box-shadow: 0 0 0 10px rgba(178, 212, 252, 0);
                    filter: brightness(100%);
                    
                }

                100% {
                    transform: scale(0.8);
                    box-shadow: 0 0 0 0 rgba(178, 212, 252, 0.7);
                    filter: brightness(60%);
                }
            }
            
            .flecha {
                display: inline-block;
                width = 30px;
                margin: 10 10px;
            }

            .linea {
                display: inline-block;
                padding: 5px 10px;
                border-radius: 5px;
                font-weight: bold;
                
            }

            .linea-green {
                background-color: #008000; /* Verde */
                
            }

            .linea-blue {
                background-color: #0000fb; /* Azul */
                
            }

            .linea-yellow {
                background-color: #ffff00; /* Amarilla */
                
            }

            .linea-red {
                background-color: #f80000; /* Roja */
                
            }
        </style>
        <div class="ruta">
        """

        
        html_flechas += """
            <div class="parada {linea}">
                <section class="dots-container">
                    <div class="linea ">{linea}</div>
                    <div class="dot linea-{color}"></div>
                    <div class="dot linea-{color}"></div>
                    <div class="dot linea-{color}"></div>
                    <div class="linea linea-{color}">Direccion:{otra_linea}</div>
                </section>
            </div>
            """.format(linea=fina, otra_linea=ini, color = color) #Damos formato al menu que sale de la flecha al clickarla (colores y paradas que conecta)
            
        
        popupflecha = folium.Popup(html = html_flechas,show = False, max_width=2650) #Metemos todo el codigo html_flechas en la variable popupinc para luego llamarlo mas facilmente

        folium.Marker(location=arrow_middle, popup = popupflecha, icon=arrow_heading).add_to(Recorrido) #Añadimos las flechas al mapa con su popup correspondiente (popupinc) y con su icono apuntando en direccion al siguiente nodo
    
    def calcular_angulo(coord_inicial, coord_final): #Calcula el angulo al que apunta la flecha comparando las posiciones de los nodos contiguos
        lat_inicial, long_inicial = coord_inicial
        lat_final, long_final = coord_final

        delta_lon = long_final - long_inicial
        delta_lat = lat_final - lat_inicial

        angulo = math.atan2(delta_lon, delta_lat)
        angulo = math.degrees(angulo)
        angulo = (angulo + 360) % 360
        return angulo
    
    G_dirigido = nx.DiGraph()                                       #Creamos el grafo dirigido
    for i in range(len(path) - 1):                                  #Para cada iteracion posible (paso en el camino)          
        G_dirigido.add_edge(path[i], path[i+1])                     #Añadimos la arista entre los nodos del grafo
    
    html_parada = """
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            align-items: left;
        }

        .parada {
            margin: 0;
            padding: 0;
            
            display: inline-block;
            text-align: left;
            border-radius: 10px;
        }

        .dots-container {
            display: flex;
            margin: 0;
            align-items: center;
            height: 100%;
            width: 100%;
        }

        .dot {
            height: 10px;
            width: 10px;
            margin-right: 10px;
            border-radius: 10px;
            animation: pulse 2s infinite ease-in-out;
        }

        .punto {
            width: 8px;
            height: 8px;
            background-color: white;
            border: 2px solid black;
            margin-right: 10px;
            margin-left: 0px;
            border-radius: 50%;
        }

        .posicion1 {
            animation-delay: -0.3s;
        }
        
        posicion2{
            animation-delay: -0.1s;
        }
        
        posicion3{
            animation-delay: 0.1s;
        }

        @keyframes pulse {
            0% {
                transform: scale(0.8);
                box-shadow: 0 0 0 0 rgba(178, 212, 252, 0.7);
                filter: brightness(100%);
                
            }

            50% {
                transform: scale(1.2);
                box-shadow: 0 0 0 0 rgba(178, 212, 252, 0);
                filter: brightness(100%);
                
            }

            100% {
                transform: scale(0.8);
                box-shadow: 0 0 0 0 rgba(178, 212, 252, 0.7);
                filter: brightness(100%);
            }
        }

        .linea {
            display: inline-block;
            padding: 0 0;
            border-radius: 5px;
            font-weight: bold;
            
        }

        .linea-green {
            background-color: #008000; /* Verde */
            
        }

        .linea-blue {
            background-color: #0000fb; /* Azul */
            
        }

        .linea-yellow {
            background-color: #ffff00; /* Amarilla */
            
        }

        .linea-red {
            background-color: #f80000; /* Roja */
            
        }
    </style>
    <div>
    """

    for parada in pathAux: #Para cada parada del pathAux creamos las divs o sections necesarias (en pathAux esta la parada inicial, la siguiente parada (direccion en la que ir) y color de la linea a seguir)
        if(parada[0]!=parada[1]): #Como el ultimo elemento del pathAux es final-final, colorfinal es un caso especial (va al else)
            html_parada += """
            <div class="parada">
                    <section class="dots-container">
                        <div class="punto"></div>
                        <div class="linea">{linea}</div>
                    </section>
                    <div class="dot linea-{color} posicion1"></div>
                    <section class="dots-container">
                        <div class="dot linea-{color} posicion2"></div>
                        <div class="linea">En dirección {otra_linea}</div>
                    </section>
                    <div class="dot linea-{color} posicion3"></div>
                    
            
            """.format(linea=parada[0], otra_linea=parada[1], color = parada[2])
        else:   #CASO ESPECIAL FINAL
            html_parada += """
                    <section class="dots-container">
                        <div class="punto"></div>
                        <div class="linea">{linea}</div>
                    </section>
            """.format(linea=parada[0])
    html_parada += "</div></div>"
    popupinc = folium.Popup(html = html_parada,show = False, max_width=2650)
    
    contenido_html = '''
    <style>
        button {
        padding: 15px 25px;
        border: unset;
        border-radius: 15px;
        color: #212121;
        z-index: 1;
        background: #e8e8e8;
        position: relative;
        font-weight: 1000;
        font-size: 17px;
        -webkit-box-shadow: 4px 8px 19px -3px rgba(0,0,0,0.27);
        box-shadow: 4px 8px 19px -3px rgba(0,0,0,0.27);
        transition: all 250ms;
        overflow: hidden;
        }

        button::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        width: 0;
        border-radius: 15px;
        background-color: #212121;
        z-index: -1;
        -webkit-box-shadow: 4px 8px 19px -3px rgba(0,0,0,0.27);
        box-shadow: 4px 8px 19px -3px rgba(0,0,0,0.27);
        transition: all 250ms
        }

        button:hover {
        color: #e8e8e8;
        }

        button:hover::before {
        width: 100%;
        }


    </style>

    <div>
    <button> Camino Completo
    </button>
    '''
    folium.Marker(location=[45.732047, 4.842442],draggable=True,icon = folium.DivIcon(html=contenido_html), popup=popupinc).add_to(Recorrido)

    
    #folium.Marker(location=[Coords['X'].mean(), Coords['Y'].mean()],draggable=True,icon = plugins.BeautifyIcon(prefix = 'fa',border_color='transparent', background_color='transparent',border_width=0, inner_icon_style='font-size:30px; color: #1E3050', extraClasses ='fa-bounce' 'fa-xl'), popup=popupinc).add_to(Recorrido)
    
    # Agregar los nodos del grafo dirigido
    for index, row in Coords.iterrows():
        if row['Coordenadas'] in path:
            color = CheckColor(row['Coordenadas'], row['Coordenadas'])
            texto = row['Coordenadas']
            
            html_unico = f'''
            <div style="text-align: center; margin: 0; padding: 0;">
                <div class="ovalo" style="width: 100px; height: 50px; border-radius: 50%; margin: 20px auto; display: flex; align-items: center; justify-content: center; color: white; font-size: 40px; font-weight: bold; text-transform: uppercase; background-color: {color};">M</div>
                <div class="linea" style="display: inline-block; padding: 0 0; font-size: 36px;font-style: normal;font-weight: 400;">{texto}</div>
            </div>
            '''

            popupParada = folium.Popup(html = html_unico, show=False, max_width=2650)
            folium.Marker(location=[row['X'], row['Y']], icon = plugins.BeautifyIcon(icon='m', border_color='black', border_width=1, background_color=CheckColor(row['Coordenadas'], row['Coordenadas']), inner_icon_style='transform: translate(0px, 30%); color:#FFFFFF'), popup=popupParada, max_width=2650).add_to(Recorrido)
    
    # Agregar polilíneas al mapa para representar las aristas del grafo dirigido
    for edge in G_dirigido.edges():
        coord_inicial = Coords.loc[Coords['Coordenadas'] == edge[0], ['X', 'Y']].values.flatten().tolist()
        coord_final = Coords.loc[Coords['Coordenadas'] == edge[1], ['X', 'Y']].values.flatten().tolist()
    
        # Agregar la línea con "flecha"
        add_arrow(Recorrido, coord_inicial, coord_final, color=CheckColor(edge[0], edge[1]), ini = edge[0], fina = edge[1])
    
    TotalLineas.add_to(mapa)  #Añadimos la opcion de mostrar el mapa completo a la interfaz
    Recorrido.add_to(mapa)    #Añadimos la opcion de mostrar el recorrido a la interfarz
    
    folium.LayerControl( draggable = True).add_to(mapa)  #Lo hacemos con capas distintas (para que no se solapen las opciones de TotalLineas y Recorrido)

    display(clear=True) #Reseteamos si ya habia un mapa antes
    display(mapa)       #Seleccionamos nuestro mapa nuevo
    interfaz(True)      #Establecemos la interfaz a la de exito (para que aparezca el menu correspondiente)
        

interfaz(True)   #La interfaz inicial es la de Seleccionar Camino asi que la llamamos para que en la primera iteracion aparezca correctamente
# %%
