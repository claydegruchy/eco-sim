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


def clamp(n, minn, maxn): return max(min(maxn, n), minn)


# For Rectangles:
# "w", "h": The width and height of the rectangle, which are in
#             fractions of cell width and height.
# "xAlign", "yAlign": Alignment of the rectangle within the
#                     cell. Defaults to 0.5 (center).

def agent_portrayal(agent):
    m = clamp(int(agent.money), 0, 255)

    # agents who have a lot of money are green
    # this operates on a sliding scale to red where they are broke

    portrayal = {
        # "Shape": "circle",
        # "r": 0.5,

        "Shape": "rect",
        "w": 1,
        "h": 1,
        # "xAlign": 10,
        # "yAlign": 10,


        "Filled": "false",
        # "Color": f"red",
        "Color": f"rgba({m},{m}, 0, 0.5)",
        "Layer": 0,
        # "text_color": "rgb(255, 255, 0)",
        "text_color": "black",



        "text": f'''{round(agent.resources['food'],1)}={round(agent.money,1)}={round(agent.production,1)}''',
    }
    return portrayal


num_agents = 20

# Set up the grid
grid = CanvasGrid(agent_portrayal, 10, 10, 800, 500)


chart_data = [
    # {"Label": "Total Money", "Color": colour_gen("Total Money")},
    {"Label": "Agents", "Color": colour_gen("Agents")},
    # {"Label": "Average Money", "Color": colour_gen("Average Money")},
    # {"Label": "Median Money", "Color": colour_gen("Median Money")},
    {"Label": "Total Trades", "Color": colour_gen("Total Trades")},
    {"Label": "Day Trades", "Color": colour_gen("Day Trades")},
]

for resource in resource_finder():
    if resource != "food":
        continue
    chart_data.append({"Label": resource+"_price",
                      "Color": colour_gen(resource+"_price")})

    chart_data.append({"Label": resource+"_avg_assummed",
                      "Color": colour_gen(resource+"_avg_assummed")})

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
