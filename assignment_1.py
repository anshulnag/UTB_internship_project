import pandas as pd
import os
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly as py
import plotly.io as pio
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import warnings

warnings.filterwarnings("ignore")


class DataAnalyzer:

    def __init__(self, folder_path):

        self.folder_path = folder_path

    def basic_statistics(self):

        for file_name in os.listdir(self.folder_path):
            if file_name.endswith(".csv"):
                file_path = os.path.join(self.folder_path, file_name)
                df = pd.read_csv(file_path)
                print(f"\nFile: {file_name}")
                print(df.describe())

    def convergence_graph(self, values=100):

        for file_name in os.listdir(self.folder_path):
            if file_name.endswith(".csv"):
                file_path = os.path.join(self.folder_path, file_name)
                df = pd.read_csv(file_path)
                fig = go.Figure(go.Scatter(x=df.x.tail(values), y=df.y.tail(values)))
                fig.update_xaxes(title_text="x")
                fig.update_yaxes(title_text="y")
                fig.update_layout(title=file_name)
                fig.show()


folder_path = r"C:\Users\nagan\OneDrive\Desktop\Internship_project\scratches"

analyzer = DataAnalyzer(folder_path)
analyzer.basic_statistics()
analyzer.convergence_graph()
