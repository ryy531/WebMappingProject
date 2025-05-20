# Import necessary libraries
import pandas as pd
import geopandas  # Used for handling geospatial data (GeoDataFrames) and interacting with PostGIS
from sqlalchemy import create_engine  # Used to create a database connection engine
from sqlalchemy import text  # Used to execute plain SQL queries securely via SQLAlchemy
import time  # Optional, for timing operations (though not used extensively in this version)
import tkinter as tk  # Tkinter for basic GUI functionality
from tkinter import ttk  # Themed widgets for a more modern look
from tkinter import filedialog  # Standard dialogs for opening/saving files
from tkinter import (
    messagebox,
)  # Standard dialogs for displaying messages (info, warning, error)
import os  # Used for basic operating system interactions (like getting basename of a file path)


# Define the main application window class, inheriting from tk.Tk
class RootWindow(tk.Tk):
    # Constructor method, called when a RootWindow object is created
    def __init__(self):
        # Call the constructor of the parent class (tk.Tk)
        super().__init__()
        # Set the window title
        self.title("Import CSV to PostGIS Database")

        # Initialize instance variables to store selected file path and GUI entry widgets
        self.csv_file_path = None
        # Note: Corrected spelling from 'databaes' to 'database'
        self.database_username_entry = None
        self.database_password_entry = None
        self.database_host_entry = None
        self.database_port_entry = None
        self.database_database_name_entry = None
        self.output_table_entry = None
        self.status_label = None  # Widget to display operation status

        # Create a main frame to hold all other widgets, with padding
        main_frame = ttk.Frame(self, padding=10)

        # --- CSV File Selection Section ---
        # Label and Button for choosing CSV file
        input_csv_label = ttk.Label(main_frame, text="Select CSV File:")
        input_csv_label.grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )  # Anchor to the west

        # Label to display the selected CSV file path
        self.input_csv_path_label = ttk.Label(main_frame, text="No file selected")
        self.input_csv_path_label.grid(
            row=0, column=1, padx=5, pady=5, sticky="ew"
        )  # Expand east/west

        # Button to open the file dialog
        ttk.Button(main_frame, text="Browse...", command=self.select_input_csv).grid(
            row=0, column=2, padx=5, pady=5
        )

        # --- Database Connection Details Section ---
        # Labels and Entry widgets for database connection parameters
        # Username
        input_username_label = ttk.Label(main_frame, text="Database Username:")
        input_username_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.database_username_entry = ttk.Entry(main_frame)
        self.database_username_entry.grid(
            row=1, column=1, padx=5, pady=5, sticky="ew"
        )  # Expand east/west
        # Add a default value for username (optional, adjust as needed)
        # self.database_username_entry.insert(0, "postgres")

        # Password
        input_password_label = ttk.Label(main_frame, text="Database Password:")
        input_password_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.database_password_entry = ttk.Entry(
            main_frame, show="*"
        )  # Show asterisks for password
        self.database_password_entry.grid(
            row=2, column=1, padx=5, pady=5, sticky="ew"
        )  # Expand east/west

        # Host
        input_host_label = ttk.Label(main_frame, text="Database Host:")
        input_host_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.database_host_entry = ttk.Entry(main_frame)
        self.database_host_entry.grid(
            row=3, column=1, padx=5, pady=5, sticky="ew"
        )  # Expand east/west
        # Add a default value for host (optional, adjust as needed)
        self.database_host_entry.insert(0, "localhost")

        # Port
        input_port_label = ttk.Label(main_frame, text="Database Port:")
        input_port_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.database_port_entry = ttk.Entry(main_frame)
        self.database_port_entry.grid(
            row=4, column=1, padx=5, pady=5, sticky="ew"
        )  # Expand east/west
        # Insert default port number
        self.database_port_entry.insert(0, "5432")

        # Database Name
        input_database_name_label = ttk.Label(main_frame, text="Database Name:")
        input_database_name_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.database_database_name_entry = ttk.Entry(main_frame)
        self.database_database_name_entry.grid(
            row=5, column=1, padx=5, pady=5, sticky="ew"
        )  # Expand east/west
        # Add a default value for database name (optional, adjust as needed)
        # self.database_database_name_entry.insert(0, "your_database_name")

        # Output Table Name
        output_table_label = ttk.Label(main_frame, text="Output Table Name:")
        output_table_label.grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.output_table_entry = ttk.Entry(main_frame)
        self.output_table_entry.grid(
            row=6, column=1, padx=5, pady=5, sticky="ew"
        )  # Expand east/west
        # Default value for table name is set AFTER file selection in select_input_csv

        # --- Import Button ---
        ttk.Button(main_frame, text="Start Import", command=self.start_import).grid(
            row=7,
            column=0,
            columnspan=3,
            padx=5,
            pady=10,
            sticky="ew",  # Span across 3 columns and expand
        )

        # --- Status Label ---
        # Label to display the current status of the import process
        self.status_label = ttk.Label(main_frame, text="Status: Waiting for input...")
        self.status_label.grid(
            row=8, column=0, columnspan=3, padx=5, pady=5, sticky="ew"
        )  # Span across 3 columns and expand

        # Arrange the main frame to fill the window
        main_frame.pack(fill="both", expand=True)

    # Method to handle CSV file selection
    def select_input_csv(self):
        # Open a file dialog to select a CSV file
        csv_file_path = filedialog.askopenfilename(
            title="Select CSV file to upload",
            # Updated filetypes to a list of tuples as required
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            parent=self,  # Set the parent window for the dialog
        )

        # If user selected a file (path is not empty)
        if csv_file_path:
            self.csv_file_path = csv_file_path
            # Clear current output table name entry and insert the base filename
            self.output_table_entry.delete(0, tk.END)
            self.output_table_entry.insert(
                0, os.path.basename(csv_file_path).split(".")[0]
            )  # Use filename without extension as default table name
            # Update the label to show the selected file path
            self.input_csv_path_label.config(text=csv_file_path)
        else:
            # If user cancelled selection, clear stored path and update label
            self.csv_file_path = None
            self.input_csv_path_label.config(text="No file selected")
            # Optionally clear the output table name entry if file is unselected
            # self.output_table_entry.delete(0, tk.END)

    # Method to start the import process (triggered by "Start Import" button)
    def start_import(self):
        # Retrieve values from GUI entry widgets
        csv_path = self.csv_file_path
        username = self.database_username_entry.get()
        password = self.database_password_entry.get()
        host = self.database_host_entry.get()
        port = self.database_port_entry.get()
        database_name = self.database_database_name_entry.get()
        output_table = self.output_table_entry.get()

        # List of required input values and corresponding error messages
        required_inputs = [
            (csv_path, "Please select a CSV file first!"),
            (username, "Please enter the database username."),
            (host, "Please enter the database host address."),
            (port, "Please enter the database port number."),
            (database_name, "Please enter the database name."),
            (output_table, "Please enter the desired output table name."),
        ]

        # Validate required inputs
        for input_value, error_message in required_inputs:
            if not input_value:  # Checks if the value is empty string, None, etc.
                messagebox.showerror("Input Error", error_message)
                return  # Stop the process if any required input is missing

        # Build the database connection string (using f-string for clarity)
        # Handle case where password might be empty
        if password:
            database_connection_str = (
                f"postgresql://{username}:{password}@{host}:{port}/{database_name}"
            )
        else:
            database_connection_str = (
                f"postgresql://{username}@{host}:{port}/{database_name}"
            )

        # Console feedback (optional, for debugging)
        print("\n--- Starting Import Process ---")
        print("All input validated.")
        print(
            f"Attempting to connect to: postgresql://{username}@{host}:{port}/{database_name} (password hidden)"
        )
        print(f"Output table name: {output_table}")

        # --- Database Connection, Data Loading, and Writing ---
        try:
            # 1. Connect to the database
            self.status_label.config(text="Status: Connecting to database...")
            self.update_idletasks()  # Update GUI immediately
            engine = create_engine(database_connection_str)

            # Test the connection
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print("Database engine created and connection tested successfully.")
            self.status_label.config(text="Status: Database connected!")
            self.update_idletasks()

            # 2. Read CSV file
            self.status_label.config(text=f"Status: Reading CSV file: {csv_path}...")
            self.update_idletasks()
            df = pd.read_csv(csv_path)
            print(f"CSV file loaded. Read {len(df)} rows.")
            self.status_label.config(
                text=f"Status: CSV file loaded. Read {len(df)} rows."
            )
            self.update_idletasks()

            # 3. Convert to GeoDataFrame
            self.status_label.config(text=f"Status: Converting to GeoDataFrame...")
            self.update_idletasks()
            # Create GeoDataFrame using df, geometry from x/y, and CRS
            # Assumes 'x' and 'y' columns exist and contain valid numerical coordinates
            geo_data_frame = geopandas.GeoDataFrame(
                df,
                geometry=geopandas.points_from_xy(
                    df.x, df.y
                ),  # Create Point geometry from x, y columns
                crs="EPSG:4326",  # Set Coordinate Reference System to WGS84
            )
            print("Conversion to GeoDataFrame complete.")
            self.status_label.config(text=f"Status: Converted to GeoDataFrame.")
            self.update_idletasks()

            # 4. Write data to PostGIS database table
            self.status_label.config(
                text=f"Status: Writing data to table '{output_table}'..."
            )
            self.update_idletasks()
            print(f"Writing data to table '{output_table}' in PostGIS...")

            # Use to_postgis to write the GeoDataFrame to the database
            # name: The name of the output table
            # con: The SQLAlchemy engine for connection
            # if_exists: How to handle existing table ('replace', 'append', 'fail')
            # index: Whether to write DataFrame index as a database column
            geo_data_frame.to_postgis(
                name=output_table,
                con=engine,
                if_exists="replace",  # Replace table if it already exists
                index=False,
            )
            print(f"Data successfully written to table '{output_table}'.")
            self.status_label.config(
                text=f"Status: Data written to table '{output_table}'."
            )
            self.update_idletasks()

            # 5. Create Spatial Index (Optional but Recommended for performance)
            self.status_label.config(text="Status: Creating spatial index...")
            self.update_idletasks()
            print("Creating spatial index for geometry column...")

            # SQL command to create a GiST index on the geometry column
            # IF NOT EXISTS prevents error if index already exists
            index_sql = f"""
            CREATE INDEX IF NOT EXISTS "{output_table}_geom_idx"
            ON public."{output_table}" -- Assuming default 'public' schema
            USING GIST (geometry); 
            """
            # Execute the SQL command within a transaction for safety
            with engine.connect() as connection:
                with connection.begin():
                    connection.execute(text(index_sql))

            print("Spatial index created successfully.")
            self.status_label.config(text="Status: Spatial index created.")
            self.update_idletasks()

            # --- All steps completed successfully ---
            self.status_label.config(text="Status: Data import complete!")
            messagebox.showinfo(
                "Import Successful",
                "Data has been successfully imported to the database!",
            )
            print("\n--- Import Process Completed Successfully ---")

        # --- Error Handling for the entire import process ---
        except (
            FileNotFoundError
        ):  # Specific error for CSV not found (less likely after filedialog)
            self.status_label.config(text=f"Error: CSV File Not Found!")
            messagebox.showerror(
                "File Error", f"The CSV file was not found at '{csv_path}'."
            )
            print(f"Error: CSV File Not Found at '{csv_path}'.")
            return
        except pd.errors.EmptyDataError:  # Specific error for empty CSV
            self.status_label.config(text=f"Error: CSV File is Empty!")
            messagebox.showerror("File Error", f"The CSV file '{csv_path}' is empty.")
            print(f"Error: CSV File '{csv_path}' is empty.")
            return
        except pd.errors.ParserError as e:  # Specific error for malformed CSV
            self.status_label.config(text=f"Error: CSV Parsing Failed!")
            messagebox.showerror(
                "File Error", f"Failed to parse CSV file '{csv_path}': {e}"
            )
            print(f"Error: Failed to parse CSV file '{csv_path}': {e}")
            return
        except KeyError as e:  # Specific error if x or y columns are missing
            self.status_label.config(text=f"Error: Missing Required Columns!")
            messagebox.showerror(
                "Data Error",
                f"Missing required column(s) in CSV file (e.g., 'x' or 'y'): {e}",
            )
            print(
                f"Error: Missing required column(s) in CSV file (e.g., 'x' or 'y'): {e}"
            )
            return
        except Exception as e:  # Catch any other unexpected errors
            self.status_label.config(text=f"Status: Import Failed!")
            messagebox.showerror(
                "Import Failed", f"An error occurred during the import process: {e}"
            )
            print(f"\n--- Import Process Failed ---")
            print(f"Error details: {e}")
            return


# --- Main application entry point ---
# This block ensures the GUI runs only when the script is executed directly
if __name__ == "__main__":
    app = RootWindow()  # Create an instance of the RootWindow class
    app.mainloop()  # Start the Tkinter event loop (keeps the window open)
