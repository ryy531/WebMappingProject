# Import necessary libraries
import geopandas as gpd  # For reading geospatial data from PostGIS into a GeoDataFrame
from sqlalchemy import (
    create_engine,
    text,
)  # For creating a database engine and executing SQL text
from fastapi import (
    FastAPI,
    HTTPException,
)  # FastAPI for API creation, HTTPException for error responses
from fastapi.middleware.cors import CORSMiddleware  # For Cross-Origin Resource Sharing
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI()  # Server start command :  uvicorn MainApi:app --reload


class HospitalCreate(BaseModel):
    name: str | None = None
    doctor_count: int
    latitude: float
    longitude: float


class AnalysisData(BaseModel):
    latitude: float
    longitude: float
    radius_meters: int


# --- CORS (Cross-Origin Resource Sharing) Middleware Configuration ---
# Allows frontend (e.g., running on http://127.0.0.1:5500)
# to make requests to this FastAPI backend (running on http://127.0.0.1:8000).
origins = [
    "http://localhost",
    "http://localhost:8080",  # Example if your frontend runs on port 8080
    "http://127.0.0.1",
    "http://127.0.0.1:5500",  # Common port for VS Code Live Server or similar
    "null",  # Allows requests from local HTML files opened with file://
    # "*"                    # For broader development testing (allows all origins)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # For development, allow all. For production, list specific frontend domains.
    allow_credentials=False,  # Whether to support cookies for cross-origin requests.
    allow_methods=[
        "*"
    ],  # Which HTTP methods are allowed (e.g., GET, POST). ["*"] allows all.
    allow_headers=[
        "*"
    ],  # Which HTTP headers are allowed in requests. ["*"] allows all.
)

# --- Database Connection and Table Configuration ---
DATABASE_CONNECTION_STRING = (
    "postgresql://postgres:960531wdxxm@localhost:5432/PostGIS Learning Database"
)

# Configuration for the population points data
POPULATION_TABLE_NAME = "egy_2020_constrained_UNadj"  # Original population data table
POPULATION_GEOM_COL = "geometry"  # Geometry column for population points
SQL_QUERY_POPULATION_POINTS = f'SELECT * FROM public."{POPULATION_TABLE_NAME}" LIMIT 50;'  # Query for population points with a limit for now

# Configuration for the analysis polygons data
ANALYSIS_POLYGONS_TABLE_NAME = (
    "egypt_shape_admin_level2"  # Table name for analysis polygons
)
POLYGON_GEOMETRY_COLUMN_NAME = "geom"  # Geometry column for analysis polygons
SQL_QUERY_ANALYSIS_POLYGONS = f'SELECT * FROM public."{ANALYSIS_POLYGONS_TABLE_NAME}";'  # Query to get all analysis polygons

SQL_QUERY_HOSPITAL_DATA = 'SELECT * FROM public."hospitals";'
# --- API Endpoints ---


@app.get("/")
async def read_root():
    """
    Root endpoint to check if the API is running.
    """
    print("Root endpoint '/' was accessed.")
    return {"message": "Hello FastAPI! Your GIS API is running."}


@app.get("/get_population_data")
async def get_population_data():
    """
    API endpoint to fetch population point data from PostGIS.
    Currently returns a limited number of points due to SQL_QUERY_POPULATION_POINTS.
    """
    engine = None
    gdf_population = None  # GeoDataFrame for population data

    try:
        print("--- Population Data Endpoint: Start ---")
        print("Attempting to create database engine for population data...")
        engine = create_engine(DATABASE_CONNECTION_STRING)

        print("Testing database connection for population data...")
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))  # Minimal query to check connectivity
        print("Database connection successful for population data!")

        print(
            f"Attempting to read population data from table 'public.{POPULATION_TABLE_NAME}' using query: {SQL_QUERY_POPULATION_POINTS}"
        )
        gdf_population = gpd.read_postgis(
            sql=text(SQL_QUERY_POPULATION_POINTS),
            con=engine,
            geom_col=POPULATION_GEOM_COL,  # Use defined geometry column name
            crs="EPSG:4326",  # Assuming WGS84
        )
        print(
            f"Successfully read {len(gdf_population)} population points from table 'public.{POPULATION_TABLE_NAME}'."
        )

    except Exception as e:
        error_message = f"An error occurred during database interaction for population data: {str(e)}"
        print(f"ERROR: {error_message}")
        raise HTTPException(
            status_code=500,
            detail=error_message,
        )

    if gdf_population is not None and not gdf_population.empty:
        print("Population data GeoDataFrame (first 5 rows):")
        print(gdf_population.head())
        # print("\nPopulation data GeoDataFrame Info:") # .info() prints directly, so a preceding print is good
        # gdf_population.info() # This prints directly to console, can be verbose for API logs
        print("--- Population Data Endpoint: Success ---")
        return (
            gdf_population.__geo_interface__
        )  # Convert GeoDataFrame to GeoJSON-like dictionary
    elif gdf_population is not None and gdf_population.empty:
        message = f"No population data found in table 'public.{POPULATION_TABLE_NAME}' or query returned no results."
        print(f"INFO: {message}")
        # Return an empty GeoJSON FeatureCollection if no data found
        return {"type": "FeatureCollection", "features": []}
    else:
        # This case should ideally be caught by the exception or the empty check
        message = f"Failed to read population data from 'public.{POPULATION_TABLE_NAME}', or an unexpected issue occurred."
        print(f"ERROR: {message}")
        raise HTTPException(
            status_code=404,  # Or 500 if it's an unexpected server state
            detail=message,
        )


@app.get(
    "/get_polygon_data"
)  # Changed from get_populaion_data to get_polygon_data as per your code
async def get_polygon_data():  # Renamed function to match endpoint and data type
    """
    API endpoint to fetch analysis polygon data from PostGIS.
    """
    engine = None
    gdf_polygons = None  # GeoDataFrame for polygon data

    try:
        print("--- Polygon Data Endpoint: Start ---")
        print("Attempting to create database engine for polygon data...")
        engine = create_engine(DATABASE_CONNECTION_STRING)

        print("Testing database connection for polygon data...")
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))  # Minimal query to check connectivity
        print("Database connection successful for polygon data!")

        print(
            f"Attempting to read polygon data from table 'public.{ANALYSIS_POLYGONS_TABLE_NAME}' using query: {SQL_QUERY_ANALYSIS_POLYGONS}"
        )
        gdf_polygons = gpd.read_postgis(
            sql=text(SQL_QUERY_ANALYSIS_POLYGONS),
            con=engine,
            geom_col=POLYGON_GEOMETRY_COLUMN_NAME,  # Use defined geometry column name for polygons
            crs="EPSG:4326",  # Assuming WGS84
        )
        print(
            f"Successfully read {len(gdf_polygons)} polygons from table 'public.{ANALYSIS_POLYGONS_TABLE_NAME}'."
        )

    except Exception as e:
        error_message = (
            f"An error occurred during database interaction for polygon data: {str(e)}"
        )
        print(f"ERROR: {error_message}")
        raise HTTPException(
            status_code=500,
            detail=error_message,
        )

    if gdf_polygons is not None and not gdf_polygons.empty:
        print("Polygon data GeoDataFrame (first 5 rows):")  # Good for a quick check
        print(gdf_polygons.head())
        # print("\nPolygon data GeoDataFrame Info:") # .info() can be verbose for API logs
        # gdf_polygons.info()
        print("--- Polygon Data Endpoint: Success ---")
        return (
            gdf_polygons.__geo_interface__
        )  # Convert GeoDataFrame to GeoJSON-like dictionary
    elif gdf_polygons is not None and gdf_polygons.empty:
        message = (
            f"No polygon data found in table 'public.{ANALYSIS_POLYGONS_TABLE_NAME}'."
        )
        print(f"INFO: {message}")
        # Return an empty GeoJSON FeatureCollection if no data found
        return {"type": "FeatureCollection", "features": []}
    else:
        # This case implies an issue before data could be assessed as empty, likely caught by the main try-except.
        message = f"Failed to read polygon data from 'public.{ANALYSIS_POLYGONS_TABLE_NAME}', or an unexpected issue occurred."
        print(f"ERROR: {message}")
        raise HTTPException(
            status_code=404,  # Or 500
            detail=message,
        )


@app.post("/api/add_hospital")
async def add_new_hospital(hospital_input: HospitalCreate):
    print(f"name: {hospital_input.name}")
    print(f"Doctor Count: {hospital_input.doctor_count}")
    print(f"Latitude: {hospital_input.latitude}")
    print(f"Longitude: {hospital_input.longitude}")
    engine = None
    new_hospital_id = None
    engine = create_engine(DATABASE_CONNECTION_STRING)

    sql_insert_statement = text(
        """
    INSERT INTO public.hospitals (name, doctor_count, geom)
    VALUES (:name, :doctor_count, ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326))
    RETURNING id;
"""
    )
    insert_params = {
        "name": hospital_input.name,
        "doctor_count": hospital_input.doctor_count,
        "longitude": hospital_input.longitude,
        "latitude": hospital_input.latitude,
    }
    try:
        print("Attempting to create database engine for hospital insertion...")
        engine = create_engine(DATABASE_CONNECTION_STRING)
        with engine.connect() as connection:
            with connection.begin() as transaction:
                result = connection.execute(sql_insert_statement, insert_params)
                new_hospital_id = result.scalar_one_or_none()
                print(f"Successfully inserted new hospital with ID: {new_hospital_id}")

        print("--- Add Hospital Endpoint: Database insertion successful ---")
        return {
            "message": "Hospital added to database successfully!",
            "hospital_id": new_hospital_id,
            "data_submitted": hospital_input,
        }
    except Exception as e:
        error_message = f"Database error occurred while adding hospital: {str(e)}"
        print(f"ERROR: {error_message}")
        raise HTTPException(
            status_code=500,
            detail=error_message,
        )
    finally:
        if engine:
            engine.dispose()
            print("Database engine disposed.")


@app.get(
    "/get_hospitals"
)  # Changed from get_populaion_data to get_polygon_data as per your code
async def get_hospitals():
    engine = None
    gdf_hospitals = None
    try:
        print("--- Get Hospitals Endpoint: Start ---")
        print("Attempting to create database engine for hospital data...")
        engine = create_engine(DATABASE_CONNECTION_STRING)
        print("Testing database connection for hospital data...")
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("Database connection successful for hospitals!")
        print(f"Attempting to read hospital data from table 'public.hospitals'...")
        gdf_hospitals = gpd.read_postgis(
            sql=text(SQL_QUERY_HOSPITAL_DATA),
            con=engine,
            geom_col="geom",
            crs="EPSG:4326",
        )
        print(
            f"Successfully read {len(gdf_hospitals)} records from 'public.hospitals'."
        )
    except Exception as e:
        error_message = (
            f"An error occurred during database interaction for hospital data: {str(e)}"
        )
        print(f"ERROR: {error_message}")
        raise HTTPException(
            status_code=500,
            detail=error_message,
        )
    if gdf_hospitals is not None and not gdf_hospitals.empty:
        print(f"Returning {len(gdf_hospitals)} hospital records as GeoJSON.")
        print("--- Get Hospitals Endpoint: Success ---")
        return gdf_hospitals.__geo_interface__
    elif gdf_hospitals is not None and gdf_hospitals.empty:
        message = "No hospital data found in table 'public.hospitals'."
        print(f"INFO: {message}")
        print("--- Get Hospitals Endpoint: Success (No Data) ---")
        return {"type": "FeatureCollection", "features": []}
    else:
        message = f"Failed to read hospital data from 'public.hospitals', or an unexpected issue occurred."
        print(f"ERROR: {message}")
        raise HTTPException(
            status_code=500,
            detail=message,
        )


@app.post("/api/analysis_data")
async def analysis_data(data_input: AnalysisData):
    print("Start to analysis buffer circle data")
    engine = None
    gdf_populations = None
    SQL_QUERY_ANALYSIS_DATA = f'SELECT SUM("TotalPopulation") FROM "{POPULATION_TABLE_NAME}" WHERE ST_DWithin(geometry::geography,ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,:radius);'
    params = {
        "lon": data_input.longitude,
        "lat": data_input.latitude,
        "radius": data_input.radius_meters,
    }
    try:
        engine = create_engine(DATABASE_CONNECTION_STRING)
        with engine.connect() as connection:
            result = connection.execute(text(SQL_QUERY_ANALYSIS_DATA), params)
            population_sum = result.scalar_one()
            if population_sum is None:
                population_sum = 0
            print(f"Analysis complete. Total Population in buffer: {population_sum}")

            return {"population_count": int(population_sum)}

    except Exception as e:
        error_message = (
            f"An error occurred during database interaction for data analysis: {str(e)}"
        )
        print(f"ERROR: {error_message}")
        raise HTTPException(
            status_code=500,
            detail=error_message,
        )
