import os
import pandas as pd
import plotly.graph_objs as go
import streamlit as st


class DataAnalyzer:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.data_files = {}
        self.combined_data = {}

    def load_files(self):


        self.combined_data = {} 

    def load_files(self):
        

        for file_name in os.listdir(self.folder_path):
            if file_name.endswith(".csv"):
                file_path = os.path.join(self.folder_path, file_name)
                self.data_files[file_name] = pd.read_csv(file_path, sep=";")

    def create_combined_trace(self, values=100):

        traces = []
        for file_name, df in self.data_files.items():
            x_values = df["x"].tail(values)
            y_values = df["y"].tail(values)
            trace = go.Scatter(
                x=x_values, y=y_values, mode="lines+markers", name=file_name
            )
            traces.append(trace)
            self.combined_data[file_name] = trace
        return traces

    def create_streamlit_app(self):

        combined_traces = self.create_combined_trace()

        st.title("Interactive Combined Graph Dashboard")

        st.sidebar.header("Graph Customization")

        x_scale = st.sidebar.radio("X-axis Scale", ["linear", "log"])
        y_scale = st.sidebar.radio("Y-axis Scale", ["linear", "log"])

        x_title = st.sidebar.text_input("Custom X-axis Title", "X-axis")
        y_title = st.sidebar.text_input("Custom Y-axis Title", "Y-axis")

        show_grid = st.sidebar.checkbox("Show Grid", value=True)
        show_legend = st.sidebar.checkbox("Show Legend", value=True)

        
        st.sidebar.header("Graph Customization")

       
        x_scale = st.sidebar.radio("X-axis Scale", ["linear", "log"])
        y_scale = st.sidebar.radio("Y-axis Scale", ["linear", "log"])

        
        x_title = st.sidebar.text_input("Custom X-axis Title", "X-axis")
        y_title = st.sidebar.text_input("Custom Y-axis Title", "Y-axis")

     
        show_grid = st.sidebar.checkbox("Show Grid", value=True)
        show_legend = st.sidebar.checkbox("Show Legend", value=True)


        st.sidebar.header("Select Plots to Display and Customize Names")
        selected_plots = {}
        custom_names = {}


        for trace in combined_traces:
            with st.sidebar.expander(f"{trace.name} Options", expanded=True):
                is_selected = st.checkbox(f"Show {trace.name}", value=True)
                custom_name = st.text_input(f"Custom name for {trace.name}", trace.name)

                selected_plots[trace.name] = is_selected
                custom_names[trace.name] = custom_name


        fig = go.Figure()

        for trace in combined_traces:
            if selected_plots[trace.name]:

        fig = go.Figure()

        for trace in combined_traces:
            if selected_plots[trace.name]: 

                line_name = (
                    custom_names[trace.name] if custom_names[trace.name] else trace.name
                )
                fig.add_trace(
                    go.Scatter(
                        x=trace.x, y=trace.y, mode="lines+markers", name=line_name
                    )
                )

        fig.update_layout(
            title="Combined Convergence Graph",
            xaxis=dict(
                title=x_title,
                type=x_scale,
                showgrid=show_grid,
            ),
            yaxis=dict(
                title=y_title,
                type=y_scale,
                showgrid=show_grid,
            ),
            showlegend=show_legend,
        )

        st.plotly_chart(fig, use_container_width=True)

folder_path = r"scratches"  
analyzer = DataAnalyzer(folder_path)
analyzer.load_files()
analyzer.create_streamlit_app()
