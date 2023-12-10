from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from model import EcoModel, EcoAgent


def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "Color": "red",
        "Layer": 0,
        "r": 0.5,
        "text_color": "black",
        "text": f'''
Food: {round(agent.food,1)}, 
Money: {round(agent.money,1)}
Production: {round(agent.production,1)} ''',
        # Add the number of agents
        "num_agents": len(agent.model.schedule.agents)
    }
    return portrayal


# Set up the grid
grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)
chart_element = ChartModule(
    [
        {"Label": "Wolves", "Color": "#AA0000"},
        {"Label": "Sheep", "Color": "#666666"},
        {"Label": "Grass", "Color": "#00AA00"},
    ]
)

# Create and launch the server
server = ModularServer(
    EcoModel,
    [grid],
    "Eco Simulation",
    {"width": 10, "height": 10, "num_agents": 20}
)
server.port = 8521  # The default port number

# Start the server
server.launch()
