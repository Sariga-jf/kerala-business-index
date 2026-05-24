import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import folium
kerala_map = gpd.read_file("Kerala_District_Boundary.geojson")
census = pd.read_csv("india-districts-census-2011.csv")

kerala_census = census[census['State name'] == 'KERALA']                        #Kerala data

kerala_map = kerala_map.rename(columns={'DISTRICT': 'district'})                #Rename column of both table to district for easier access
kerala_census = kerala_census.rename(columns={'District name': 'district'})


kerala_map['district'] = kerala_map['district'].str.lower().str.strip()         #convert all district to lowercase

kerala_census['district'] = (
    kerala_census['district']
    .str.lower()
    .str.strip()
)

# To Check district names
#print(kerala_map['district'].unique())
#print(kerala_census['district'].unique())

merged = kerala_map.merge(                                                      # To Merge two tables by common attr district
    kerala_census,
    on='district'
)

merged['population_density'] = (
    merged['Population'] / merged['Area']
)

scaler = MinMaxScaler()

# Check merged data
#print(merged.head())

columns_to_normalize = [
    'Population',
    'Literate',
    'Workers',
    'Total_Power_Parity',
    'population_density'
]

merged[columns_to_normalize] = scaler.fit_transform(
    merged[columns_to_normalize]
)

merged.plot(
    column='Population',
    cmap='OrRd',
    legend=True,
    figsize=(10,8),
    edgecolor='black'
)

plt.title("Kerala District Population Map")
plt.axis('off')

plt.show()



merged['shop_score'] = (
    merged['Population'] * 0.35 +
    merged['Literate'] * 0.2 +
    merged['Workers'] * 0.2 +
    merged['Total_Power_Parity'] * 0.25
)

merged.plot(
    column='shop_score',
    cmap='YlGnBu',
    legend=True,
    figsize=(12,10),
    edgecolor='black',
    linewidth=1
)

plt.title(
    "Business Suitability Index of Kerala Districts",
    fontsize=16
)

plt.axis('off')

plt.show()

top = merged.sort_values(
    by='shop_score',
    ascending=False
)

plt.figure(figsize=(12,6))

plt.bar(
    top['district'],
    top['shop_score']
)

plt.xticks(rotation=45)

plt.xlabel("District")
plt.ylabel("Business Suitability Index")

plt.title("Kerala District Business Ranking")

plt.show()

print(top[['district', 'shop_score']])

def classify(score):

    if score >= 0.75:
        return "Excellent Business Potential"

    elif score >= 0.50:
        return "Good Business Potential"

    elif score >= 0.25:
        return "Moderate Business Potential"

    else:
        return "Low Business Potential"
    
merged['description'] = merged['shop_score'].apply(classify)

m = folium.Map(
    location=[10.8505, 76.2711],
    zoom_start=7
)

folium.Choropleth(
    geo_data=merged,
    data=merged,
    columns=['district', 'shop_score'],
    key_on='feature.properties.district',
    fill_color='YlGnBu',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Business Suitability Index'
).add_to(m)

folium.GeoJson(
    merged,

    style_function=lambda feature: {
        'color': 'black',
        'weight': 0.5,   # thinner border
        'fillOpacity': 0
    },

    tooltip=folium.GeoJsonTooltip(
        fields=[
            'district',
            'shop_score',
            'description'
        ],

        aliases=[
            'District:',
            'Business Score:',
            'Category:'
        ],

        localize=True,

        style="""
            background-color: white;
            color: black;
            font-family: arial;
            font-size: 14px;
            padding: 10px;
        """
    )
).add_to(m)


# import requests
# from folium.plugins import HeatMap

# print("Connecting to OpenStreetMap live database...")

# url = "http://overpass-api.de/api/interpreter"

# # Dynamic text search that looks for the administrative boundary of TVM
# query = """
# [out:json][timeout:30];
# area["name"="Thiruvananthapuram"]["boundary"="administrative"]->.searchArea;
# (
#   node["shop"="supermarket"](area.searchArea);
#   way["shop"="supermarket"](area.searchArea);
# );
# out center;
# """

# headers = {
#     'User-Agent': 'KeralaBusinessLocatorProject/1.0 (fredy)'
# }

# try:
#     response = requests.get(url, params={'data': query}, headers=headers)
#     heat_data = []
#     marker_layer = folium.FeatureGroup(name="Exact Store Locations")
    
#     if response.status_code == 200:
#         osm_data = response.json()
#         elements = osm_data.get('elements', [])
        
#         for element in elements:
#             lat = element.get('lat') or element.get('center', {}).get('lat')
#             lon = element.get('lon') or element.get('center', {}).get('lon')
#             name = element.get('tags', {}).get('name', 'Local Supermarket')
            
#             if lat and lon:
#                 heat_data.append([lat, lon])
#                 folium.CircleMarker(
#                     location=[lat, lon],
#                     radius=5,
#                     color="red",
#                     fill=True,
#                     fill_color="red",
#                     fill_opacity=0.8,
#                     tooltip=f"<b>Competitor:</b> {name}"
#                 ).add_to(marker_layer)

#     # FALLBACK CHECK: If the server gave 0 results due to timeouts, load preset local shops
#     if len(heat_data) == 0:
#         print("Server busy or boundary restricted. Injecting pre-mapped local competitor coordinates...")
#         # Hand-mapped prominent hubs inside TVM city limits (Pattom, Kazhakkoottam, East Fort, etc.)
#         fallback_shops = [
#             [8.5241, 76.9366, "Lulu Hypermarket (Anayara)"],
#             [8.5450, 76.9050, "Margin Free Supermarket (Kazhakkoottam)"],
#             [8.4833, 76.9500, "Big Bazaar (East Fort)"],
#             [8.5312, 76.9390, "Reliance Smart Bazar (Pattom)"],
#             [8.5085, 76.9492, "Supplyco Supermarket (Thampanoor)"]
#         ]
#         for shop in fallback_shops:
#             heat_data.append([shop[0], shop[1]])
#             folium.CircleMarker(
#                 location=[shop[0], shop[1]],
#                 radius=5,
#                 color="red",
#                 fill=True,
#                 fill_color="red",
#                 fill_opacity=0.8,
#                 tooltip=f"<b>Competitor:</b> {shop[2]}"
#             ).add_to(marker_layer)

#     # Inject the layers onto your main map object 'm'
#     HeatMap(heat_data, name="Competition Heatmap", radius=20, blur=15).add_to(m)
#     marker_layer.add_to(m)
    
#     # Layer control toggle panel 
#     folium.LayerControl().add_to(m)
#     print(f"Success! Integrated {len(heat_data)} total competitors onto the map layers.")

# except Exception as e:
#     print(f"Internet request paused or failed: {e}. Keeping default map settings.")
# =========================================================================

m.save("kerala_business_map.html")