from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from model import EcoModel
import hashlib
from helper_classes import resource_finder


def colour_gen(word):
    # Use hashlib to create a hash value from the word using MD5
    hash_object = hashlib.md5(word.encode('utf-8'))
    hash_hex = hash_object.hexdigest()

    # Take the first 6 characters of the hash as the color code
    color_code = '#' + hash_hex[:6]

    return color_code


def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "Color": "pink",
        "Layer": 0,
        "r": 0.5,
        "text_color": "black",
        "text": f'''{round(agent.resources['food'],1)}={round(agent.money,1)}={round(agent.production,1)}''',
    }
    return portrayal


num_agents = 20

# Set up the grid
grid = CanvasGrid(agent_portrayal, 10, 10, 860, 200)


chart_data = [
    {"Label": "Total Money", "Color": colour_gen("Total Money")},
    {"Label": "Agents", "Color": colour_gen("Agents")},
    {"Label": "Average Money", "Color": colour_gen("Average Money")},
    {"Label": "Median Money", "Color": colour_gen("Median Money")},
    {"Label": "Total Trades", "Color": colour_gen("Total Trades")},
    {"Label": "Day Trades", "Color": colour_gen("Day Trades")},
    {"Label": "Average Price Assumption",
     "Color": colour_gen("Average Price Assumption")},
    {"Label": "avg_price_assumption_bottom",
     "Color": colour_gen("avg_price_assumption_bottom")},
    {"Label": "avg_price_assumption_top",
     "Color": colour_gen("avg_price_assumption_top")},
]

for resource in resource_finder():
    chart_data.append({"Label": resource+"_price",
                      "Color": colour_gen(resource)})

chart_element = ChartModule(
    chart_data
)

# Create and launch the server
server = ModularServer(
    EcoModel,
    [grid, chart_element, ],
    "Eco Simulation",
    {"width": 5, "height": 4, "num_agents": num_agents, }
)
server.port = 8521  # The default port number

# Start the server
server.launch()
