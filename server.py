from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from model import EcoModel
# from agent import EcoAgent


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


num_agents = 20

# Set up the grid
grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)

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
        # Average Price Assumption
        {"Label": "Average Price Assumption", "Color": "#0A0000"},
        # avg_price_assumption_bottom
        {"Label": "avg_price_assumption_bottom", "Color": "#0B0000"},
        # avg_price_assumption_top
        {"Label": "avg_price_assumption_top", "Color": "#B00000"},




    ]
)

# Create and launch the server
server = ModularServer(
    EcoModel,
    [grid, chart_element],
    "Eco Simulation",
    {"width": 5, "height": 4, "num_agents": num_agents, }
)
server.port = 8521  # The default port number

# Start the server
server.launch()
