# Import necessary libraries
import geopandas as gpd  # For reading geospatial data from PostGIS into a GeoDataFrame
from sqlalchemy import (
    create_engine,
    text,
)  # For creating a database engine and executing SQL text
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()  # use uvicorn MainApi:app --reload command to start server

# --- CORS (Cross-Origin Resource Sharing) Middleware Configuration ---
# This is necessary to allow your frontend (running on a different origin,
# e.g., file:// or http://127.0.0.1:xxxx for a live server)
# to make requests to this FastAPI backend (running on http://127.0.0.1:8000).

# Define a list of origins that are allowed to make cross-origin requests.
# For development, allowing "null" (for file:// access) and common local dev servers is useful.
# Using ["*"] allows all origins, which is convenient for development but generally
# insecure for production environments (you should list specific frontend domains).
origins = [
    "http://localhost",  # Common alias for local machine
    "http://localhost:8080",  # Example if your frontend runs on port 8080
    "http://127.0.0.1",  # Another common alias for local machine
    "http://127.0.0.1:5500",  # Common port for VS Code Live Server
    "null",  # Allows requests from local HTML files opened with file://
    # For broader development testing, you can use:
    # "*"
]

# Add the CORSMiddleware to the FastAPI application.
# This middleware will automatically add the necessary CORS headers to responses.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specify allowed origins (or ["*"] for all during dev)
    allow_credentials=True,  # Whether to support cookies for cross-origin requests (often False for simple APIs)
    allow_methods=[
        "*"
    ],  # Which HTTP methods are allowed (e.g., GET, POST). ["*"] allows all.
    allow_headers=[
        "*"
    ],  # Which HTTP headers are allowed in requests. ["*"] allows all.
)


DATABASE_CONNECTION_STRING = (
    "postgresql://postgres:960531wdxxm@localhost:5432/PostGIS Learning Database"
)


TABLE_NAME = "btn_2020_constrained_UNadj"

SQL_QUERY_STRING = f'SELECT * FROM public."{TABLE_NAME}";'


@app.get("/")
async def read_root():
    return {"message": "Hello FastAPI! Your GIS API is starting..."}


@app.get("/get_population_data")
async def get_populaion_data():
    engine = None
    gdf_from_db = None
    try:
        # Print a message indicating the start of the process
        print("Attempting to create database engine...")
        # Create a SQLAlchemy engine using the connection string
        engine = create_engine(DATABASE_CONNECTION_STRING)

        # (Optional but good practice) Test the database connection by executing a simple query.
        # This helps confirm that the connection parameters are correct before attempting larger operations.
        print("Testing database connection...")
        with engine.connect() as connection:
            connection.execute(
                text("SELECT 1")
            )  # A minimal query to check connectivity
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
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during database interaction: {e}",
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
        return gdf_from_db.__geo_interface__
    else:
        # Message if no data was read or if an error occurred before gdf_from_db was populated
        raise HTTPException(
            status_code=404,
            detail=f"\nFailed to read data from the table 'public.{TABLE_NAME}', or the table is empty.",
        )
