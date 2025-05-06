# Import necessary libraries
import geopandas as gpd  # For reading geospatial data from PostGIS into a GeoDataFrame
from sqlalchemy import (
    create_engine,
    text,
)  # For creating a database engine and executing SQL text

# --- 1. Database Connection Configuration ---
# Define the connection string for your PostgreSQL/PostGIS database.
# Replace with your actual username, password, host, port, and database name.
# Note: If your database name contains spaces, it might need to be URL-encoded (e.g., 'My%20Database').
# It's generally better to use database names without spaces or special characters.
DATABASE_CONNECTION_STRING = "postgresql://postgres:960531wdxxm@localhost:5432/PostGIS Learning Database"  # Example

# --- 2. Table and SQL Query Configuration ---
# Define the name of the table you want to read from.
# Ensure this matches the exact table name in your database, including case if it was created with quotes.
# PostgreSQL typically folds unquoted identifiers to lowercase.
TABLE_NAME = "btn_2020_constrained_UNadj"  # Assuming the table is lowercase as per typical PostGIS behavior

# Define the SQL query to retrieve data.
# It's good practice to schema-qualify the table name (e.g., 'public.your_table').
# If the table name in the database has mixed case or special characters, quote it in the SQL:
# SQL_QUERY_STRING = f'SELECT * FROM public."{TABLE_NAME}";'
# If the table name is all lowercase and simple, quoting might not be strictly necessary:
SQL_QUERY_STRING = f"SELECT * FROM public.{TABLE_NAME};"
# You can customize this query to select specific columns or filter data, e.g.:
# SQL_QUERY_STRING = f'SELECT id, "TotalPopulation", geom FROM public."{TABLE_NAME}" WHERE "TotalPopulation" > 100;'


# --- 3. Initialize Variables ---
engine = None  # Will store the SQLAlchemy database engine
gdf_from_db = None  # Will store the GeoDataFrame read from the database

# --- 4. Connect to Database and Read Data ---
try:
    # Print a message indicating the start of the process
    print("Attempting to create database engine...")
    # Create a SQLAlchemy engine using the connection string
    engine = create_engine(DATABASE_CONNECTION_STRING)

    # (Optional but good practice) Test the database connection by executing a simple query.
    # This helps confirm that the connection parameters are correct before attempting larger operations.
    print("Testing database connection...")
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))  # A minimal query to check connectivity
    print("Database connection successful!")

    # Print a message indicating that data reading is about to start
    print(f"Attempting to read data from table 'public.{TABLE_NAME}'...")

    # Use GeoPandas to read data from the PostGIS database
    # sql: The SQL query (as a string or SQLAlchemy text() object).
    # con: The SQLAlchemy engine or connection object.
    # geom_col: The name of the geometry column in your PostGIS table (e.g., 'geom' or 'geometry').
    # crs: The Coordinate Reference System to assign to the GeoDataFrame's geometry.
    #      'EPSG:4326' corresponds to WGS84 (latitude/longitude).
    gdf_from_db = gpd.read_postgis(
        sql=text(SQL_QUERY_STRING),  # Wrap SQL string in text() for SQLAlchemy
        con=engine,
        geom_col="geom",  # Ensure this matches your geometry column name
        crs="EPSG:4326",  # Assuming WGS84
    )

    print(f"Successfully read data from table 'public.{TABLE_NAME}'.")

except Exception as e:
    # Catch any errors that occur during engine creation, connection, or data reading
    print(f"An error occurred during database interaction: {e}")
    if engine is None:
        print("The error likely occurred during database engine creation.")
    elif gdf_from_db is None:
        print(
            f"The error likely occurred while trying to read from table 'public.{TABLE_NAME}'."
        )
        print(
            "Possible reasons: Table does not exist, SQL query is incorrect, or connection issues after engine creation."
        )

# --- 5. Display Results (if data was successfully read) ---
# Check if the GeoDataFrame was successfully populated and is not empty
if gdf_from_db is not None and not gdf_from_db.empty:
    print("\n--- Data Read from Database (First 5 Rows): ---")
    # Display the first 5 rows of the GeoDataFrame
    print(gdf_from_db.head())

    print("\n--- GeoDataFrame Info: ---")
    # Display a concise summary of the GeoDataFrame, including data types and non-null values
    # .info() prints directly to the console, so no need for an f-string or print() around it.
    gdf_from_db.info()

    print(
        f"\nSuccessfully read {len(gdf_from_db)} rows from the database table 'public.{TABLE_NAME}'."
    )
else:
    # Message if no data was read or if an error occurred before gdf_from_db was populated
    print(
        f"\nFailed to read data from the table 'public.{TABLE_NAME}', or the table is empty."
    )
