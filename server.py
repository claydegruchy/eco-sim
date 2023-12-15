from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from model import EcoModel
import hashlib
from helper_classes import resource_finder


def colour_gen(word):
    # Use hashlib to create a hash value from the word using MD5
    hash_object = hashlib.md5(word.encode('utf-8'))

    # convert to rgb

    return [int(hash_object.hexdigest()[:2], 16), int(hash_object.hexdigest()[2:4], 16), int(hash_object.hexdigest()[4:6], 16)]


def colour_str(word):
    s = colour_gen(word)

    return f"rgb({s[0]},{s[1]},{s[2]})"


def clamp(n, minn, maxn): return max(min(maxn, n), minn)


# For Rectangles:
# "w", "h": The width and height of the rectangle, which are in
#             fractions of cell width and height.
# "xAlign", "yAlign": Alignment of the rectangle within the
#                     cell. Defaults to 0.5 (center).


def agent_portrayal(agent):
    money = (agent.money/100)+0.5  # clamp(int(agent.money), 0, 255)/255
    food = clamp(clamp(int(agent.get_resource('food')), 0, 255)/20, 0, 1)
    role = colour_gen(agent.role.name)
    # print(role, food)

    # agents who have a lot of money are green
    # this operates on a sliding scale to red where they are broke

    portrayal = {
        # "Shape": "circle",
        # "r": 0.5,

        "Shape": "rect",
        "w": food,
        "h": 0.9,
        # "xAlign": 10,
        # "yAlign": 10,


        "Filled": "false",
        # "Color": f"red",
        "Color": f"rgba({role[0]},{role[1]}, {role[2]}, {money})",
        "Layer": 0,
        # "text_color": "rgb(255, 255, 0)",
        "text_color": "black",



        "text": f'''{agent.unique_id}:{round(agent.production,1)}''',
    }
    return portrayal


num_agents = 20

# Set up the grid
grid = CanvasGrid(agent_portrayal, 10, 10, 800, 500)


chart_data = [
    # {"Label": "Total Money", "Color": colour_str("Total Money")},
    {"Label": "Agents", "Color": colour_str("Agents")},
    # {"Label": "Average Money", "Color": colour_str("Average Money")},
    # {"Label": "Median Money", "Color": colour_str("Median Money")},
    # {"Label": "Total Trades", "Color": colour_str("Total Trades")},
    {"Label": "Day Trades", "Color": colour_str("Day Trades")},
]

for resource in resource_finder():
    if resource != "food":
        continue
    chart_data.append({"Label": resource+"_price",
                      "Color": colour_str(resource+"_price")})

    chart_data.append({"Label": resource+"_avg_assummed",
                      "Color": colour_str(resource+"_avg_assummed")})
    chart_data.append({"Label": resource+"_median_assummed",
                      "Color": colour_str(resource+"_median_assummed")})


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
