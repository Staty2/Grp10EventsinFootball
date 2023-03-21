#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 14:48:10 2023

@author: felix
"""

from statsbombpy import sb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from mplsoccer import Pitch, FontManager, Sbopen
from mplsoccer import Pitch
pitch = Pitch()

#Combining all 3 seasons into one dataframe
matches2021 = sb.matches(competition_id=37, season_id = 90) #a specific season of the womens FA Super League, also use season ID 90 (20-21), 42 (19-20),4(18-19)
matches1920 = sb.matches(competition_id=37, season_id = 42)
matches1819 = sb.matches(competition_id=37, season_id = 4)
frames = [matches1819, matches1920, matches2021]
FAWSL = pd.concat(frames)


def findingallmatches(team1, team2, dataframe):
    '''
    findingallmatches('Manchester City WFC','Chelsea FCW', FAWSL)
    '''
    match_ids = []
    
    for index, row in dataframe.iterrows():
        # Check if the home team is team1 and the away team is team2
        if row['home_team'] == team1 and row['away_team'] == team2:
            # Print the match ID if the teams match
            match_id = row['match_id']
            match_ids.append(match_id)
        elif row['home_team'] == team2 and row['away_team'] == team1:
            # Otherwise, print a message indicating that the teams do not match
            match_id = row['match_id']
            match_ids.append(match_id)
    
    return match_ids

def findingallnames(dataframe):
    '''
    findingallnames(FAWSL)
    '''
    # Extract the unique team names from the home and away team columns
    home_teams = set(dataframe['home_team'])
    away_teams = set(dataframe['away_team'])
    
    # Combine the unique team names from both columns into a set
    team_names = home_teams.union(away_teams)
    
    # Convert the set to a list and return it
    return list(team_names)



def firstsub_web_network(team1,team2,match_df):
    '''
    firstsub_web_network('Manchester City WFC','Chelsea FCW',events)
    '''
    #make a cpoy of the dataframe
    df = match_df.copy()
    #find all the positions and abbriviate them (this is for later)
    
    #only use the passes by team1
    df = df[df['team']==team1]
    #create new columns
    df['passer'] = df['player']
    df['recipient'] = df['pass_recipient']
    df['position'] = df['position']
    #create new df of players who passed
    df_passes = df[df['type']=='Pass']
    df_goodpasses = df_passes[df_passes['pass_outcome']!='Incomplete']
    #do all passes before first sub
    df_subs = df[df['type']=='Player Off']
    df_subs = df_subs['minute']
    first_sub = df_subs.min()
    df_goodpasses = df_goodpasses[df_goodpasses['minute']<first_sub]
    #find averge locations of each players passes
    df_goodpasses[['x', 'y']] = df_goodpasses['location'].apply(lambda x: pd.Series([x[0], x[1]]))
    df_avlocations = df_goodpasses.groupby('passer').agg({'x':['mean'],'y':['mean','count'],'position':'first'})
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
    fig.suptitle(f'{team1} average positions and passes against\n {team2} before first sub on minute {first_sub}', color='white', fontsize=35)
    
    #abbrivate all the positions 
    formation_dict = {'Left Center Forward': 'LCF','Right Back': 'RB','Right Center Midfield': 'RCM',
                      'Right Wing': 'RW','Right Center Forward': 'RCF','Right Midfield': 'RM',
                      'Center Back': 'CB','Left Center Back': 'LCB','Secondary Striker': 'SS',
                      'Right Center Back': 'RCB','Center Forward': 'CF','Left Wing': 'LW',
                      'Left Center Midfield': 'LCM','Center Midfield': 'CM','Left Midfield': 'LM',
                      'Left Back': 'LB','Goalkeeper': 'GK'}
    df_avlocations['position_abrv'] = df_avlocations.position.map(formation_dict)
    #plot all nodes
    for index, row in df_avlocations.iterrows():
        pitch.annotate(row.position_abrv, xy=(row.x, row.y), c='white', va='center',
                       ha='center', size=16, weight='bold', ax=ax)

    return



events = sb.events(match_id=7298)

team1 = 'Manchester City WFC'
team2 = 'Chelsea FCW'
firstsub_web_network(team1,team2,events)

