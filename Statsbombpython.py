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


a = findingallnames(FAWSL)
print(a)

