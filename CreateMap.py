import folium
import pandas as pd
import tkinter as tk
import tkinter.filedialog
from folium.plugins import HeatMap


root = tk.Tk()
root.withdraw()
csvFileName = tkinter.filedialog.askopenfilename(title = "Please choose the total population file you want :", filetypes= [("csv files", "*.csv"),("All files", "*.*")])
root.destroy()
if not csvFileName :
    print("User didn't select file")
    exit()
else : 
    print(f"User selected file : {csvFileName} ")



#csvFileName = 'btn_2020_constrained_UNadj.csv'
df = None

try :
    df = pd.read_csv(csvFileName)
    print("File Load Successful.")

except FileNotFoundError :
    print(f"File '{csvFileName}' Not found")
    exit()

except pd.errors.EmptyDataError :
    print(f"Error, file '{csvFileName}' read was Empty!")
    exit()

except pd.errors.ParserError:
    print(f"Error: Could not parse file '{csvFileName}'. Check format.")
    exit()

except Exception as e :
    print(f"An unexpected error occurred while reading the CSV: {e}")
    exit()


#Check if file is empty
if  df is None or df.empty :
    print("Error, Data frame could not loaded or was Empty!")
    exit()

requiredColumns =  ['x', 'y', 'TotalPopulation']
allColumnPresent = all (col in df.columns for col in requiredColumns)
if allColumnPresent :
    print ("All required fields exist!")
else:
    print ("Error: Missing required columns!")
    missingCols = [col for col in requiredColumns if col not in df.columns]
    print(f"Missing columns: {missingCols}")
    exit()

#Create Base Map
mapCenter = [df['y'].mean(), df['x'].mean()]
baseMap = folium.Map(location = mapCenter, zoom_start = 10)
print("Base map created successfully.")

#Create HeatMap
print("Preparing heatmap data...")
heatData = df[['y', 'x', 'TotalPopulation']].values.tolist()
print("Adding heatmap layer...")
newHeatMap = folium.plugins.HeatMap(data=heatData, radius=15, blur=10, name='Population HeatMap')
newHeatMap.add_to(baseMap)

# Add markers on map

markerGroup = folium.FeatureGroup(name='Population Markers')

for index, row in df.iterrows() :
    lon = row['x']
    lat = row['y']

    #Create html contents
    htmlContent = f"<b> Position : </b> ({lat:.4f}, {lon:.4f})<br> "
    htmlContent += f"<b>TotalPopulation:</b> {row['TotalPopulation']}<br>"
    htmlContent += "<hr><b>Age Data with Gender:</b><br>"
    #dynamicly shows the column name
    for colName in df.columns : 
        if colName.startswith(('f_' , 'm_')) : 
            value = row[colName]
            if pd.notna(value):
                htmlContent += f"<b>{colName}:</b> {value}<br>" 
            else:
                htmlContent += f"<b>{colName}:</b> N/A<br>" 
    
    #Create the iframe
    iframe = folium.IFrame(html= htmlContent, width=200, height=250)

    #Create popup object
    popup = folium.Popup(iframe, max_width = 200)

    marker = folium.Marker(location=[lat, lon], popup = popup, tooltip=f"Total population : {row['TotalPopulation']}")
    marker.add_to(markerGroup) 

#Add Marker to map group    
markerGroup.add_to(baseMap)
print("Markers added to the map.") 

#Create layer control
print("Adding layer control...")
folium.LayerControl().add_to(baseMap)

#Save base map 


root = tk.Tk()
root.withdraw()
htmlFileSavePath = tkinter.filedialog.asksaveasfilename(title= "Choose Your save directory: ", initialfile='webMapData.html',defaultextension=".html", filetypes=[("HTML files","*.html"), ("All files","*.*")])
root.destroy()
if not htmlFileSavePath :
    print ("User cancel save option")
else:
    try:
        baseMap.save(htmlFileSavePath)
        print(f"Map successfully saved to: {htmlFileSavePath}")
    except Exception as e:
        print(f"Error saving map to {htmlFileSavePath}: {e}")


