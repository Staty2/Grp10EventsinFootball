# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 10:04:54 2023

@author: hanwe
"""
from kloppy import statsbomb
import matplotlib as mpl
from mplsoccer.pitch import Pitch
import matplotlib.pyplot as plt
import pandas as pd

dataset = statsbomb.load_open_data(match_id=9880,coordinates='statsbomb',event_types=['pass', 'shot','substitution'])
# set the match we are analysing
pass_data = dataset.filter('pass')
# looking at the measurement of the field.
print(dataset.metadata.pitch_dimensions)
# the attackers are attacking from the field's left.
print(dataset.metadata.orientation)
# print the coordinate system.
print(dataset.metadata.coordinate_system)
# take the two teams out of the dataset
(team1, team2) = dataset.metadata.teams
print(team1.name, team2.name)

plt.rcParams['axes.unicode_minus'] = False # make the "-" normally showed

# Firstly, look at the stat of this team's pass data.
# Lionel Andrés Messi Cuccittini(in this match)
# Use the full name.
player_name = 'Lionel Andrés Messi Cuccittini'

# paint the field
pitch = Pitch()
fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0)

# filter the other players and 
# filter the foul balls

df_pass = pass_data.filter(
    lambda e: e.player.name==player_name and e.raw_event['play_pattern']!='From Throw In'
).to_df()   # transfer to pandas DataFrame

# paint arrows from the starting coordinates and ending coordinates
pitch.arrows(
    df_pass.coordinates_x, df_pass.coordinates_y,
    df_pass.end_coordinates_x, df_pass.end_coordinates_y, 
    color = "blue", ax=ax['pitch']
)
# paint circles as players
pitch.scatter(
    df_pass.coordinates_x,
    df_pass.coordinates_y,
    alpha = 0.2, s = 500, color = "blue", ax=ax['pitch']
)
fig.suptitle('passes of %s against %s'%(player_name, team2.name), fontsize = 30)
plt.show()
plt.savefig('passplot1.png', dpi=150)

# Then, paint all players


team_pass_df = pass_data.filter(
    # fliter passes with teams' names.
    lambda e: e.team.name==team1.name and e.raw_event['play_pattern']!='From Throw In'
).to_df(
    # transfer to pandas df
    '*coordinates*',
    lambda e: {'player_name': e.player.name}
)

# group the DataFrame by players
dfs = dict(tuple(team_pass_df.groupby('player_name')))

pitch = Pitch(line_color='black', pad_top=20)
fig, axs = pitch.grid(
    ncols = 4, nrows = 4, grid_height=0.85, title_height=0.06, axis=False,
    endnote_height=0.04, title_space=0.04, endnote_space=0.01
)
for name, ax in zip(dfs.keys(), axs['pitch'].flat[:len(dfs.keys())]):
    # paint the names
    ax.text(
        60, -10, name,
        ha='center', va='center', fontsize=10
    )
    # take the players' ball passing data out of the dataset.
    player_df = dfs[name]
    pitch.scatter(
        player_df.coordinates_x, 
        player_df.coordinates_y, 
        alpha = 0.2, s = 50, color = "blue", ax=ax
    )
    pitch.arrows(
        player_df.coordinates_x,
        player_df.coordinates_y,
        player_df.end_coordinates_x,
        player_df.end_coordinates_y,
        color = "blue", ax=ax, width=1
    )
# remove the blank fields
for ax in axs['pitch'][-1, 16 - len(dfs.keys()):]:
    ax.remove()

axs['title'].text(
    0.5, 0.5, 'passes of %s against %s'%(team1.name, team2.name), 
    ha='center', va='center', fontsize=30
)
plt.show()
plt.savefig('passplot2.png', dpi=150)


# give the network
# we only analyse the datas before substitution.
subst = dataset.find('substitution')

# 'pass.complete'means we only want the successful passes.
# we only need one team's data
df = dataset.filter('pass.complete').filter(
    # index shows the order of the events
    # we fliter the pass events before the substitution's index
    lambda e: e.raw_event['index'] < subst.raw_event['index'] and e.team.name == team1.name
).to_pandas(
    # transfer
    additional_columns={
        'player_name': lambda event: str(event.player),
        'receiver_name': lambda event: str(event.receiver_player)
    }
)


# filter the columns
df = df[['player_name', 'receiver_name', 
    'coordinates_x', 'coordinates_y',
    'end_coordinates_x', 'end_coordinates_y'
]]

# calculate the average position of players

outgoing_x = df.groupby(['player_name'])[['coordinates_x']].agg(['sum', 'count'])
outgoing_x.columns = outgoing_x.columns.droplevel(0)
outgoing_y = df.groupby(['player_name'])[['coordinates_y']].agg(['sum', 'count'])
outgoing_y.columns = outgoing_y.columns.droplevel(0)
incoming_x = df.groupby(['receiver_name'])[['end_coordinates_x']].agg(['sum', 'count'])
incoming_x.columns = incoming_x.columns.droplevel(0)
incoming_y = df.groupby(['receiver_name'])[['end_coordinates_y']].agg(['sum', 'count'])
incoming_y.columns = incoming_y.columns.droplevel(0)
pos_x = outgoing_x + incoming_x
pos_y = outgoing_y + incoming_y

pos = pd.DataFrame(pos_x.index).set_index('player_name')

pos['x'] = pos_x['sum']/pos_x['count']
pos['y'] = pos_y['sum']/pos_y['count']

# set the maximum
max_count = outgoing_x['count'].max()

# calculater the number of passes
passes_count = df.groupby(['player_name', 'receiver_name']).agg(['count'])
# delete the mutilevels columns
passes_count.columns = passes_count.columns.droplevel(0)
# delete the repeat columns
passes_count = passes_count.loc[:,~passes_count.columns.duplicated()].copy().reset_index()



pitch = Pitch()
fig, ax = pitch.draw(figsize=(10, 7))

# paint the players
pitch.scatter(
    pos['x'], pos['y'],
    s=pos_x['count']/max_count*300,
    edgecolors='grey', linewidth=1, alpha=1,
    ax=ax, zorder = 3
)

# mark the name
for _, row in pos.iterrows():
    pitch.annotate(
        row.name.split()[-1],
        xy=(row.x, row.y),
        c='black', va='center', ha='center',
        weight = "bold", size=16, ax=ax, zorder = 4
    )

# paint the edges
for _, row in passes_count.iterrows():
    pitch.lines(
        pos.loc[row['player_name']].x,
        pos.loc[row['player_name']].y,
        pos.loc[row['receiver_name']].x,
        pos.loc[row['receiver_name']].y,
        alpha=1, zorder=2, color="red", ax = ax,
        lw=row['count']/passes_count['count'].max()*10
    )

fig.suptitle('ball passing network of %s against %s'%(team1.name, team2.name), fontsize = 24)
plt.savefig('passnetwork.png', dpi=600)
