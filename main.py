import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from pygbif import occurrences, maps, species
from mpl_toolkits.basemap import Basemap
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

def get_species_data(sp_name: str= None) -> dict:
	if sp_name is None:
		return None
	else:
		try:
			# transform sp_name from string to int id of the gbif backend
			key = species.name_backbone(name= sp_name, rank= "species")["usageKey"]

			# seach for the species and only show results with lat/lon data
			data = occurrences.search(taxonKey= key, hasCoordinate= True, basisOfRecord= "HUMAN_OBSERVATION", limit= 300)["results"]
			
			# occurrences.search()["results"] datastructure: list[dict]
			# [{occurrence1}, {occurrence2}, ... {occurrenceN}]
			filters = ["decimalLongitude", "decimalLatitude", "scientificName", "year", "month", "day", 
					   "occurrenceRemarks", "country", "basisOfRecord", "rightsHolder", "individualCount",
					   "occurrenceID"]
			
			# compiling data dictionaries into one dictionary
			# create empty dictionary
			compiled_data = {}
			
			# access dictionaries one by one
			for dictionary in data:
				# get keys from filters
				for key in filters:
					if key not in compiled_data.keys(): # add an empty list to the dictionary if the key does not exist in it
						compiled_data[key] = []
					if key in dictionary.keys():
						compiled_data[key].append(dictionary[key])
			return compiled_data
		except:
			return "SPECIES NAME IS WRITTEN WRONG OR NOT AVAILABLE"

class App(ctk.CTk):
	def __init__(self):
		# window customization
		super().__init__()
		ctk.set_appearance_mode("dark")
		self.geometry("1200x800")
		self.minsize(1000, 600)
		self.title("Species Distribution Mapper")
		
		# variables
		self.font = ("Comic sans MS", 24, "bold")
		self.sp_name = ctk.StringVar()

		self.rowconfigure((0, 1, 2, 3, 4), weight= 1, uniform= "a")
		self.columnconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9), weight= 1, uniform= "a")

		self.map = None
		self.create_widgets()

		# close window event
		self.protocol("WM_DELETE_WINDOW", self.terminate)

		self.mainloop()
	
	def terminate(self):
		"""
		Method needed to terminate the application because the Basemap class doesn't play nice
		when an update occurs, so it doesn't allow the program to stop
		"""
		import sys
		sys.exit()
		quit()
	
	def create_widgets(self):
		# layout
		# 5 x 9 matrix where the left 4 columns are for info on the species and the right is dedicated to the distribution map
		SimpleEntry(parent= self, 
			  entry_variable= self.sp_name, 
			  frame_color= "red", 
			  font= self.font,
			  button_func= self.search_sp).grid(row= 0, column= 1, rowspan= 2, columnspan= 6, padx= 10, pady= 10, sticky= "ew")
	
	def search_sp(self):
		data = get_species_data(sp_name= self.sp_name.get())

		if self.map:
			self.clear_info_and_map()
			self.map.grid_forget()
			self.map.destroy()
		self.map = MapCanvas(parent= self, data= data)
		self.map.grid(row= 2, column= 6, rowspan= 2, columnspan= 5)

	def clear_info_and_map(self):
		self.map.grid_forget()
		self.map.destroy()

class SimpleEntry(ctk.CTkFrame):
	"""
	Class that creates a frame containing a CTkLabel and a CTkEntry in a row
	"""
	def __init__(self, parent, entry_variable, frame_color, font, button_func):
		super().__init__(master= parent, fg_color= "transparent")
		ctk.CTkLabel(self, text= "Enter scientific name: ", font= font).pack(side= "left", fill= "both", padx= 10)
		ctk.CTkEntry(self, textvariable= entry_variable, font= font).pack(side= "left", fill= "x", expand= True, padx= 10)
		ctk.CTkButton(self, command= button_func, text= "SEARCH", font= font).pack(side= "bottom", fill= "both", expand= True)

class MapCanvas(ctk.CTkFrame):
	"""
	Class that creates a frame containing a canvas with a Basemap and a scatter plot on the map
	"""
	def __init__(self, parent: str, data: dict):
		super().__init__(master= parent, fg_color= "red")
		lat, lon = data["decimalLatitude"], data["decimalLongitude"]
		sp_name = data["scientificName"][0].split(" ")
		sp_name = f"{sp_name[0]} {sp_name[1]}"

		self.fig = Figure(figsize= (7, 4), dpi= 100)

		map_canvas = self.draw_map(lat= lat, lon= lon, sp_name= sp_name).get_tk_widget()
		map_canvas.pack(fill= "both", expand= True)
	
	def draw_map(self, lat: list, lon: list, sp_name: str) -> FigureCanvasTkAgg:
		# canvas and map
		ax = self.fig.add_subplot()
		canvas = FigureCanvasTkAgg(self.fig, master= self)
		bio_plot = Basemap(ax= ax)

		# add coastlines and countries
		bio_plot.drawcoastlines(linewidth= .3)
		bio_plot.drawcountries(linewidth= .3)

		# add longitude and latitude lines
		lat_lines = np.arange(-90.,91.,30.)
		lon_lines = np.arange(-180.,181.,60.)
		bio_plot.drawmeridians(lon_lines, labels= [False, True, True, False])
		bio_plot.drawparallels(lat_lines, labels= [False, True, True, False])

		# add distribution data
		ax.scatter(lon, lat, label= sp_name, alpha= .75)

		# legend
		ax.legend()

		# toolbar
		toolbar = NavigationToolbar2Tk(canvas, self)
		toolbar.update()

		return canvas
	
if __name__ == "__main__":
	App()

