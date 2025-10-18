import customtkinter as ctk
from components import SimpleEntry, InformationDisplay, MapCanvas
from settings import BLACK, WHITE, HEIGHT, WIDTH, MINIMUM_HEIGHT, MINIMUM_WIDTH, FONT, ANIMATION_FRAMES
from utilities import get_species_data
from pygbif import occurrences, maps, species
from threading import Thread
from time import sleep


class App(ctk.CTk):
	def __init__(self):
		# window customization
		super().__init__()
		ctk.set_appearance_mode("dark")
		self.geometry(f"{WIDTH}x{HEIGHT}")
		self.minsize(MINIMUM_WIDTH, MINIMUM_HEIGHT)
		self.title("Species Distribution Mapper")
		
		# data
		self.font = FONT
		self.animation_frames = ANIMATION_FRAMES
		self.sp_name = ctk.StringVar()
		self.animation_text = ctk.StringVar()
		self.main_frame = None
		self.loading_frame = None 
		self.entry_field = None
		self.frame_idx = 0
		self.thread_return = [None] # thread return will get the result of searching while in a thread

		#self.rowconfigure(0, weight= 1, uniform= "a")
		#self.rowconfigure(1, weight= 5, uniform= "a")
		#self.columnconfigure((0, 1), weight= 1, uniform= "a")
		#self.columnconfigure(2, weight= 5, uniform= "a")

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
			self.main_frame.columnconfigure(0, weight= 1, uniform= "a")
			self.main_frame.columnconfigure(1, weight= 2, uniform= "a")
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
	
if __name__ == "__main__":
	App()

