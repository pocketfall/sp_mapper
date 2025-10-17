import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from pygbif import occurrences, maps, species
from mpl_toolkits.basemap import Basemap
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from threading import Thread
from time import sleep

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
		
		# data
		self.font = ("Comic sans MS", 24, "bold")
		self.animation_frames = ["|", "/", "--", "\\"]
		self.sp_name = ctk.StringVar()
		self.animation_text = ctk.StringVar()
		self.main_frame = None
		self.loading_frame = None 
		self.entry_field = None
		self.frame_idx = 0
		self.thread_return = [None] # thread return will get the result of searching while in a thread

		self.rowconfigure(0, weight= 1, uniform= "a")
		self.rowconfigure(1, weight= 5, uniform= "a")
		self.columnconfigure((0, 1), weight= 1, uniform= "a")
		self.columnconfigure(2, weight= 5, uniform= "a")

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
		# 2x3 where the 3rd column has a weight of 5
		if self.main_frame is None:
			self.main_frame = ctk.CTkFrame(self, fg_color= "magenta")
			self.main_frame.rowconfigure(0, weight= 1, uniform= "a")
			self.main_frame.rowconfigure(1, weight= 5, uniform= "a")
			self.main_frame.columnconfigure((0, 1), weight= 1, uniform= "a")
			self.main_frame.columnconfigure(2, weight= 5, uniform= "a")
			self.main_frame.pack(expand= True, fill= "both")

		self.entry_field = SimpleEntry(parent= self.main_frame, 
							entry_variable= self.sp_name, 
							frame_color= "red", 
							font= self.font, 
							button_func= self.search_sp)
		self.entry_field.grid(row= 0, column= 0, rowspan= 1, columnspan= 3, padx= 10, pady= 10, sticky= "ew")
	
	def search_sp(self):
		"""
		Use the gbif API to search for the species entered in the Entry field
		and create a distribution map if it does not already exist, otherwise delete
		the existing one before creating another
		"""
		# clear screen to display loading frame
		self.clear_screen()
		self.create_loading_screen()
		#self.loading_frame.place(relx= .5, rely= .5, anchor= "center")

		# search the data using a thread
		search_thread = Thread(target= self.thread_search, args= (self.sp_name.get(), self.thread_return))
		search_thread.start()

		# create a loading screen while requesting data
		while search_thread.is_alive():
			self.animate()
		self.loading_frame.destroy()

		# add the widgets again
		self.create_widgets()

		data = self.thread_return[0]
		self.frame_idx = 0

		# draw map when data is available
		self.map = MapCanvas(parent= self.main_frame, data= data)
		self.map.grid(row= 1, column= 2, padx= 5, pady= 5, sticky= "new")

		# add species info to a left panel
		self.list_info(data)
	
	def create_loading_screen(self):	
		self.loading_frame = ctk.CTkFrame(self.main_frame, fg_color= "transparent")
		loading_label = ctk.CTkLabel(self.loading_frame, textvariable= self.animation_text, font= self.font, text_color= "black")
		loading_label.pack(expand= True, fill= "both")
		self.loading_frame.place(relx= .5, rely= .5, anchor= "center", relheight= 1, relwidth= 1)
	
	def clear_screen(self):
		for child in self.main_frame.winfo_children():
			child.destroy()
		self.main_frame.update()
		print(self.main_frame.winfo_children())
	
	def thread_search(self, sp_name: str, return_list: list) -> None:
		data = get_species_data(sp_name= sp_name)
		return_list[0] = data

	def animate(self):
		self.main_frame.update()
		sleep(.33)
		self.frame_idx += 1
		if self.frame_idx >= len(self.animation_frames):
			self.frame_idx = 0

		self.animation_text.set(str(self.animation_frames[self.frame_idx]))
		print(self.animation_frames[self.frame_idx])
	
	def list_info(self, data):
		countries = set(data["country"])
		latitude_range = [min(data["decimalLatitude"]), max(data["decimalLatitude"])]
		longitude_range = [min(data["decimalLongitude"]), max(data["decimalLongitude"])]

		self.sp_info = InformationDisplay(self.main_frame, 
									countries= countries, 
									lat_range= latitude_range, 
									lon_range= longitude_range,
									font= self.font)
		self.sp_info.grid(row= 1, column= 0, rowspan= 1, columnspan= 2, sticky= "nsew", padx= 5, pady= 5)
		

	def clear_info_and_map(self):
		self.map.destroy()
		self.sp_info.destroy()

class InformationDisplay(ctk.CTkFrame):
	def __init__(self, parent, countries: set, lat_range: list[float], lon_range: list[float], font: tuple):
		super().__init__(master= parent, fg_color= "cyan")

		processed_data = self.preprocess_data(countries, lat_range, lon_range)
		
		info_title = ctk.CTkLabel(self, text= "Information", font= font).pack(expand= True, fill= "both")
		for data in processed_data:
			ctk.CTkLabel(self, text= data, font= font).pack(fill= "both")
	
	def preprocess_data(self, countries, lat_range, lon_range) -> tuple[str]:
		country_processed = "\n".join(list(countries))
		print(country_processed)
		lat_processed = f"Maximum latitude: {lat_range[1]}\nMinimum latitude: {lat_range[0]}"
		lon_processed = f"Maximum longitude: {lon_range[1]}\nMinimum longitude: {lon_range[0]}"

		return (country_processed, lat_processed, lon_processed)

class SimpleEntry(ctk.CTkFrame):
	"""
	Class that creates a frame containing a CTkLabel and a CTkEntry in a row
	"""
	def __init__(self, parent, entry_variable, frame_color, font, button_func):
		super().__init__(master= parent, fg_color= frame_color)
		ctk.CTkLabel(self, text= "Enter scientific name: ", font= font).pack(side= "left", fill= "both", padx= 10)
		ctk.CTkEntry(self, textvariable= entry_variable, font= font, width= 500).pack(side= "left", fill= "x", expand= True, padx= 10)
		ctk.CTkButton(self, command= button_func, text= "SEARCH", font= font).pack(side= "left", fill= "both", expand= True)

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

