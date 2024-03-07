header_height = "4rem"
content_height = "90vh"
footer_position = "96vh"
footer_height = "4vh"
sidebar_width = "12vw"
parkrun_purple = "#2b233d"
parkrun_purple_lighter = "#d1cae1" #"#afa3ca"

tab_height = '5vh'

HEADER_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "right": 0,
    "height": header_height,
    "padding": "1rem 1rem",
    "background-color": parkrun_purple,
    "color": "#FFFFFF"
}

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": header_height,
    "left": 0,
    "bottom": 0,
    "width": sidebar_width,
    "padding": "1rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "position": "fixed",
    "top": header_height,
    "height": content_height,
    "width": "100vw",
    # "margin-left": sidebar_width,
    "padding": "1rem 1rem",
    "overflowY": "scroll"
}

FOOTER_STYLE = {
    "position": "fixed",
    "top": footer_position,
    "left": 0,
    "right": 0,
    "height": footer_height,
    "padding": "1rem 1rem",
    # "background-color": parkrun_purple_lighter,
}