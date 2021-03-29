import re
import os
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).parent.parent

#################
### read data ###
#################

df = pd.read_csv(PROJECT_ROOT / 'data/euroleaks/parsed.csv')

# lowercase speech
df.speech = df.speech.apply(lambda s: s.lower())


#####################
### clean speaker ###
#####################

# strip and make lowercase
df.speaker = df.speaker.apply(lambda s: s.strip().lower() if not pd.isnull(s) else s)

# handle missing (only one)
df.speaker.loc[df.speaker.isnull()] = 'jeroen dijsselbloem'

# drop transcription artifact speaker
df = df[df.speaker != 'group']
df = df[df.speaker != 'inaudible']

# drop comuter generated speech
df = df[df.speech != 'Has entered the conference.']

# make names unique
amend_names = {
    'wolfgang schäuble': [
        'wolfgang schäuble',
        'wolfgang schauble',
        'wolfgang'
    ],
    'peter kažimír': [
        'peter kažimír',
        'peter kazimir'
    ],
    'michel sapin': [
        'michel sapin',
        'michel'
    ],
    'maria luís albuquerque': [
        'maria luís albuquerque',
        'maria luís',
        'maria luis albuquerque'
    ],
    'johan van overtveldt': [
        'johan van overtveldt',
        'johan'
    ],
    'benoît cœuré': [
        'benoît cœuré',
        'benoit couré',
        'benoit cœuré'
    ],
    'hans jörg schelling': [
        'hans jörg schelling',
        'hans'
    ],
    'poul mathias thomsen': [
        'paul thomsen',
        'paul',
        'poul thomsen'
    ],
    'yanis varoufakis': [
        'yanis varoufakis',
        'yanis varoufakis [privately]'
    ],
    'luis de guindos': [
        'luis de guindos',
        'luis'
    ],
    'irina': [
        'irina',
        'irana'
    ],
    'jānis reirs': [
        'yanis [not varoufakis]'
    ],
    'luca antonio ricci': [
        'ricci'
    ],
    'thomas steffen': [
        'thomas'
    ]
}

# invert dict
amend_names_inv = {value: key for key,values in amend_names.items() for value in values}

# amend speaker names
df.speaker = df.speaker.apply(lambda s: amend_names_inv[s] if s in amend_names_inv.keys() else s)


#######################################
### remove paranthesis and brackets ###
#######################################

def remove_brackets(sentence):
    brackets_ = re.compile('\[.*\]')
    return re.sub(brackets_, '', sentence)

def remove_paranthesis(sentence):
    paranthesis_ = re.compile('\(.*\)')
    return re.sub(paranthesis_, '', sentence)

df.speech = df.speech.apply(lambda s: remove_brackets(remove_paranthesis(s)))


#############################
### the aide memoire case ###
#############################

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
    pattern = re.compile('(aide{0,1} {0,1}( |-)memoire{0,1})')
    return re.sub(pattern, 'aide memoire', s)

df.speech = df.speech.apply(lambda s: aide_memoire(s))

###########################
### program / programme ###
###########################

df.speech = df.speech.apply(lambda s: s.replace('programme', 'program'))

####################
### write to csv ###
####################

# drop missing speech
df = df[df.speech != '']

df.to_csv(PROJECT_ROOT / 'data/euroleaks/cleaned.csv', index=False)

