# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 14:16:32 2023

@author: joshu
"""

from statsbombpy import sb
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import gaussian_filter
from mplsoccer import Pitch, VerticalPitch, FontManager, Sbopen

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

a = findingallmatches('Arsenal WFC', 'Chelsea FCW', FAWSL)
print(a)


#events = sb.events(match_id=19736)
#print(events)
#print(df.columns)

# get data
parser = Sbopen()
match_files = [19736, 19785, 2275063, 2275090, 3775548, 3775627]
df = pd.concat([parser.event(file)[0] for file in match_files])  # 0 index is the event file

# filter chelsea pressure and pass events
mask_arsenal_pass = (df.team_name == 'Arsenal WFC') & (df.type_name == 'Pass')
df_pass = df.loc[mask_arsenal_pass, ['x', 'y', 'end_x', 'end_y']]
mask_arsenal_carry = (df.team_name == 'Arsenal WFC') & (df.type_name == 'Carry')
df_carry = df.loc[mask_arsenal_carry, ['x', 'y']]
mask_arsenal_shot = (df.team_name == 'Arsenal WFC') & (df.type_name == 'Shot')
df_shot = df.loc[mask_arsenal_shot, ['x', 'y']]
mask_arsenal_dribble = (df.team_name == 'Arsenal WFC') & (df.type_name == 'Dribble')
df_dribble = df.loc[mask_arsenal_dribble, ['x', 'y']]

# setup pitch
pitch = Pitch(pitch_type='statsbomb', line_zorder=2,
              pitch_color='#22312b', line_color='#efefef')

# fontmanager for google font (robotto)
robotto_regular = FontManager()

# path effects
path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'),
            path_effects.Normal()]

# see the custom colormaps example for more ideas on setting colormaps
pearl_earring_cmap = LinearSegmentedColormap.from_list("Pearl Earring - 10 colors",
                                                       ['#15242e', '#4393c4'], N=10)

fig, axs = pitch.grid(endnote_height=0.03, endnote_space=0,
                      # leave some space for the colorbar
                      grid_width=0.88, left=0.025,
                      title_height=0.06, title_space=0,
                      # Turn off the endnote/title axis. I usually do this after
                      # I am happy with the chart layout and text placement
                      axis=False,
                      grid_height=0.86)
fig.set_facecolor('#22312b')


x_coords = pd.concat([df_pass.x, df_carry.x, df_shot.x, df_dribble.x])
y_coords = pd.concat([df_pass.y, df_carry.y, df_shot.y, df_dribble.y])
# plot heatmap
bin_statistic = pitch.bin_statistic(x_coords, y_coords, statistic='count', bins=(25, 25), normalize=True)
bin_statistic['statistic'] = gaussian_filter(bin_statistic['statistic'], 1)
pcm = pitch.heatmap(bin_statistic, ax=axs['pitch'], cmap='hot', edgecolors='#22312b')

# add cbar
ax_cbar = fig.add_axes((0.915, 0.093, 0.03, 0.786))
cbar = plt.colorbar(pcm, cax=ax_cbar)
cbar.outline.set_edgecolor('#efefef')
cbar.ax.yaxis.set_tick_params(color='#efefef')
plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='#efefef')
for label in cbar.ax.get_yticklabels():
    label.set_fontproperties(robotto_regular.prop)
    label.set_fontsize(15)

#title
ax_title = axs['title'].text(0.5, 0.5, "Offensive analysis of Arsenal WFC Women", color='white',
                             va='center', ha='center', path_effects=path_eff,
                             fontproperties=robotto_regular.prop, fontsize=30)
