from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model import EcoModel, EcoAgent


def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "Color": "red",
        "Layer": 0,
        "r": 0.5,
        "text": f"Food: {round(agent.food,1)}",
        "num_agents": len(agent.model.schedule.agents)  # Add the number of agents
    }
    return portrayal


# Set up the grid
grid = CanvasGrid(agent_portrayal, 10, 10, 200, 200)

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
