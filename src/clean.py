import re
import os
from pathlib import Path
import json

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).parent.parent

#################
### euroleaks ###
#################

# read data
df = pd.read_csv(PROJECT_ROOT / 'data/euroleaks/parsed.csv')


# clean speaker

# strip and make lowercase
df.speaker = df.speaker.apply(lambda s: s.strip().lower() if not pd.isnull(s) else s)

# handle missing (only one)
df.speaker.loc[df.speaker.isnull()] = 'jeroen dijsselbloem'

# drop transcription artifact speaker
df = df[df.speaker != 'group']
df = df[df.speaker != 'inaudible']

# drop varoufakis remarks made to aides at his side, not addressed to the Eurogroup
df = df[df.speaker != 'yanis varoufakis [privately]']

# make names unique
with open(PROJECT_ROOT / 'data/euroleaks/amend_names.json', 'r') as f:
    amend_names = json.load(f)

# invert dict
amend_names_inv = {value: key for key,values in amend_names.items() for value in values}

# amend speaker names
df.speaker = df.speaker.apply(lambda s: amend_names_inv[s] if s in amend_names_inv.keys() else s)

# speaker identification based on context and listening
df.speaker[np.logical_and(df.speaker == 'speaker 1', df.date=='2015-05-11 00:00:00')] = 'pierre moscovici'
df.speaker[np.logical_and(df.speaker == 'speaker 2', df.date=='2015-05-11 00:00:00')] = 'benoît cœuré'

# drop comuter generated speech
df = df[df.speech.apply(lambda s: s.strip().lower() if not pd.isnull(s) else s) != 'has entered the conference.']

# remove paranthesis and brackets

def remove_brackets(sentence):
    brackets_ = re.compile('\[.*\]')
    return re.sub(brackets_, '', sentence)

def remove_paranthesis(sentence):
    paranthesis_ = re.compile('\(.*\)')
    return re.sub(paranthesis_, '', sentence)

df.speech = df.speech.apply(lambda s: remove_brackets(remove_paranthesis(s)))


# make spelling of aide memoire consistent
def aide_memoire(s):
    """Replaces all of:
        'aid memoire'
        'aide memoir'
        'aide memoire'
        'aide -memoire'
        'aide-memoir'
        'aide-memoire'
    with 'aide memoire'.
    """
    pattern = re.compile('([Aa]ide{0,1} {0,1}( |-)[Mm]emoire{0,1})')
    return re.sub(pattern, 'aide memoire', s)

df.speech = df.speech.apply(lambda s: aide_memoire(s))

# make spelling of program/programme consistent
df.speech = df.speech.apply(lambda s: s.replace('programme', 'program'))
df.speech = df.speech.apply(lambda s: s.replace('Programme', 'Program'))

# make spelling of labor consistent
df.speech = df.speech.apply(lambda s: s.replace('labour', 'labor'))
df.speech = df.speech.apply(lambda s: s.replace('Labour', 'Labor'))

# make usage of 20th february consistent
pattern = re.compile('20(th)?,? ?(uh)?,? ?(of)?,? ?(uh)?,? ?[Ff]ebruary|[Ff]ebruary ?(the)? ?20t?h?[^\d,. ]')
df.speech = df.speech.apply(lambda s: re.sub(pattern, '20th_february', s))


# write to csv

# drop missing speech
df = df[df.speech != '']

df.to_csv(PROJECT_ROOT / 'data/euroleaks/cleaned.csv', index=False)


###################
### communiques ###
###################

df = pd.read_csv(PROJECT_ROOT / 'data/communiques/parsed.csv')\
        .sort_values(by='date').reset_index(drop=True)

# remove escaped characters
df.story = df.story.apply(lambda s:\
    s.replace('\\xc2', '').replace('\\xa0', '').replace('\n', ' ').replace('\\',''))

# replace programme with program
df.story = df.story.apply(lambda s: s.replace('programme', 'program'))
df.story = df.story.apply(lambda s: s.replace('Programme', 'Program'))

# make spelling of labor consistent
df.story = df.story.apply(lambda s: s.replace('labour', 'labor'))
df.story = df.story.apply(lambda s: s.replace('Labour', 'Labor'))

# 20th_february
pattern = re.compile('20(th)?,? ?(uh)?,? ?(of)?,? ?(uh)?,? ?[Ff]ebruary|[Ff]ebruary ?(the)? ?20t?h?[^\d,. ]')
df.story = df.story.apply(lambda s: re.sub(pattern, '20th_february', s))


# write to csv
df.to_csv(PROJECT_ROOT / 'data/communiques/cleaned.csv', index=False)

