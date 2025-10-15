import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from pygbif import occurrences, maps, species
from mpl_toolkits.basemap import Basemap


## get distribution data
#key = species.name_backbone(name= "Engraulis ringens", rank= "species")["usageKey"]
#
## seach for the species and only show results with lat/lon data
#data = occurrences.search(taxonKey= key, hasCoordinate= True, basisOfRecord= "HUMAN_OBSERVATION", limit= 300)["results"]
#
## occurrences.search()["results"] datastructure: list[dict]
## [{occurrence1}, {occurrence2}, ... {occurrenceN}]
#filters = ["decimalLongitude", "decimalLatitude", "scientificName", "year", "month", "day", 
#		   "occurrenceRemarks", "country", "basisOfRecord", "rightsHolder", "individualCount",
#		   "occurrenceID"]
#
## compiling data dictionaries into one dictionary
## create empty dictionary
#compiled_data = {}
#
## access dictionaries one by one
#for dictionary in data:
#	# get keys from filters
#	for key in filters:
#		if key not in compiled_data.keys(): # add an empty list to the dictionary if the key does not exist in it
#			compiled_data[key] = []
#		if key in dictionary.keys():
#			compiled_data[key].append(dictionary[key])
## print(compiled_data.keys())
## it worked !
## print(compiled_data["decimalLatitude"])
#
## separating into variables
#lat, lon = compiled_data["decimalLatitude"], compiled_data["decimalLongitude"]
#individual_count = compiled_data["individualCount"]
#rights_holder = compiled_data["rightsHolder"]
#scientific_name = compiled_data["scientificName"][0].split(" ")
#scientific_name = f"{scientific_name[0]} {scientific_name[1]}"
#year, month, day = compiled_data["year"], compiled_data["month"], compiled_data["day"]
#
## draw map
#m = Basemap()
#m.drawcoastlines(linewidth= .3)
#m.drawcountries(linewidth= .3)
#
## assign lat and lon lines for the map
#lat_lines = np.arange(-90.,91.,30.)
#lon_lines = np.arange(-180.,181.,60.)
#m.drawmeridians(lon_lines, labels= [False, True, True, False])
#m.drawparallels(lat_lines, labels= [False, True, True, False])
#
## missing: distribution data
## add distribution of species
#plt.scatter(lon, lat, 
#			label= scientific_name,
#			alpha= .75)
#plt.legend()
#
## show map
## plt.show() # instead of show we want to display it in a canvas inside a tkinter app

# uncomment the above code for a working block that displays a distribution graph of Engraulis ringens

# creating GUI app

# font configuration
font = ("Comic sans MS", 24, "bold")

# window and configuration
root = ctk.CTk()
ctk.set_appearance_mode("dark")
root.geometry("1200x800")
root.minsize(1000, 600)
root.title("Distribution Mapper")

# layout
# 5 x 9 matrix where the left 4 columns are for info on the species and the right is dedicated to the distribution map
root.rowconfigure((0, 1, 2, 3, 4), weight= 1, uniform= "a")
root.columnconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9), weight= 1, uniform= "a")

# add label and input widget
scientific_name_gui = ctk.StringVar()
ctk.CTkLabel(root, text= "Enter scientific name:", font= font).grid(row= 0, column= 0, columnspan= 3, sticky= "nsew", padx= 10, pady= 10,
																	rowspan= 2)
ctk.CTkEntry(root, textvariable= scientific_name_gui, font= (font[0], 20)).grid(row= 0, column= 3, columnspan= 5, sticky= "ew", padx= 10, pady= 10,
																				rowspan= 2)

# canvas widget
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# make mock plot
x, y = np.arange(0, 10, 1), np.arange(0, 10, 1)

plot_frame = ctk.CTkFrame(root, fg_color= "red")
fig = Figure(dpi= 100)#figsize= (5, 4), dpi= 100)
canvas = FigureCanvasTkAgg(fig, master= plot_frame)
ax = fig.add_subplot()
ax.scatter(x, y)
ax.plot(x, y)
canvas.get_tk_widget().pack(fill= "both", expand= True)
plot_frame.grid(row= 2, column= 4, columnspan= 5, rowspan= 2)

# add data to the left side

# mainloop
root.mainloop()
