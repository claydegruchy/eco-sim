import pandas as pd
from mesa.visualization.modules import TextElement
import base64
import io
from agent_role_config import resource_finder, roles


def chart(df):
    my_stringIObytes = io.BytesIO()
    df.plot(title="DataFrame Plot").figure.savefig(
        my_stringIObytes, format='jpg')
    my_stringIObytes.seek(0)
    my_base64_jpgData = base64.b64encode(my_stringIObytes.read()).decode()
    return '<img src="data:image/png;base64, {}">'.format(my_base64_jpgData)


def table_style(df):
    return f'''<html>
    <head>
    <style> 
    table, th, td {{font-size:10pt; border:1px solid black; border-collapse:collapse; text-align:left;}}
    th, td {{padding: 5px;}}
    </style>
    </head>
    <body>
    {
    df.to_html()
    }
    </body>
    </html>'''


def colour_list(N):
    return [f"rgba(230,25,75,{N})",
            f"rgba(60,180,75,{N})",
            f"rgba(255,225,25,{N})",
            f"rgba(67,99,216,{N})",
            f"rgba(245,130,49,{N})",
            f"rgba(145,30,180,{N})",
            f"rgba(70,240,240,{N})",
            f"rgba(240,50,230,{N})",
            f"rgba(188,246,12,{N})",
            f"rgba(250,190,190,{N})",
            f"rgba(0,128,128,{N})",
            f"rgba(230,190,255,{N})",
            f"rgba(154,99,36,{N})",
            f"rgba(255,250,200,{N})",
            f"rgba(128,0,0,{N})",
            f"rgba(170,255,195,{N})",
            f"rgba(128,128,0,{N})",
            f"rgba(255,216,177,{N})",
            f"rgba(0,0,117,{N})",
            f"rgba(128,128,128,{N})",
            f"rgba(255,255,255,{N})",
            f"rgba(0,0,0,{N})",]


class ColourMaker:
    def __init__(self):
        self.current = 0

    def selected(self, N):
        return colour_list(N)[self.current]

    def next(self):
        self.current += 1
        if self.current > len(colour_list(1)):
            self.current = 0

    def reset(self):
        self.current = 0


selected_agent_stats = ['age', 'money',
                        'production',
                        'last_production', 'last_trade', 'last_order_count']
agent_resources = list(resource_finder())


def highlight_max(s):
    '''
    highlight the maximum in a Series yellow.
    '''
    is_max = s == s.max()
    return ['background-color: yellow' if v else '' for v in is_max]

# a function that returns red if lowest, green if highest, and white otherwise.


def color_red_or_green(val):
    if val == val.min():
        color = 'red'
    elif val == val.max():
        color = 'green'
    else:
        color = 'white'
    return ['background-color: %s' % color for v in val]


def agent_table_generator(m):
    frame = pd.DataFrame([[a.unique_id, a.role.name] +
                         [a.get_stat(stat) for stat in selected_agent_stats] +
                         [a.get_resource(
                             res) for res in agent_resources]
                         for a in m.schedule.agents],
                         columns=["id", "role",]+selected_agent_stats+agent_resources) \
        .style.map(lambda x: 'background-color : red' if x < 5 else 'background-color : green', subset=['food'])\
        .map(lambda x: 'background-color : yellow' if x < 15 and x > 5 else '', subset=['food'])\


    for resource in agent_resources:
        frame.map(
            lambda x: 'background-color : LightGray' if x == 0 else '', subset=[resource])

    return frame

    # style food column red if under 5, green if over 15, yellow if between
    # .map(lambda x: 'background-color : yellow' if x < 15 and x > 5 else '', subset=['food'])


class EventReport:
    def __init__(self,):
        self.events = [["Server", "Server started."]]

    def add_event(self, actor, text):
        self.events.append([actor, text])

    def get_events(self):
        # return the last 10 events
        return pd.DataFrame(self.events[-10:], columns=["Actor", "Event"])


class PandasChartElement(TextElement):
    def __init__(self, lambda_data):
        self.lambda_data = lambda_data

    def render(self, model):
        return chart(self.lambda_data(model))


class TableElement(TextElement):
    def __init__(self, lambda_data):
        self.lambda_data = lambda_data

    def render(self, model):
        return table_style(self.lambda_data(model))


class SimpleText(TextElement):
    def __init__(self, lambda_data):
        self.lambda_data = lambda_data

    def render(self, model):
        return self.lambda_data(model)
