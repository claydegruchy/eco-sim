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
