import json
import numpy as np 
import read_data

events = read_data.load_events()
players = read_data.load_players()
playerank = read_data.load_playerank()
matches = read_data.load_matches()
nations = ['Italy','England','Germany','France','Spain','European_Championship','World_Cup']

def getMatchPlayers(matchId):
	matchplayers = []
	for match in matches:
		if match['wyId'] == matchId:
			for team, info in match['teamsdata'].items():
				matchplayers.append([p['playerId'] for p in info['formation']['lineup']] + [p['playerIn'] for p in info['formation']['substitutions']])
			return matchplayers

def flow_centrality_nation(nation):
	match_list_nation = []
	list_nation_ev = []
	for ev in events[nation]:
		list_nation_ev.append(ev)
		if ev['matchId'] not in match_list_nation:
			match_list_nation.append(ev['matchId'])
	
	df_match_ev = pd.DataFrame(list_nation_ev)
	
	player_flow_centrality = []
	for match in match_list_nation:
		print("Match: ", match)
		matchplayers = getMatchPlayers(match)
		df_ev_match = df_match_ev[df_match_ev['matchId']==match]
		df_team = df_ev_match[['playerId','eventSec']].rename(columns={'playerId':'sender'})
		df_team['receiver'] = df_team['sender'].shift(-1).dropna()

		#create list with sendere and receiver
		df_team1 = []
		for i,row in df_team.iterrows():
			if row['sender'] == row['receiver']:
				pass        
			else:
				df_team1.append([row['sender'],row['receiver']])
		df_team1 = pd.DataFrame(df_team1, columns=['sender','receiver'])  
		df_team1_count = df_team1.groupby(['sender','receiver']).size().reset_index(name="Time")

		# networkX team 1
		g = nx.Graph()
		for i,row in df_team1_count.iterrows():
			g.add_edge(row['sender'],row['receiver'],weight=row['Time'])
		for player in matchplayers: 
			try:
				player_performances[player].append()
				player_flow_centrality.append(nx.current_flow_betweenness_centrality(g)[player])
			except KeyError:
				if player not in g:
					pass
				else:
					player_performances[player] = [nx.current_flow_betweenness_centrality(g)[player]]

	print("Compute Average Flow centrality for all players...")
	for player, flow in player_performances.items():
		player_performances[player] = np.mean(flow)

	print("Write performances to JSON file!")
	with open('avg_flow_centrality_'+nation+'.txt', 'w') as fp:
			json.dump(player_performances, fp)

if __name__ == "__main__":
	for nation in nations:
		flow_centrality_nation(nation)
