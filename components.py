import customtkinter as ctk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk 
from matplotlib.figure import Figure
from mpl_toolkits.basemap import Basemap

class InformationDisplay(ctk.CTkScrollableFrame):
	"""
	Scrollable frame that displays information about the species, namely max and min longitude/latitude and
	the countries it has been spotted in
	"""
	def __init__(self, parent, countries: set, lat_range: list[float], lon_range: list[float], font: tuple):
		super().__init__(master= parent, fg_color= "transparent")

		processed_data = self.preprocess_data(countries, lat_range, lon_range)
		
		info_title = ctk.CTkLabel(self, text= "Information", font= font).pack(expand= True, fill= "both", pady= 10)
		for data in processed_data[::-1]:
			if data == processed_data[0]:
				ctk.CTkLabel(self, text= f"Has been seen in", font= font).pack(fill= "both", expand= True, pady= 10)
				ctk.CTkLabel(self, text= data, font= font).pack(fill= "both", expand= True)
			else:
				ctk.CTkLabel(self, text= data, font= font).pack(fill= "both", expand= True, pady= 10)
	
	def preprocess_data(self, countries, lat_range, lon_range) -> tuple[str]:
		country_processed = "\n".join(list(countries))
		lat_processed = f"Maximum latitude: {round(lat_range[1], 2)}\nMinimum latitude: {round(lat_range[0], 2)}"
		lon_processed = f"Maximum longitude: {round(lon_range[1])}\nMinimum longitude: {round(lon_range[0], 2)}"

		return (country_processed, lat_processed, lon_processed)

class SimpleEntry(ctk.CTkFrame):
	"""
	Class that creates a frame containing a CTkLabel, CTkEntry and CTkButton in a row
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
	def __init__(self, parent, data: dict):
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

