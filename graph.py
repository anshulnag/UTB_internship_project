import os
import zipfile
from io import BytesIO
import pandas as pd
import plotly.graph_objs as go
import streamlit as st


class DataAnalyzer:
    def __init__(self):
        self.data_files = {}
        self.combined_data = {}
        self.statistics_data = {}
        self.excluded_files = (
            set()
        )  # Keeps track of files excluded from last Y statistics

    def add_uploaded_files(self, uploaded_files):
        for uploaded_file in uploaded_files:
            try:
                df = pd.read_csv(uploaded_file, sep=";")
                file_name = uploaded_file.name
                self.data_files[file_name] = df

                if "y" in df.columns:
                    y_column = df["y"]
                    stats = y_column.describe().to_dict()
                    self.statistics_data[file_name] = stats
                else:
                    st.warning(
                        f"Warning: Column 'y' not found in the file '{file_name}'."
                    )
            except Exception as e:
                st.error(f"Error processing file '{uploaded_file.name}': {e}")

    def add_uploaded_folder(self, uploaded_zip):
        try:
            # Extract the uploaded zip file
            with zipfile.ZipFile(BytesIO(uploaded_zip.read()), "r") as zip_ref:
                zip_ref.extractall("uploaded_folder")

            # Process all CSV files in the extracted folder
            extracted_files = [
                f for f in os.listdir("uploaded_folder") if f.endswith(".csv")
            ]
            for file_name in extracted_files:
                file_path = os.path.join("uploaded_folder", file_name)
                df = pd.read_csv(file_path, sep=";")
                self.data_files[file_name] = df

                if "y" in df.columns:
                    y_column = df["y"]
                    stats = y_column.describe().to_dict()
                    self.statistics_data[file_name] = stats
                else:
                    st.warning(
                        f"Warning: Column 'y' not found in the file {file_name}."
                    )
        except Exception as e:
            st.error(f"Error processing uploaded folder: {e}")

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

    def calculate_last_y_statistics(self):
        all_last_y_values = []
        for file_name, df in self.data_files.items():
            if file_name not in self.excluded_files:  # Only include files not excluded
                if "y" in df.columns:
                    last_y_value = df["y"].iloc[-1]
                    all_last_y_values.append(last_y_value)

        if all_last_y_values:
            combined_last_y_series = pd.Series(all_last_y_values)
            last_y_stats = combined_last_y_series.describe().to_dict()
            return pd.DataFrame(
                {
                    "Statistic": last_y_stats.keys(),
                    "Value": last_y_stats.values(),
                }
            )
        else:
            return pd.DataFrame(columns=["Statistic", "Value"])

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
        st.title("Interactive Combined Graph Dashboard")
        st.sidebar.header("Upload Files")

        uploaded_files = st.sidebar.file_uploader(
            "Upload multiple CSV files", type="csv", accept_multiple_files=True
        )
        if uploaded_files:
            self.add_uploaded_files(uploaded_files)

        st.sidebar.header("Upload Folder")
        uploaded_zip = st.sidebar.file_uploader(
            "Upload a ZIP folder of CSV files", type="zip"
        )
        if uploaded_zip:
            self.add_uploaded_folder(uploaded_zip)

        combined_traces = self.create_combined_trace()
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
                exclude_from_last_y = st.checkbox(
                    f"Exclude {custom_name} from Last Y Statistics",
                    value=False,
                    key=f"{trace.name}_exclude",
                )

                if exclude_from_last_y:
                    self.excluded_files.add(trace.name)
                else:
                    self.excluded_files.discard(trace.name)

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

        st.header("Combined Last Y Value Statistics")
        last_y_stats = self.calculate_last_y_statistics()
        if not last_y_stats.empty:
            st.write("Statistics of the last Y values from all files combined:")
            st.table(last_y_stats)
        else:
            st.write("No last Y value statistics available. Please upload valid files.")


# Instantiate and Run the App
analyzer = DataAnalyzer()
analyzer.create_streamlit_app()
