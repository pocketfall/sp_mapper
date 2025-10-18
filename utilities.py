from pygbif import occurrences, species, maps

def get_species_data(sp_name: str= None) -> dict:
	if sp_name is None:
		return None
	else:
		try:
			# transform sp_name from string to int id of the gbif backend
			key = species.name_backbone(name= sp_name, rank= "species")["usageKey"]

			# seach for the species and only show results with lat/lon data
			data = occurrences.search(taxonKey= key, hasCoordinate= True, limit= 500)["results"]
			
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

