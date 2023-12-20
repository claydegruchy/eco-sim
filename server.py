from mesa.visualization.modules import CanvasGrid, ChartModule, PieChartModule
from mesa.visualization.ModularVisualization import ModularServer
from report_helpers import table_style, ColourMaker, chart, agent_table_generator, EventReport, PandasChartElement, TableElement, SimpleText
import math
import pandas as pd
from model import EcoModel
import hashlib
from agent_role_config import resource_finder, roles


def colour_gen(word):
    hash_object = hashlib.md5(word.encode('utf-8'))
    return [int(hash_object.hexdigest()[:2], 16), int(hash_object.hexdigest()[2:4], 16), int(hash_object.hexdigest()[4:6], 16)]


def colour_str(word, tint=1):
    s = colour_gen(word)
    s = [clamp(int(x*tint), 0, 255) for x in s]
    return f"rgb({s[0]},{s[1]},{s[2]})"


def clamp(n, minn, maxn): return max(min(maxn, n), minn)


def agent_portrayal(agent):
    money = (agent.money/100)+0.5  # clamp(int(agent.money), 0, 255)/255
    food = clamp(clamp(int(agent.get_resource('food')), 0, 255)/20, 0, 1)
    role = colour_gen(agent.role.name)
    portrayal = {
        # "Shape": "circle",
        # "r": 0.5,

        "Shape": "rect",
        "w": max(food, 0.1),
        "h": 0.9,
        # "xAlign": 10,
        # "yAlign": 10,


        "Filled": "false",
        # "Color": f"red",
        "Color": f"rgba({role[0]},{role[1]}, {role[2]}, {max(money, 0.1)})",
        "Layer": 0,
        # "text_color": "rgb(255, 255, 0)",
        "text_color": "black",



        "text": f'''{agent.role}:{round(agent.money,1)}''',
    }
    return portrayal


num_agents = 30
print("[Server]", "setting up", num_agents, "agents")
# trade report
print("[Server]", "setting up trade report")
trade_report_data = [
    {"Label": "Day Trades", "Color": colour_str("Day Trades")},
    {"Label": "Day Trade Quantity", "Color": colour_str("Day Trade Quantity")},

]

trade_report_colours = ColourMaker()


# production statistics
print("[Server]", "setting up production statistics")
chart_production_data = []


for resource in resource_finder():
    trade_report_data.append({"Label": resource+"_price",
                             "Color": trade_report_colours.selected(0.5)})

    trade_report_data.append({"Label": resource+"_avg_assummed",
                             "Color": trade_report_colours.selected(1)})
    trade_report_colours.next()
    chart_production_data.append(
        {"Label": resource+"_production", "Color": colour_str(resource)})


chart_production = ChartModule(chart_production_data)


# agnet report
print("[Server]", "setting up agent report")
agent_report_data = [
    {"Label": "Agents", "Color": colour_str("Agents")},
    # {"Label": "Dead Agents", "Color": colour_str("Dead Agents")},
]
for role in roles:
    agent_report_data.append({"Label": role.name+"_count",
                              "Color": colour_str(role.name)})
# event report
print("[Server]", "setting up event report")
event_reporter = EventReport()

trade_report = ChartModule(trade_report_data)
agent_report = ChartModule(agent_report_data)
event_report = TableElement(lambda m: event_reporter.get_events())

# role distribution pie chart
print("[Server]", "setting up role distribution pie chart")
pie_chat = PieChartModule(
    [{"Label": role.name+"_count",
        "Color": colour_str(role.name)} for role in roles]
)

# simple, high level KPIs
print("[Server]", "setting up simple, high level KPIs")
simple_kpis = SimpleText(lambda m: f"Dead Agents: {len(m.dead_agents)}")

# breakdown of agent stats
print("[Server]", "setting up agent stat table")
table_agent_stats = TableElement(
    lambda m: agent_table_generator(m)
)


# general stats needed for engine
print("[Server]", "setting up engine stats")
width = int(math.sqrt(num_agents))
height = int(num_agents / width) + 1
grid = CanvasGrid(agent_portrayal, 10, 10, 800, 500)


print("[Server]", "setting up w/h", width, height)

# Create and launch the server
server = ModularServer(
    EcoModel,
    [
        # test,
        event_report,
        simple_kpis,
        table_agent_stats,
        chart_production,
        trade_report,
        grid,
        agent_report,
        pie_chat,
    ],
    "Eco Simulation",
    {
        "width": width,
        "height": height,
        "num_agents": num_agents,
        "event_reporter": event_reporter
    }
)
server.port = 8521  # The default port number

# Start the server
server.launch()
