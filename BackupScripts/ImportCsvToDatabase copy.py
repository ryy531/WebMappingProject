import pandas as pd
import geopandas
from sqlalchemy import create_engine
from sqlalchemy import text
import time
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os


class RootWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Import CSV to Database")

        self.csv_file_path = None
        self.database_username_entry = None
        self.database_password_entry = None
        self.database_host_entry = None
        self.database_port_entry = None
        self.database_database_name_entry = None
        self.output_table_entry = None

        main_frame = ttk.Frame(self, padding=10)

        input_csv_lable = ttk.Label(main_frame, text="choose your csv file")
        input_csv_lable.grid(row=0, column=0, padx=5, pady=5)
        self.input_csv_path_lable = ttk.Label(main_frame, text="No file choose")
        self.input_csv_path_lable.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(main_frame, text="Browse", command=self.select_input_csv).grid(
            row=0, column=2, padx=5, pady=5
        )

        # Create Lables
        input_username_lable = ttk.Label(main_frame, text="user name")
        input_username_lable.grid(row=1, column=0, padx=5, pady=5)
        self.database_username_entry = ttk.Entry(main_frame)
        self.database_username_entry.grid(row=1, column=1, padx=1, pady=5)
        # password lable
        input_password_lable = ttk.Label(main_frame, text="password")
        input_password_lable.grid(row=2, column=0, padx=5, pady=5)
        self.database_password_entry = ttk.Entry(main_frame, show="*")
        self.database_password_entry.grid(row=2, column=1, padx=1, pady=5)
        # host lable
        input_host_lable = ttk.Label(main_frame, text="host")
        input_host_lable.grid(row=3, column=0, padx=5, pady=5)
        self.database_host_entry = ttk.Entry(main_frame)
        self.database_host_entry.grid(row=3, column=1, padx=1, pady=5)
        # port lable
        input_port_lable = ttk.Label(main_frame, text="port")
        input_port_lable.grid(row=4, column=0, padx=5, pady=5)
        self.database_port_entry = ttk.Entry(main_frame)
        self.database_port_entry.grid(row=4, column=1, padx=1, pady=5)
        self.database_port_entry.insert(0, "5432")
        # database name
        input_database_name = ttk.Label(main_frame, text="database name")
        input_database_name.grid(row=5, column=0, padx=5, pady=5)
        self.database_database_name_entry = ttk.Entry(main_frame)
        self.database_database_name_entry.grid(row=5, column=1, padx=1, pady=5)
        # table name
        output_table_name = ttk.Label(main_frame, text="output table name")
        output_table_name.grid(row=6, column=0, padx=5, pady=5)
        self.output_table_entry = ttk.Entry(main_frame)
        self.output_table_entry.grid(row=6, column=1, padx=1, pady=5)

        # import button

        ttk.Button(main_frame, text="Start Import", command=self.start_import).grid(
            row=7, columnspan=3, padx=5, pady=5
        )

        # Status lable
        self.status_label = ttk.Label(main_frame, text="Waiting for import...")
        self.status_label.grid(row=8, columnspan=3, padx=5, pady=5)

        main_frame.pack(fill="both", expand=True)

    def select_input_csv(self):
        csv_file_path = filedialog.askopenfilename(
            title="Select csv file you want to upload",
            filetypes=[("CSV files", "*.csv")],
            parent=self,
        )
        if csv_file_path:
            self.csv_file_path = csv_file_path
            self.output_table_entry.delete(0, tk.END)
            self.output_table_entry.insert(0, os.path.basename(csv_file_path))
            self.input_csv_path_lable.config(text=csv_file_path)
        else:
            self.csv_file_path = None
            self.input_csv_path_lable.config(text="No file choose")

    # main import logic
    def start_import(self):
        csv_path = self.csv_file_path
        username = self.database_username_entry.get()
        password = self.database_password_entry.get()
        host = self.database_host_entry.get()
        port = self.database_port_entry.get()
        database_name = self.database_database_name_entry.get()
        output_table = self.output_table_entry.get()

        required_inputs = [
            (csv_path, "Please choose the CSV file you want upload!"),
            (username, "Please input database username"),
            (host, "Please input database host address"),
            (port, "Please input database port number"),
            (database_name, "Please input database name"),
            (output_table, "Please choose the output table name"),
        ]

        for input_value, error_message in required_inputs:
            if not input_value:
                tk.messagebox.showerror("Input error!", error_message)
                return

        if password:
            database_connection_str = (
                f"postgresql://{username}:{password}@{host}:{port}/{database_name}"
            )

        else:
            database_connection_str = (
                f"postgresql://{username}@{host}:{port}/{database_name}"
            )

        print("All input passed")
        print(
            f"database connection string (not include password): postgresql://{username}@{host}:{port}/{database_name}"
        )
        print(f"output table name : {output_table}")

        try:
            new_engine = create_engine(database_connection_str)
            with new_engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print("Database engine created and connection tested.")
        except Exception as e:
            tk.messagebox.showerror("Error!", e)
            return
        self.status_label.config(text="Database connected!")

        # read CSV
        try:
            self.status_label.config(text=f"Start to read CSV file")
            df = pd.read_csv(csv_path)
        except FileNotFoundError:
            self.status_label.config(text=f"file{csv_path} not found!")
            tk.messagebox.showerror(
                "File Error!", f"Cannot find CSV file '{csv_path}'!"
            )
            return
        except pd.errors.EmptyDataError:
            self.status_label.config(text=f"file{csv_path} was empty!")
            tk.messagebox.showerror("File Error!", f"Empty CSV file '{csv_path}'!")
            return
        except pd.errors.ParserError:
            self.status_label.config(text=f"file{csv_path} parser not correct!")
            tk.messagebox.showerror(
                "File Error!", f"Wrong parser of CSV file '{csv_path}'!"
            )
            return
        except Exception as e:
            self.status_label.config(text=f"failed to read CSV file!")
            tk.messagebox.showerror("Error!", e)
            return
        self.status_label.config(text=f"CSV file loaded! Read {len(df)} rows!")

        # Transfer df to geo pandas frame
        try:
            self.status_label.config(text=f"Start transform to geo data frame")
            geo_data_frame = geopandas.GeoDataFrame(
                df, crs="EPSG:4326", geometry=geopandas.points_from_xy(df.x, df.y)
            )
        except KeyError as e:
            self.status_label.config(text=f"failed transform to geo data frame!")
            tk.messagebox.showerror(
                "Error!", f"Missing geo transform column in CSV file like x or y : {e}"
            )
            return
        except Exception as e:
            self.status_label.config(text=f"failed transform to geo data frame!")
            tk.messagebox.showerror("Error!", e)
            return
        self.status_label.config(text=f"Complete transform to geo data frame!")

        # write data into database
        self.status_label.config(text="Writting data into database...")
        try:
            geo_data_frame.to_postgis(
                name=output_table, con=new_engine, if_exists="replace", index=False
            )
            index_sql = f"""
            CREATE INDEX IF NOT EXISTS {output_table}_geom_idx
            ON public.{output_table}
            USING GIST (geometry);
            """
            with new_engine.connect() as connection:
                with connection.begin():
                    connection.execute(text(index_sql))

        except Exception as e:
            self.status_label.config(text=f"failed to write data into database!")
            tk.messagebox.showerror(
                "Error!", f"failed to write data into data base beacuse: {e}"
            )
            return
        self.status_label.config(text="Data successfuly import into database!")


if __name__ == "__main__":
    app = RootWindow()
    app.mainloop()
