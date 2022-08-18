from typing import Mapping
import requests 
import pandas as pd
import logging
import argparse
from copy import copy

API_KEY = 'k_d8xn0mac'
############################################################
#                Shows to track
############################################################
## NOTE I've gone ahead and grabbed the id's of the shows for simplicity sake and listed them below
# Game of Thrones: tt0944947
# Stranger Things: tt4574334
# Chernobyl: tt7366338
# The Mandalorian: tt8111088
# Mr. Robot: tt4158110


MAPPING = {
	"game of thrones": 'tt0944947',
	"stranger things": 'tt4574334',
	'chernobyl': 'tt7366338',
	'the mandalorian': 'tt8111088',
	'mr robot': 'tt4158110'
}

class ImdbSeries():
	base_url = 'https://imdb-api.com/en/API/'

	def __init__(self,title,imdb_id) -> None:
		self.title = title
		self.imdb_id = imdb_id

	def get_title_data(self) -> dict:
		"""
		This will pull all the relevant data from the title api
		"""
		url = f"{self.base_url}Title/{API_KEY}/{self.imdb_id}"
		payload = {}
		headers= {}
		response = requests.request("GET", url, headers=headers, data = payload)
		return response.json()

	def get_episode_data(self,seasons:list) -> dict:
		"""
		This will return information for each episode. Since there are multiple episodes for a season, the return dict will have the season as a key
		and the value will be a nested dict of the response from the api of the episodes for that season.

		Returns:
			_type_: Dictionary of the json response from the api
		"""
		d = {}
		for season in seasons:
			url = f"{self.base_url}SeasonEpisodes/{API_KEY}/{self.imdb_id}/{season}" ## form the url
			payload = {}
			headers= {}
			response = requests.request("GET", url, headers=headers, data = payload)
			d[season] = response.json()
		return d

def filter_title_data(title_data:dict) -> dict:
	"""
	This will remove all the unnecessary fields from the collected data

	Returns:
		_type_: Dictionary
	"""
	fields = ['id','title','stars','starList','actorList','imDbRating','imDbRatingVotes','tvSeriesInfo','tvEpisodeInfo']
	return {k:v for k,v in title_data.items() if k in fields}


def make_series_df(series_data:dict) -> pd.DataFrame:
	"""
	This will make a data frame for each series consisting of relevant fields

	Returns:
		_type_: DataFrame with essential fields
	"""
	filt = {k:v for k,v in series_data.items() if k not in ['starList','actorList','tvSeriesInfo','tvEpisodeInfo','stars']}
	df = pd.DataFrame(filt,index = [0])
	return df


def make_episodes_df(episodes:dict) -> pd.DataFrame:
	""" Produces a data frame of all the episodes with the associated season, rating, and other fields for a series

	Args:
		episodes (dict): The json provided from the get_episode_data

	Returns:
		pd.DataFrame: Data frame of all aired episodes for a series
	"""
	temp_df = pd.DataFrame()
	for i in episodes.values():
		series_id = i['imDbId']
		temp = i['episodes']
		for j in temp:
			df = pd.DataFrame(j,index = [0]).drop(['plot','image'],axis = 1)
			df['seriesId'] = series_id
			
			temp_df = pd.concat([temp_df,df],axis = 0)
	return temp_df

def make_actor_df(title_data:dict) -> pd.DataFrame:
	""" Produces a dataframe of all the actors with the character they acted as for a given series

	Args:
		title_data (dict): The json data captured from the title api

	Returns:
		pd.DataFrame: Data frame of actors
	"""
	series_id = title['id']
	actors = title_data['actorList']
	df = pd.DataFrame()
	for a in actors:
		temp_actor_df = pd.DataFrame(a,index = [0]).drop(['image'],axis = 1)
		temp_actor_df['seriesId'] = series_id
		df = pd.concat([df,temp_actor_df],axis = 0)
	return df
			

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--single',help='Will only fetch data for a single series, provided it is in the mapping',nargs='+')
	args = parser.parse_args()
	series_to_run = copy(MAPPING)
	all_series = list(series_to_run.keys()) ## copy of the original keys from the mapping 
	
	if args.single:
		tv_show = args.single[0].lower() ## convert to lower case since for matching
		if tv_show not in MAPPING.keys():
			logging.error(f" The show {tv_show} is not in the mapping of series, please add it in the script with the associated id. Exiting now")
			exit()
		else:
			for k in all_series:
				if k != tv_show: ## delete all the other series
					del series_to_run[k]

	print(series_to_run)
	logging.basicConfig(level=logging.INFO)
	episodes_df = pd.DataFrame()
	series_df = pd.DataFrame()
	actors_df = pd.DataFrame()
	logging.info("Beginning to query the title API")
	for series,series_id in series_to_run.items():
		############################################################
		#       Populate the series data frame
		############################################################
		s = ImdbSeries(series,series_id)
		logging.info(f"Successfully grabbed {series}")
		title = s.get_title_data()
		title_filtered = filter_title_data(title)
		temp = make_series_df(title_filtered)
		series_df = pd.concat([series_df,temp],axis = 0)
		############################################################
		#     Populate the episodes data frame
		############################################################
		logging.info(f"Compiling the episodes for {series}")
		seasons = title_filtered['tvSeriesInfo']['seasons']
		episodes = s.get_episode_data(seasons)
		temp_episodes = make_episodes_df(episodes)
		episodes_df = pd.concat([episodes_df,temp_episodes],axis = 0)

		############################################################
		#    Populate the actors data frame
		############################################################
		logging.info(f"Compiling the actors for {series}")
		temp_actors = make_actor_df(title_filtered)
		actors_df = pd.concat([actors_df,temp_actors],axis = 0)

	############################################################
	#    Output to CSV
	############################################################
	logging.info("Writing CSV's")
	series_df.to_csv("Series.csv",index = False)
	episodes_df.to_csv("Episodes.csv",index = False)
	actors_df.to_csv("Actors.csv",index = False)

	print("Complete!")



		




