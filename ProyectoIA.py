
import heapq #utilizamos una priority queue
import pandas as pd #hay que instalar pandas y openpyxl

class Parada:
    def __init__(self, estado,index=0, acumulado=0, padre=None,  heuristica=0):
        self.estado = estado #comrpobar si esta en la pila de abiertos o cerrados
        self.index = index #index en las matrices para las distancias
        self.acumulado = acumulado #distancia desde el inicio a este nodo
        self.padre = padre #parada de la que viene
        self.heuristica = heuristica #distancia desde el nodo hasta el puesto como final


Heur = pd.read_excel('Datos/datos.xlsx', 'HEURISTICA', index_col=0)
Dist = pd.read_excel('Datos/datos.xlsx', 'DISTANCIAS', index_col=0)
Heur.at['madrid','barcelona']







# Heurist = [[ciu1, distciud2, distciud3, distciud4],     #vamos a declarar una matriz con la heuristica
#                  [distciu1, ciud2, distciud3, distciud4]]

# Dist = [[ciu1, distciud2, distciud3, distciud4],       #vamos a hacer una matriz con las distancias entre lugares
#                  [distciu1, ciud2, distciud3, distciud4]]
# print(Datos.sheet_names)
# Dist = Datos.parse('DISTANCIAS')
# Heur = Datos.parse('HEURISTICA')
# print(Heur)
# print(Dist)
# Datos
# def Heuristica(inicio, final):
#     return Heurist[inicio.index, final.index]
# def Distancia(inicio, final):
#     return Dist[inicio.index, final.index]







# class Nodo:
#     def __init__(self, state, parent=None, action=None, cost=0, heuristic=0):
#         self.state = state  #Abierto/cerrado
#         self.parent = parent  #padre
#         self.action = action  #Acción que llevó a este estado desde el padre
#         self.cost = cost  #Costo desde inicio
#         self.heuristic = heuristic  #h(n)

#     def total_cost(self):
#         return self.cost + self.heuristic


# def astar(initial_state, goal_state):
#     open_list = []  #Nodos abiertos
#     closed_set = set()  #Nodos cerrados

    
#     start_node = Nodo(state=initial_state, cost=0, heuristic=calculate_heuristic(initial_state, goal_state))
#     heapq.heappush(open_list, (start_node.total_cost(), start_node))

#     while open_list:
#         _, current_node = heapq.heappop(open_list)

#         if current_node.state == goal_state:
#             # Llegamos al objetivo, reconstruimos el camino
#             path = []
#             while current_node:
#                 path.append((current_node.state, current_node.action))
#                 current_node = current_node.parent
#             path.reverse()
#             return path

#         closed_set.add(current_node.state)

#         # Generamos los sucesores y los agregamos a la lista de nodos abiertos
#         for successor_state, action, step_cost in generate_successors(current_node.state):
#             if successor_state not in closed_set:
#                 successor_cost = current_node.cost + step_cost
#                 successor_node = Nodo(
#                     state=successor_state,
#                     parent=current_node,
#                     action=action,
#                     cost=successor_cost,
#                     heuristic=calculate_heuristic(successor_state, goal_state)
#                 )
#                 heapq.heappush(open_list, (successor_node.total_cost(), successor_node))

#     # Si no se encuentra un camino, retornamos None
#     return None

# # Función para calcular la heurística (puede ser personalizada)
# def calculate_heuristic(state, goal_state):
#     # En este ejemplo, utilizamos una heurística nula
#     return 0

# # Función para generar sucesores (debe ser personalizada para el problema específico)
# def generate_successors(state):
#     # Aquí debes generar los sucesores a partir del estado actual y definir las acciones y costos
#     pass

# # Ejemplo de uso
# initial_state = (0, 0)
# goal_state = (4, 4)
# path = astar(initial_state, goal_state)

# if path:
#     print("Camino encontrado:")
#     for state, action in path:
#         print(f"Estado: {state}, Acción: {action}")
# else:
#     print("No se encontró un camino hacia el objetivo.")

