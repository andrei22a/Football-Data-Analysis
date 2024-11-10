import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import DataLoader
from Colors import *

def create_viewer():

    # Map label names to league values
    MAP_LEAGUES = {
        "Premier League": "premier-league",
        "La Liga": "la-liga",
        "Bundesliga": "bundesliga"
    }

    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    # Load the default data
    data = load_data(2022, "premier-league")
    df = data[1]

    # Create application main window
    root = tk.Tk()
    root.title("Football Stats Visualizer")
    root.geometry("1680x900")

    # Create a menu widget
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    # Create menu options
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Open")
    file_menu.add_command(label="Save")
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=file_menu)

    # Top frame for comboboxes
    top_frame = ttk.Frame(root)
    top_frame.pack(fill=tk.X, padx=10, pady=10)

    # Combobox label
    label = ttk.Label(top_frame, text="Select a league:")
    label.pack(side=tk.LEFT, padx=(0, 10))

    # Year combobox
    year_options = [2022, 2021, 2020]
    combo_year = ttk.Combobox(top_frame, values=year_options, state="readonly")
    combo_year.pack(side=tk.LEFT)
    combo_year.set(year_options[0]) # Default value

    # League combobox
    league_options = ["Premier League", "La Liga", "Bundesliga"]
    combo_league = ttk.Combobox(top_frame, values=league_options, state="readonly")
    combo_league.pack(side=tk.LEFT)
    combo_league.set(league_options[0]) # Default value

    # Callback function for combobox select event
    def on_select(event):
        nonlocal inner_frame
        nonlocal data
        inner_frame.destroy()
        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor=tk.NW)
        year = combo_year.get()
        league = MAP_LEAGUES[combo_league.get()]
        data = load_data(year, league)
        df = data[stats_type.get()]
        fill_df_canvas(df, inner_frame)

    # Frame for legend and actions
    actions_frame = ttk.Frame(root)
    actions_frame.pack(fill=tk.X, padx=10, pady=10)

    # Create legend
    create_legend_item(actions_frame, Colors.UCL, "Champions League")
    create_legend_item(actions_frame, Colors.UEL, "Europa League")
    create_legend_item(actions_frame, Colors.UECL, "Conference League")
    create_legend_item(actions_frame, Colors.REL, "Relegation")

    # Callback for radio buttons change event
    def on_change():
        nonlocal inner_frame
        nonlocal data
        inner_frame.destroy()
        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor=tk.NW)
        df = data[stats_type.get()]
        fill_df_canvas(df, inner_frame) 

    # Create radio buttons
    stats_type = tk.IntVar(value=1)
    radio1 = ttk.Radiobutton(actions_frame, text="Full", variable=stats_type, value=1, command=on_change)
    radio1.pack(side=tk.RIGHT)
    radio2 = ttk.Radiobutton(actions_frame, text="Reduced", variable=stats_type, value=0, command=on_change)
    radio2.pack(side=tk.RIGHT)

    # Load the data based on the combobox values
    combo_year.bind("<<ComboboxSelected>>", on_select)
    combo_league.bind("<<ComboboxSelected>>", on_select)
    
    # Frame for the DataFrame
    df_frame = ttk.Frame(root)
    df_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Canvas and scrollbars for the DataFrame
    canvas = tk.Canvas(df_frame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    vsb = ttk.Scrollbar(df_frame, orient=tk.VERTICAL, command=canvas.yview)
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=vsb.set)

    hsb = ttk.Scrollbar(root, orient=tk.HORIZONTAL, command=canvas.xview)
    hsb.pack(side=tk.BOTTOM, fill=tk.X)
    canvas.configure(xscrollcommand=hsb.set)

    canvas.bind_all("<MouseWheel>", on_mousewheel)

    # Inner frame for the DataFrame content
    inner_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor=tk.NW)

    # Fill canvas with DataFrame
    fill_df_canvas(df, inner_frame)

    # Update scroll bars
    inner_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    root.mainloop()

# Fetch local data based on year and league
def load_data(year, league):
    loader = DataLoader.DataLoader(year, league)
    data = loader.load_data()
    return data

# Load and resize team image
def load_image(url, size=(50, 50)):
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)

def create_legend_item(parent, color, text):
    item_frame = ttk.Frame(parent)
    item_frame.pack(side=tk.LEFT, padx=(0, 10))  # Alineación horizontal con espacio entre elementos
    
    color_square = tk.Canvas(item_frame, width=20, height=20, bg=color, highlightthickness=0)
    color_square.pack(side=tk.LEFT, padx=(0, 5))
    
    label = ttk.Label(item_frame, text=text)
    label.pack(side=tk.LEFT)

# Fill canvas with DataFrame data
def fill_df_canvas(df, frame):

    # Cell Styles
    style = ttk.Style()
    style.configure("Cell.TFrame", borderwidth=1, relief="solid")
    style.configure("Bold.TLabel", font=('Arial', 10, 'bold'))
    style.configure("Green.TFrame", background=Colors.UCL)
    style.configure("Blue.TFrame", background=Colors.UEL)
    style.configure("Orange.TFrame", background=Colors.UECL)
    style.configure("Red.TFrame", background=Colors.REL, color="white")

    # Create cells
    def create_cell(parent, content, is_header=False, is_bold=False, is_green=False, is_blue=False, is_orange=False, is_red=False):
        if is_green:
            cell_style = "Green.TFrame"
        elif is_blue:
            cell_style = "Blue.TFrame"
        elif is_orange:
            cell_style = "Orange.TFrame"
        elif is_red:
            cell_style = "Red.TFrame"
        else:
            cell_style = "Cell.TFrame"
        cell = ttk.Frame(parent, style=cell_style)
        if isinstance(content, ImageTk.PhotoImage):
            label = ttk.Label(cell, image=content)
            label.image = content
        else:
            if is_header:
                font = ('Arial', 10, 'bold')
            elif is_bold:
                style = "Bold.TLabel"
            else:
                font = ('Arial', 10)
            label = ttk.Label(cell, text=str(content), style=style if is_bold else "", font=font if not is_bold else None)
        label.pack(padx=5, pady=5, expand=True)
        return cell

    # Create header
    for col, header in enumerate(df.columns):
        cell = create_cell(frame, header, is_header=True)
        cell.grid(row=0, column=col, sticky="nsew")

    # Fill the fram with data
    for row, (index, data) in enumerate(df.iterrows(), start=1):
        for col, value in enumerate(data):
            if df.columns[col] == 'team_logo':
                try:
                    img = load_image(value)
                    cell_content = img
                except Exception as e:
                    cell_content = "Error de carga"
            else:
                cell_content = str(value)
            
            is_bold = df.columns[col] == "points"
            is_green = df.columns[col] == 'rank' and value in [1, 2, 3, 4]
            is_blue = df.columns[col] == 'rank' and value in [5, 6]
            is_orange = df.columns[col] == 'rank' and value in [7, 8]
            is_red = df.columns[col] == 'rank' and value in [18, 19, 20]

            cell = create_cell(frame, cell_content, is_bold=is_bold, is_green=is_green, is_blue=is_blue, is_orange=is_orange, is_red=is_red)
            cell.grid(row=row, column=col, sticky="nsew")

    # Configure row and column weight
    for i in range(len(df.index) + 1):
        frame.grid_rowconfigure(i, weight=1)
    for i in range(len(df.columns)):
        frame.grid_columnconfigure(i, weight=1)
