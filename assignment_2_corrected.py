import os
import pandas as pd
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import json
from PIL import Image


class DataAnalyzer:

    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.data_files = {}

    def load_files(self):
        for file_name in os.listdir(self.folder_path):
            if file_name.endswith(".csv"):
                file_path = os.path.join(self.folder_path, file_name)
                self.data_files[file_name] = pd.read_csv(file_path, sep=";")
        print(f"Loaded {len(self.data_files)} CSV files from {self.folder_path}")

    def save_statistics(self, output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        combined_stats = {}
        json_path = os.path.join(output_dir, "statistics.json")
        for file_name, df in self.data_files.items():
            if "y" in df.columns:
                y_column = df["y"]
                stats = y_column.describe().to_dict()
                combined_stats[file_name] = stats
            else:
                print(f"Warning: Column 'y' not found in file {file_name}. Skipping.")
        with open(json_path, "w") as json_file:
            json.dump(combined_stats, json_file, indent=4)

        print("statistics has been saved")

    def save_images(self, output_dir, values=100):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        combined_fig, combined_ax = plt.subplots()
        for file_name, df in self.data_files.items():
            fig, ax = plt.subplots()
            x_values = df["x"].tail(values)
            y_values = df["y"].tail(values)
            ax.plot(x_values, y_values, label=file_name, marker="o")
            for x, y in zip(x_values, y_values):
                ax.vlines(x=x, ymin=0, ymax=y, colors="gray", linestyles="dotted")
                ax.hlines(y=y, xmin=0, xmax=x, colors="gray", linestyles="dotted")

            ax.set_xlabel("X-axis")
            ax.set_ylabel("Y-axis")
            ax.legend(loc="best")
            image_path = os.path.join(
                output_dir, f"graph_{file_name.split('.')[0]}.png"
            )
            fig.savefig(image_path)
            plt.close(fig)
            combined_ax.plot(x_values, y_values, label=file_name, marker="o")

        combined_ax.set_xlabel("X-axis")
        combined_ax.set_ylabel("Y-axis")
        combined_ax.set_title("Combined Convergence Graph")
        combined_ax.legend(loc="best")

        combined_image_path = os.path.join(output_dir, "combined_convergence.png")
        combined_fig.savefig(combined_image_path)
        plt.close(combined_fig)

        images = [f for f in os.listdir(output_dir) if f.endswith(".png")]
        loaded_images = [Image.open(os.path.join(output_dir, img)) for img in images]
        widths, heights = zip(*(i.size for i in loaded_images))
        total_width = max(widths)
        total_height = sum(heights)
        combined_image = Image.new("RGB", (total_width, total_height))

        y_offset = 0
        for img in loaded_images:
            combined_image.paste(img, (0, y_offset))
            y_offset += img.height

        combined_image.save(
            os.path.join(output_dir, "combined_convergence_stacked.png")
        )
        print("graph images has been saved")


folder_path = r"C:\Users\nagan\OneDrive\Desktop\Internship_project\scratches"
output_directory = r"C:\Users\nagan\OneDrive\Desktop\Internship_project\output"
analyzer = DataAnalyzer(folder_path)
analyzer.load_files()
analyzer.save_statistics(output_directory)
analyzer.save_images(output_directory)
