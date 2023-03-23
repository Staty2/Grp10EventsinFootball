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
import matplotlib.patheffects as path_effects
from mplsoccer import Pitch, FontManager
pitch = Pitch()

#Combining all 3 seasons into one dataframe
matches2021 = sb.matches(competition_id=37, season_id = 90) #a specific season of the womens FA Super League, also use season ID 90 (20-21), 42 (19-20),4(18-19)
matches1920 = sb.matches(competition_id=37, season_id = 42)
matches1819 = sb.matches(competition_id=37, season_id = 4)
frames = [matches1819, matches1920, matches2021]
FAWSL = pd.concat(frames)


def findingallmatches(team1, team2, all_matches):
    '''
    findingallmatches('Manchester City WFC','Chelsea FCW', FAWSL)
    '''
    match_ids = []        
    for index, row in all_matches.iterrows():
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

def findingallnames(all_matches):
    '''
    findingallnames(FAWSL)
    '''
    # Extract the unique team names from the home and away team columns
    home_teams = set(all_matches['home_team'])
    away_teams = set(all_matches['away_team'])
    
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




def Xthreat_which(which,team1,team2,all_matches):
    '''
    matches1819 = sb.matches(competition_id=37, season_id = 4)
    team1 = 'Manchester City WFC'
    team2 = 'Chelsea FCW'
    Xthreat_which('shot',team1,team2,matches1819)
    '''
    bins = (16, 12)
    #find all matches
    match_ids = findingallmatches(team1, team2, all_matches)
    print(f'number of matches = {len(match_ids)}')
    
    # next we create a dataframe of all the events
    all_events_df = []
    
    cols = ['match_id', 'id', 'type', 'player','location','shot_outcome']
    for match in match_ids:
        # get carries/ passes/ shots
        event = sb.events(match_id=match)  # get the first dataframe (events) which has index = 0
        event = event.loc[event.type.isin(['Carry', 'Shot', 'Pass']), cols].copy()
    
        # boolean columns for working out probabilities
        event['goal'] = event['shot_outcome'] == 'Goal'
        event['shoot'] = event['type'] == 'Shot'
        event['move'] = event['type'] != 'Shot'
        event[['x', 'y']] = event['location'].apply(lambda x: pd.Series([x[0], x[1]]))

        all_events_df.append(event)
        
    event = pd.concat(all_events_df)
    
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc', line_zorder=2)
    
    shot_probability = pitch.bin_statistic(event['x'], event['y'], values=event['shoot'],
                                       statistic='mean', bins=bins)
    move_probability = pitch.bin_statistic(event['x'], event['y'], values=event['move'],
                                       statistic='mean', bins=bins)
    goal_probability = pitch.bin_statistic(event.loc[event['shoot'], 'x'],
                                       event.loc[event['shoot'], 'y'],
                                       event.loc[event['shoot'], 'goal'],
                                       statistic='mean', bins=bins)
    if which == 'shot':
        fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=True, tight_layout=False)
        fig.set_facecolor("#22312b")
        shot_heatmap = pitch.heatmap(shot_probability, ax=ax)
    
    elif which == 'move':
        fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=True, tight_layout=False)
        fig.set_facecolor("#22312b")
        shot_heatmap = pitch.heatmap(move_probability, ax=ax)
        
    elif which == 'goal':
        fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=True, tight_layout=False)
        fig.set_facecolor("#22312b")
        shot_heatmap = pitch.heatmap(goal_probability, ax=ax)
    
    else:
        print('please input "shot", "move", or "goal" as the which input')
    
    return



def Xthret_prob(team1,team2,all_matches):
    bins = (16, 12)
    #find all matches
    match_ids = findingallmatches(team1, team2, all_matches)
    print(f'number of matches = {len(match_ids)}')
    
    # next we create a dataframe of all the events
    all_events_df = []
    
    cols = ['match_id', 'id', 'type', 'player',
            'location', 'shot_end_location', 'pass_end_location',
            'carry_end_location', 'shot_outcome', 'shot_statsbomb_xg']
    for match in match_ids:
        # get carries/ passes/ shots
        event = sb.events(match_id=match)  # get the first dataframe (events) which has index = 0
        event = event.loc[event.type.isin(['Carry', 'Shot', 'Pass']), cols].copy()
    
        # boolean columns for working out probabilities
        event['goal'] = event['shot_outcome'] == 'Goal'
        event['shoot'] = event['type'] == 'Shot'
        event['move'] = event['type'] != 'Shot'
        event[['x', 'y']] = event['location'].apply(lambda x: pd.Series([x[0], x[1]]))
        event['carry_end_location'].loc[event['carry_end_location'].isnull()] = event['carry_end_location'].loc[event['carry_end_location'].isnull()].apply(lambda x: [0,0])
        event['shot_end_location'].loc[event['shot_end_location'].isnull()] = event['shot_end_location'].loc[event['shot_end_location'].isnull()].apply(lambda x: [0,0])
        event['pass_end_location'].loc[event['pass_end_location'].isnull()] = event['pass_end_location'].loc[event['pass_end_location'].isnull()].apply(lambda x: [0,0])
        event[['c_end_x', 'c_end_y']] = event['carry_end_location'].apply(lambda x: pd.Series([x[0], x[1]]))
        event[['s_end_x', 's_end_y']] = event['shot_end_location'].apply(lambda x: pd.Series([x[0], x[1]]))
        event[['p_end_x', 'p_end_y']] = event['pass_end_location'].apply(lambda x: pd.Series([x[0], x[1]]))
        event['end_x'] = event.apply(lambda row: row['c_end_x'] + row['s_end_x'] + row['p_end_x'], axis=1)
        event['end_y'] = event.apply(lambda row: row['c_end_y'] + row['s_end_y'] + row['p_end_y'], axis=1)

        all_events_df.append(event)
        
    event = pd.concat(all_events_df)
    
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc', line_zorder=2)
    
    shot_probability = pitch.bin_statistic(event['x'], event['y'], values=event['shoot'],
                                       statistic='mean', bins=bins)
    move_probability = pitch.bin_statistic(event['x'], event['y'], values=event['move'],
                                       statistic='mean', bins=bins)
    goal_probability = pitch.bin_statistic(event.loc[event['shoot'], 'x'],
                                       event.loc[event['shoot'], 'y'],
                                       event.loc[event['shoot'], 'goal'],
                                       statistic='mean', bins=bins)
    
    # get a dataframe of move events and filter it
    # so the dataframe only contains actions inside the pitch.
    move = event[event['move']].copy()
    bin_start_locations = pitch.bin_statistic(move['x'], move['y'], bins=bins)
    move = move[bin_start_locations['inside']].copy()
    
    # get the successful moves, which filters out the events that ended outside the pitch
    # or where not successful (null)
    bin_end_locations = pitch.bin_statistic(move['end_x'], move['end_y'], bins=bins)
    move_success = move[(bin_end_locations['inside'])].copy()
    
    # get a dataframe of the successful moves
    # and the grid cells they started and ended in
    bin_success_start = pitch.bin_statistic(move_success['x'], move_success['y'], bins=bins)
    bin_success_end = pitch.bin_statistic(move_success['end_x'], move_success['end_y'], bins=bins)
    df_bin = pd.DataFrame({'x': bin_success_start['binnumber'][0],
                           'y': bin_success_start['binnumber'][1],
                           'end_x': bin_success_end['binnumber'][0],
                           'end_y': bin_success_end['binnumber'][1]})
    
    # calculate the bin counts for the successful moves, i.e. the number of moves between grid cells
    bin_counts = df_bin.value_counts().reset_index(name='bin_counts')
    
    # create the move_transition_matrix of shape (num_y_bins, num_x_bins, num_y_bins, num_x_bins)
    # this is the number of successful moves between grid cells.
    num_y, num_x = shot_probability['statistic'].shape
    move_transition_matrix = np.zeros((num_y, num_x, num_y, num_x))
    move_transition_matrix[bin_counts['y'], bin_counts['x'],
                           bin_counts['end_y'], bin_counts['end_x']] = bin_counts.bin_counts.values
    
    # and divide by the starting locations for all moves (including unsuccessful)
    # to get the probability of moving the ball successfully between grid cells
    bin_start_locations = pitch.bin_statistic(move['x'], move['y'], bins=bins)
    bin_start_locations = np.expand_dims(bin_start_locations['statistic'], (2, 3))
    move_transition_matrix = np.divide(move_transition_matrix,
                                       bin_start_locations,
                                       out=np.zeros_like(move_transition_matrix),
                                       where=bin_start_locations != 0,
                                       )
    
    move_transition_matrix = np.nan_to_num(move_transition_matrix)
    shot_probability_matrix = np.nan_to_num(shot_probability['statistic'])
    move_probability_matrix = np.nan_to_num(move_probability['statistic'])
    goal_probability_matrix = np.nan_to_num(goal_probability['statistic'])
    
    xt = np.multiply(shot_probability_matrix, goal_probability_matrix)
    diff = 1
    iteration = 0
    while np.any(diff > 0.00001):  # iterate until the differences between the old and new xT is small
        xt_copy = xt.copy()  # keep a copy for comparing the differences
        # calculate the new expected threat
        xt = (np.multiply(shot_probability_matrix, goal_probability_matrix) +
              np.multiply(move_probability_matrix,
                          np.multiply(move_transition_matrix, np.expand_dims(xt, axis=(0, 1))).sum(
                              axis=(2, 3)))
              )
        diff = (xt - xt_copy)
        iteration += 1
    print('Number of iterations:', iteration)
    
    path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'),
            path_effects.Normal()]
    # new bin statistic for plotting xt only
    for_plotting = pitch.bin_statistic(event['x'], event['y'], bins=bins)
    for_plotting['statistic'] = xt
    fig, ax = pitch.draw(figsize=(14, 9.625))
    _ = pitch.heatmap(for_plotting, ax=ax)
    _ = pitch.label_heatmap(for_plotting, ax=ax, str_format='{:.2%}',
                            color='white', fontsize=14, va='center', ha='center',
                            path_effects=path_eff)
    # sphinx_gallery_thumbnail_path = 'gallery/tutorials/images/sphx_glr_plot_xt_004'
    
    # first get grid start and end cells
    grid_start = pitch.bin_statistic(move_success.x, move_success.y, bins=bins)
    grid_end = pitch.bin_statistic(move_success.end_x, move_success.end_y, bins=bins)
    
    # then get the xT values from the start and end grid cell
    start_xt = xt[grid_start['binnumber'][1], grid_start['binnumber'][0]]
    end_xt = xt[grid_end['binnumber'][1], grid_end['binnumber'][0]]
    
    # then calculate the added xT
    added_xt = end_xt - start_xt
    move_success['xt'] = added_xt
    
    # show players with top 5 total expected threat
    top5 = move_success.groupby('player')['xt'].sum().sort_values(ascending=False).head(5)
    print(top5)
    return


team1 = 'Manchester City WFC'
team2 = 'Chelsea FCW'

