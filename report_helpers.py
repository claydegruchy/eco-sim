
import base64
import io


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
