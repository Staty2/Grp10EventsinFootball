#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 14:34:20 2023

@author: felix
"""
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from mplsoccer import Pitch, FontManager, Sbopen
from mplsoccer import Pitch
pitch = Pitch()

            
def regorganise_match(match):
    # Open the JSON file and load its contents
    with open(match) as f:
        data = json.load(f)
    
    # Find the index of the first JSON object that has a "index" of 3
    for i, item in enumerate(data):
        if item["index"] == 3:
            index = i
            break
    
    # Create a new list containing only the JSON objects starting from the desired index
    new_data = data[index:]
    
    # Convert the JSON objects to a Pandas DataFrame and add the "type.id" and "type.name" columns
    df = pd.json_normalize(new_data)
    
    column_order = ['id', 'index', 'period', 'type.id', 'type.name', 'timestamp', 'minute', 'second', 'possession', 'possession_team.id',
                    'possession_team.name', 'play_pattern.id', 'play_pattern.name', 'team.id', 'team.name', 'player.id', 'player.name',
                    'position.id', 'position.name', 'location', 'duration', 'under_pressure', 'counterpress', 'related_events', 'pass.recipient.id', 
                    'pass.recipient.name', 'pass.length','pass.angle','pass.height.id', 'pass.height.name', 'pass.end_location', 
                    'pass.body_part.id', 'pass.body_part.name', 'pass.type.id', 'pass.type.name', 'pass.outcome.id', 'pass.outcome.name','carry.end_location', 
                    'ball_receipt.outcome.id', 'ball_receipt.outcome.name', 'substitution.outcome.id', 'substitution.outcome.name',
                    'substitution.replacement.id', 'substitution.replacement.name', 'bad_behaviour.card.id', 'bad_behaviour.card.name', 
                    'tactics.formation', 'duel.type.id', 'duel.type.name', 'duel.outcome.id', 'duel.outcome.name', 'interception.outcome.id',
                    'interception.outcome.name', 'shot.statsbomb_xg', 'shot.end_location', 'shot.key_pass_id', 'shot.outcome.id''shot.outcome.name',
                    'shot.body_part.id', 'shot.body_part.name', 'shot.technique.id', 'shot.technique.name', 'shot.type.id', 'shot.type.name',
                    'shot.freeze_frame.location', 'shot.freeze_frame.player.id', 'shot.freeze_frame.player.name', 'shot.freeze_frame.position.id', 
                    'shot.freeze_frame.position.name', 'shot.freeze_frame.teammate', 'goalkeeper.technique.id', 'goalkeeper.technique.name',
                    'goalkeeper.body_part.id', 'goalkeeper.body_part.name', 'goalkeeper.position.id', 'goalkeeper.position.name',
                    'goalkeeper.type.id', 'goalkeeper.type.name', 'goalkeeper.outcome.id', 'goalkeeper.outcome.name', 'dribble.outcome.id',
                    'dribble.outcome.name', 'dribble.overrun', 'dribble.nutmeg', 'ball_receipt.outcome.id', 'ball_receipt.outcome.name']
    
    # Reorder the columns
    df = df.reindex(columns=column_order)
    
    return df





def findingallmatches(team1,team2,matches):
    '''
    findingallmatches('Manchester City WFC','Chelsea FCW','18_19.json')
    '''
    match_ids = []
    # Load JSON object
    with open(matches) as f:
        match_data = json.load(f)
    
    for obj in match_data:
        # Check if the home team is Manchester City WFC and the away team is Chelsea FCW
        if obj['home_team']['home_team_name'] == team1 and obj['away_team']['away_team_name'] == team2:
            # Print the match ID if the teams match
            match_id = obj['match_id']
            match_ids.append(match_id)
        elif obj['home_team']['home_team_name'] == team2 and obj['away_team']['away_team_name'] == team1:
            # Otherwise, print a message indicating that the teams do not match
            match_id = obj['match_id']
            match_ids.append(match_id)

    return match_ids





def findingallnames(matches):
    '''
    findingallnames('18_19.json')
    '''
    team_names = []
    # Load JSON object
    with open(matches) as f:
        match_data = json.load(f)
    for obj in match_data:
        # Check if the home team is Manchester City WFC and the away team is Chelsea FCW
        team = obj['home_team']['home_team_name']
        # Print the match ID if the teams match
        team_names.append(team)    
    team_names = list(set(team_names))
    return team_names



    

def firstsub_web_network(match_df):
    df = match_df.copy()
    teams = list(set(df['possession_team.name']))
    #only show the passes by chelsea
    df = df[df['team.name']==teams[0]]
    #create new columns
    df['passer'] = df['player.id']
    df['recipient'] = df['pass.recipient.id']
    df['position'] = df['position.name']
    #create new df of players who passed
    df_passes = df[df['type.name']=='Pass']
    df_goodpasses = df_passes[df_passes['pass.outcome.name']!='Incomplete']
    #do all passes before first sub
    df_subs = df[df['type.name']=='Player Off']
    df_subs = df_subs['minute']
    first_sub = df_subs.min()
    df_goodpasses = df_goodpasses[df_goodpasses['minute']<first_sub]
    #find averge locations of each players passes
    df_goodpasses[['x', 'y']] = df_goodpasses['location'].apply(lambda x: pd.Series([x[0], x[1]]))
    df_avlocations = df_goodpasses.groupby('passer').agg({'x':['mean'],'y':['mean','count'],'position.id':'first'})
    df_avlocations.columns = ['x','y','count','position']
    #find passes between each player
    df_passbetween = df_goodpasses.groupby(['passer','recipient']).id.count().reset_index() 
    df_passbetween.rename({'id':'pass_count'}, axis ='columns', inplace=True)
    #megre passes between and avergae locations
    df_passbetween = df_passbetween.merge(df_avlocations, left_on='passer', right_index=True)
    df_passbetween = df_passbetween.merge(df_avlocations, left_on='recipient', right_index =True, suffixes =['','_end'])
    # #only look at high amount of passes
    # df_passbetween = df_passbetween[df_passbetween['pass_count']>3]
    
    #visualise it in mplsoccer
    #make lines bigger or smaller depending on the count
    MAX_LINE_WIDTH = 18
    MAX_MARKER_SIZE = 3000
    df_passbetween['width'] = (df_passbetween.pass_count / df_passbetween.pass_count.max() *
                               MAX_LINE_WIDTH)
    df_avlocations['marker_size'] = (df_avlocations['count']
                                             / df_avlocations['count'].max() * MAX_MARKER_SIZE)
    
    #also make them more or less transparent
    MIN_TRANSPARENCY = 0.3
    color = np.array(to_rgba('white'))
    color = np.tile(color, (len(df_passbetween), 1))
    c_transparency = df_passbetween.pass_count / df_passbetween.pass_count.max()
    c_transparency = (c_transparency * (1 - MIN_TRANSPARENCY)) + MIN_TRANSPARENCY
    color[:, 3] = c_transparency
    
    
    #display the positions
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
    fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=True, tight_layout=False)
    fig.set_facecolor("#22312b")
    pass_lines = pitch.lines(df_passbetween.x, df_passbetween.y,
                             df_passbetween.x_end, df_passbetween.y_end, lw=df_passbetween.width,
                              color=color, zorder=1, ax=ax)
    pass_nodes = pitch.scatter(df_avlocations.x, df_avlocations.y,
                                s=df_avlocations.marker_size,
                                color='red', edgecolors='black', linewidth=1, alpha=1, ax=ax)
    fig.suptitle(f'{teams[0]} average positions and passes against\n {teams[1]} before first sub on minute {first_sub}', color='white', fontsize=35)
    
    #label the nodes
    formation_dict = {1: 'GK', 2: 'RB', 3: 'RCB', 4: 'CB', 5: 'LCB', 6: 'LB', 7: 'RWB',
                      8: 'LWB', 9: 'RDM', 10: 'CDM', 11: 'LDM', 12: 'RM', 13: 'RCM',
                      14: 'CM', 15: 'LCM', 16: 'LM', 17: 'RW', 18: 'RAM', 19: 'CAM',
                      20: 'LAM', 21: 'LW', 22: 'RCF', 23: 'ST', 24: 'LCF', 25: 'SS'}
    df_avlocations['position_abrv'] = df_avlocations.position.map(formation_dict)
    
    for index, row in df_avlocations.iterrows():
        pitch.annotate(row.position_abrv, xy=(row.x, row.y), c='white', va='center',
                       ha='center', size=16, weight='bold', ax=ax)

    return





matches = findingallmatches('Manchester City WFC','Chelsea FCW','18_19.json')
match_df = regorganise_match(f'{matches[0]}.json')
firstsub_web_network(match_df)



