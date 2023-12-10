from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from model import EcoModel, EcoAgent
import random


def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "Color": "red",
        "Layer": 0,
        "r": 0.5,
        "text_color": "black",
        "text": f'''{round(agent.food,1)}={round(agent.money,1)}={round(agent.production,1)}''',
    }
    return portrayal


num_agents = 8

# Set up the grid
grid = CanvasGrid(agent_portrayal, 10, 10, 700, 700)

chart_element = ChartModule(
    [
        {"Label": "Total Money", "Color": "#AA0000"},
        {"Label": "Agents", "Color": "#AA00AA"},
        {"Label": "Average Money", "Color": "#AAAAAA"},
        {"Label": "Median Money", "Color": "#00AA00"},
        # Total Trades
        {"Label": "Total Trades", "Color": "#00A0AA"},
        # Day Trades
        {"Label": "Day Trades", "Color": "#00000A"},




    ]
)

# Create and launch the server
server = ModularServer(
    EcoModel,
    [grid, chart_element],
    "Eco Simulation",
    {"width": 2, "height": 4, "num_agents": num_agents, }
)
server.port = 8521  # The default port number

# Start the server
server.launch()
