import os
import pandas as pd
import plotly.graph_objs as go
import streamlit as st


class DataAnalyzer:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.data_files = {}
        self.combined_data = {}
        self.statistics_data = {}

    def load_files(self):
        for file_name in os.listdir(self.folder_path):
            if file_name.endswith(".csv"):
                file_path = os.path.join(self.folder_path, file_name)
                self.data_files[file_name] = pd.read_csv(file_path, sep=";")

    def calculate_statistics(self):
        combined_stats = {}
        for file_name, df in self.data_files.items():
            if "y" in df.columns:
                y_column = df["y"]
                stats = y_column.describe().to_dict()
                combined_stats[file_name] = stats
            else:
                print(f"Warning: Column 'y' not found in file {file_name}. Skipping.")
        self.statistics_data = combined_stats

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
        st.sidebar.header("Select Plots and Customize Names")
        selected_plots = {}
        custom_names = {}
        show_in_table = {}

        for trace in combined_traces:
            custom_name = st.sidebar.text_input(
                f"Custom name for {trace.name}", trace.name, key=f"{trace.name}_custom"
            )
            with st.sidebar.expander(f"{custom_name} Options", expanded=True):
                is_selected = st.checkbox(
                    f"Show {custom_name} in Graph",
                    value=True,
                    key=f"{trace.name}_graph",
                )
                is_in_table = st.checkbox(
                    f"Show {custom_name} in Table",
                    value=True,
                    key=f"{trace.name}_table",
                )
                selected_plots[trace.name] = is_selected
                show_in_table[trace.name] = is_in_table
                custom_names[trace.name] = custom_name
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
            xaxis=dict(title=x_title, type=x_scale, showgrid=show_grid),
            yaxis=dict(title=y_title, type=y_scale, showgrid=show_grid),
            showlegend=show_legend,
        )
        st.plotly_chart(fig, use_container_width=True)
        st.header("Statistics Table")
        if self.statistics_data:
            table_data = []
            for original_name, stats in self.statistics_data.items():
                if show_in_table.get(original_name, False):
                    display_name = custom_names.get(original_name, original_name)
                    stats_row = {"File": display_name, **stats}
                    table_data.append(stats_row)

            if table_data:
                stats_df = pd.DataFrame(table_data)
                styled_df = (
                    stats_df.style.set_table_styles(
                        [
                            {
                                "selector": "th",
                                "props": [
                                    ("background-color", "#4CAF50"),
                                    ("color", "white"),
                                ],
                            },
                            {
                                "selector": "tbody td",
                                "props": [
                                    ("border", "1px solid #ddd"),
                                    ("padding", "8px"),
                                ],
                            },
                        ]
                    )
                    .highlight_max(color="lightgreen")
                    .highlight_min(color="lightcoral")
                    .format(precision=2)
                    .set_properties(
                        **{
                            "background-color": "#f9f9f9",
                            "color": "#333",
                            "font-size": "14px",
                        }
                    )
                )
                st.write(styled_df.to_html(), unsafe_allow_html=True)
            else:
                st.write(
                    "No statistics to display. Please enable some files to view statistics."
                )


folder_path = r"scratches"
analyzer = DataAnalyzer(folder_path)
analyzer.load_files()
analyzer.calculate_statistics()
analyzer.create_streamlit_app()
