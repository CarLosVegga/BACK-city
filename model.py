import numpy as np

from mesa import Agent, Model

from mesa.space import ContinuousSpace as Grid

from mesa.time import StagedActivation

from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from random import randint
from math import sqrt

from BFS import BFS

FRAME_RATE = 30

class Node():
    def __init__(self, pos = [0, 0], adjs = [], trafficLights = {}):
        self.pos = pos
        self.adjs = adjs
        self.trafficLights = trafficLights
        self.isTransitable = False

# Car Agent
class Car(Agent):
    def __init__(self, model, pos, startingNode, endingNode, speed = [0, 0]):
        super().__init__(model.next_id(), model)
        self.pos = pos
        self.currentNode = startingNode
        self.endingNode = endingNode
        self.speed = speed
        self.path  = BFS(self.model.matrix, startingNode, endingNode)
        self.direction = self.getDirection(self.currentNode, self.path[1])

    def step(self):
        if self.currentNode == self.endingNode:
            return
        
        nextNode = self.path[1]
        self.direction = self.getDirection(self.currentNode, nextNode)
        car_ahead = self.car_ahead(self.direction)
        if car_ahead == None and not self.encountersRedLight(nextNode, self.direction):
            new_speed = self.accelerate(self.direction)
        elif car_ahead != None:
            new_speed = self.decelerate(car_ahead, self.direction)
        elif self.encountersRedLight(nextNode, self.direction):
            new_speed = self.decelerate(self.model.matrix[nextNode].pos, self.direction)
                
        new_speed = self.speedLimits(new_speed, self.direction)

        self.speed = np.array(new_speed)

        if self.direction == 'left':
            new_pos = (self.pos + np.array([0.3, 0.0]) * self.speed).tolist()
        elif self.direction == 'right':
            new_pos = (self.pos + np.array([0.3, 0.0]) * self.speed).tolist()
        elif self.direction == 'up':
            new_pos = (self.pos + np.array([0.0, 0.3]) * self.speed).tolist()
        elif self.direction == 'down':
            new_pos = (self.pos + np.array([0.0, 0.3]) * self.speed).tolist()

        if self.arrivedToNode(new_pos, nextNode, self.direction):
            self.pos = self.model.matrix[nextNode].pos
            self.path = self.path[1:]
            self.currentNode = nextNode

            if self.currentNode == self.endingNode:
                return
        
        self.model.grid.move_agent(self, new_pos)

    # Correct speed limits in case acceleration/deacceleration gets out of bounds
    def speedLimits(self, new_speed, direction):
        if direction == 'left' and new_speed[0] <= -self.model.speedLimit:
            return [-self.model.speedLimit, 0]
        elif direction == 'left' and new_speed[0] >= 0.0:
            return [0.0, 0.0]
        elif direction == 'right' and new_speed[0] >= self.model.speedLimit:
            return [self.model.speedLimit, 0.0]
        elif direction == 'right' and new_speed[0] <= 0.0:
            return [0.0, 0.0]
        elif direction == 'up' and new_speed[1] >= self.model.speedLimit:
            return [0.0, self.model.speedLimit]
        elif direction == 'up' and new_speed[1] <= 0.0:
            return [0.0, 0.0]
        elif direction == 'down' and new_speed[1] <= self.model.speedLimit:
            return [0.0, -self.model.speedLimit]
        elif direction == 'down' and new_speed[1] >= 0.0:
            return [0.0, 0.0]
        else:
            return new_speed
    
    def car_ahead(self, direction):
        for neighbor in self.model.grid.get_neighbors(self.pos, 30):
            if direction == 'right' and neighbor.pos[0] > self.pos[0]  and neighbor.pos[1] == self.pos[1]:
                return neighbor
            elif direction == 'left' and neighbor.pos[0] < self.pos[0] and neighbor.pos[1] == self.pos[1]:
                return neighbor
            elif direction == 'up' and neighbor.pos[1] > self.pos[1] and neighbor.pos[0] == self.pos[0]:
                return neighbor
            elif direction == 'down' and neighbor.pos[1] < self.pos[1] and neighbor.pos[0] == self.pos[0]:
                return neighbor
        return None
        
    def getDirection(self, start, end):
        start = self.model.matrix[start]
        end = self.model.matrix[end]
        x = end.pos[0] - start.pos[0]
        y = end.pos[1] - start.pos[1]

        if x < 0: return 'left'
        elif x > 0: return 'right'
        elif y < 0: return 'down'
        elif y > 0: return 'up'

    # To know if you can accelerate or deaccelerate according to the Traffic Light
    def encountersRedLight(self, nextNodeIndex, direction):
        nextNode = self.model.matrix[nextNodeIndex]
        distanceToNode = sqrt(pow(nextNode.pos[0] - self.pos[0], 2) + pow(nextNode.pos[1] - self.pos[1], 2))

        if (distanceToNode > 25): return False
        if (nextNode.trafficLights):
            if (nextNode.trafficLights[direction].state == 'g'): return False
        
        return True

    # To determine if you are changing of node after new position
    def arrivedToNode(self, pos, nextNode, direction):
        nextPosition = self.model.matrix[nextNode].pos
        if (direction == 'right'):
            return True if pos[0] >= nextPosition[0] else False
        elif (direction == 'left'):
            return True if pos[0] <= nextPosition[0] else False
        elif (direction == 'down'):
            return True if pos[1] <= nextPosition[1] else False
        elif (direction == 'up'):
            return True if pos[1] >= nextPosition[1] else False

    def accelerate(self, direction): 
        if direction == 'left':
            return [self.speed[0] - 0.05, 0]
        elif direction == 'right':
            return [self.speed[0] + 0.05, 0]
        elif direction == 'up':
            return [0, self.speed[1] + 0.05]
        elif direction == 'down':
            return [0, self.speed[1] - 0.05]

    def decelerate(self, object, direction):
        # It is decelerating because of a car ahead
        if isinstance(object, Car):
            if direction == 'left':
                return [object.speed[0] + 0.1, 0]
            elif direction == 'right':
                return [object.speed[0] - 0.1, 0]
            elif direction == 'up':
                return [0, object.speed[1] - 0.1]
            elif direction == 'down':
                return [0, object.speed[1] + 0.1]
        # TODO: Mejorar frenado

        if direction == 'left':
            return [self.speed[0] + 0.1, 0]
        elif direction == 'right':
            return [self.speed[0] - 0.1, 0]
        elif direction == 'up':
            return [0, self.speed[1] - 0.1]
        elif direction == 'down':
            return [0, self.speed[1] + 0.1]


# Traffic Light Agent
class TL(Agent):
    def __init__(self, model, state):
        super().__init__(model.next_id(), model)

        self.ticks = 0

        if (state == 'g'): self.ticks = 0
        elif (state == 'y'): self.ticks = 5 * FRAME_RATE
        else: self.ticks = 8 * FRAME_RATE
        
        self.state = '' # Initially turned off

    def step(self):
        if self.ticks == 0:
            self.state = 'g'
        elif self.ticks == 5 * FRAME_RATE:
            self.state = 'y'
        elif self.ticks == 8 * FRAME_RATE: 
            self.state = 'r'
        elif self.ticks == 13 * FRAME_RATE:
            self.ticks = -1
        self.ticks += 1

# City Model
class City(Model):    
    def __init__(self):
        super().__init__()

        self.schedule = StagedActivation(self)
        self.grid = Grid(601, 601, torus=False)
        self.count = 1
        self.speedLimit = 1.0
        # Traffics lights orientation are inverterted
        self.matrix = {
            1: Node([0, 100], [8], {}),
            2: Node([0, 200], [], {}),
            3: Node([0, 300], [10], {}),
            4: Node([0, 400], [], {}),
            5: Node([0, 500], [12], {}),
            6: Node([0, 600], [], {}),
            7: Node([100, 0], [], {}),
            8: Node([100, 100], [7, 14], {"right": TL(self, 'g'), "down": TL(self, 'r')}),
            9: Node([100, 200], [2, 8], {"left": TL(self, 'g'), "down": TL(self, 'r')}),
            10: Node([100, 300], [9, 16], {"right": TL(self, 'g'), "down": TL(self, 'r')}),
            11: Node([100, 400], [4, 10], {"left": TL(self, 'g'), "down": TL(self, 'r')}),
            12: Node([100, 500], [11, 18], {"right": TL(self, 'g'), "down": TL(self, 'r')}),
            13: Node([100, 600], [6, 12], {"left": TL(self, 'g')}),
            14: Node([200, 100], [21, 15], {"right": TL(self, 'g')}),
            15: Node([200, 200], [9, 16], {"left": TL(self, 'g'), "up": TL(self, 'r')}),
            16: Node([200, 300], [17, 35], {"right": TL(self, 'g'), "up": TL(self, 'r')}),
            17: Node([200, 400], [11, 18], {"left": TL(self, 'g'), "up": TL(self, 'r')}),
            18: Node([200, 500], [19, 24], {"right": TL(self, 'g'), "up": TL(self, 'r')}),
            19: Node([200, 600], [13], {"left": TL(self, 'g'), "up": TL(self, 'r')}),
            20: Node([300, 0], [], {}),
            21: Node([300, 100], [20, 27], {"right": TL(self, 'g'), "down": TL(self, 'r')}),
            22: Node([300, 200], [21, 15], {"left": TL(self, 'g')}),
            23: Node([300, 400], [17], {"left": TL(self, 'g'), "down": TL(self, 'r')}),
            24: Node([300, 500], [23, 30], {"right": TL(self, 'g'), "down": TL(self, 'r')}),
            25: Node([300, 600], [19, 24], {"left": TL(self, 'g')}),
            26: Node([400, 0], [27], {}),
            27: Node([400, 100], [28, 33], {"right": TL(self, 'g'), "up": TL(self, 'r')}),
            28: Node([400, 200], [22], {"left": TL(self, 'g'), "up": TL(self, 'r')}),
            29: Node([400, 400], [23, 30], {"left": TL(self, 'g')}),
            30: Node([400, 500], [37, 31], {"right": TL(self, 'g'), "up": TL(self, 'r')}),
            31: Node([400, 600], [25], {"left": TL(self, 'g'), "up": TL(self, 'r')}),
            32: Node([500, 0], [], {}),
            33: Node([500, 100], [32, 39], {"right": TL(self, 'g'), "down": TL(self, 'r')}),
            34: Node([500, 200], [28, 33], {"left": TL(self, 'g'), "down": TL(self, 'r')}),
            35: Node([500, 300], [34, 41], {"right": TL(self, 'g'), "down": TL(self, 'r')}),
            36: Node([500, 400], [35, 29], {"left": TL(self, 'g'), "down": TL(self, 'r')}),
            37: Node([500, 500], [36, 43], {"right": TL(self, 'g'), "down": TL(self, 'r')}),
            38: Node([500, 600], [31, 37], {"left": TL(self, 'g')}),
            39: Node([600, 100], [], {}),
            40: Node([600, 200], [34], {}),
            41: Node([600, 300], [], {}),
            42: Node([600, 400], [36], {}),
            43: Node([600, 500], [], {}),
            44: Node([600, 600], [38], {}),
        }

        # Starting schedulers for all traffic lights
        for _, node in self.matrix.items():
            for _, trafficLight in node.trafficLights.items():
                self.schedule.add(trafficLight)

        # To provide cars start and endpoints
        self.startingNodes = [1, 3, 5, 26, 40, 42, 44]
        self.endNodes = [2, 4, 6, 7, 20, 32, 39, 41, 43]
        self.endPositions = []
        for node in self.endNodes:
            self.endPositions.append(self.matrix[node].pos)
        self.carObjects = []
        # Initialize a car on each starting node with a random end node
        for start in self.startingNodes:
            end = self.endNodes[randint(0, len(self.endNodes) - 1)]
            car = Car(self, self.matrix[start].pos, start, end)
            self.grid.place_agent(car, car.pos)
            self.schedule.add(car)  
            self.carObjects.append(car)
        
        
    def step(self):
        self.schedule.step()
        
        car_coords = {}
        tl_data = {}

        data = {
            "car_coords": car_coords,
            "tl_data": tl_data
        }

        for car in self.carObjects:
            # if car.pos not in self.endPositions:
            car_coords[car.unique_id] = {"x": car.pos[0] - 300, "z": car.pos[1] - 300, "direction": car.direction}

        for node in self.matrix:
            tl = self.matrix[node].trafficLights
            for direction in tl:
                id = tl[direction].unique_id
                state = tl[direction].state

                if direction == 'left':
                    tl_data[id] = {"x": self.matrix[node].pos[0] - 285, "z": self.matrix[node].pos[1] - 300, "y": 15, "state": state}
                elif direction == 'right':
                    tl_data[id] = {"x": self.matrix[node].pos[0] - 315, "z": self.matrix[node].pos[1] - 300, "y": 15, "state": state}
                elif direction == 'up':
                    tl_data[id] = {"x": self.matrix[node].pos[0] - 300, "z": self.matrix[node].pos[1] - 315, "y": 15, "state": state}
                elif direction == 'down':
                    tl_data[id] = {"x": self.matrix[node].pos[0] - 300, "z": self.matrix[node].pos[1] - 285, "y": 15, "state": state}

        return data