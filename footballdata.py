#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 14:34:20 2023

@author: felix
"""
import json
import pandas as pd

# Open the JSON file and load its contents
with open('7298.json') as f:
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
                'pass.body_part.id', 'pass.body_part.name', 'pass.type.id', 'pass.type.name', 'carry.end_location', 
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

#indexs: when using iloc need to add 1 to the last index so passing would be 24-35
# pass: 24-34
# carry: 35-35
# ball_receipt: 36-37
# substitution: 38-41
# bad_behaviour: 42-43
# tactics: 44-44
# duel: 45-47
# interception: 48-49
# shot: 50-64
# goalkeeper: 65-72
# dribble: 73-76


#without IDs:
# column_order = ['id', 'index', 'period', 'type.name', 'timestamp', 'minute', 'second', 'possession', 'possession_team.name',
#                 'play_pattern.name', 'team.name', 'player.name', 'position.name', 'location', 'duration', 'under_pressure', 
#                 'counterpress', 'related_events', 'pass.recipient.name', 'pass.length','pass.angle', 'pass.height.name',
#                 'pass.end_location', 'pass.body_part.name', 'pass.type.name', 'carry.end_location', 'ball_receipt.outcome.name', 
#                 'substitution.outcome.name', 'substitution.replacement.name', 'bad_behaviour.card.name', 'tactics.formation', 
#                 'duel.type.name', 'duel.outcome.name', 'interception.outcome.name', 'shot.statsbomb_xg', 'shot.end_location', 
#                 'shot.key_pass_id', 'shot.outcome.name', 'shot.body_part.name', 'shot.technique.name', 'shot.type.name', 
#                 'shot.freeze_frame.location', 'shot.freeze_frame.player.name', 'shot.freeze_frame.position.name', 
#                 'shot.freeze_frame.teammate', 'goalkeeper.technique.name', 'goalkeeper.body_part.name', 'goalkeeper.position.name', 
#                 'goalkeeper.type.name', 'goalkeeper.outcome.name', 'dribble.outcome.name', 'dribble.overrun', 'dribble.nutmeg', 
#                 'ball_receipt.outcome.name']


# Reorder the columns
df = df.reindex(columns=column_order)

# This will print the first 5 time stamps and the corresponding coloums so the first will be columns 1 to 4.
print(df.iloc[:5, 1:5])
print(df.iloc[:5, 5:9])
print(df.iloc[:5, 9:11])
print(df.iloc[:5, 11:13])
print(df.iloc[:5, 13:15])
print(df.iloc[:5, 24:35])

# To see each unique event:
# events = df['type.name'].tolist()
# events = set(events)
# print(events)
# print(len(events))
