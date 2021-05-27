import re
import os
from pathlib import Path

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).parent.parent

#######################
### helper function ###
#######################

def format_timestamp(s):
    if re.compile('\(\d{2}:\d{2}:\d{2}\)').match(s):
        return pd.to_datetime(s, format='(%H:%M:%S)')
    elif re.compile('\(\d{2}:\d{2}\)').match(s):
        return pd.to_datetime(s, format='(%M:%S)', errors='coerce')
    elif re.compile('\d{4}-\d{2}-\d{2}').match(s):
        return pd.to_datetime(s, format='%Y-%m-%d')
    else:
        return np.datetime64('NaT')


#################
### euroleaks ###
#################

leaks_short = {1: [
            'feb24eurogroup',
            'mar17ewg',
            'apr1ewg',
            'apr24eurogroup',
            'may11eurogroup',
            'jun18eurogroup',
            'jun22eurogroup',
            'jun24eurogroup',
            'jun25eurogroup-part1',
            'jun27eurogroup',
            'jun30eurogroup'
            ],
         2: ['jul1eurogroup'],
         3: ['jun25eurogroup-part-2']
        }

dfs = []

speaker_regex = '^([\w*\[\]] *)*'

for group, leaks_ in leaks_short.items():

    for leak in leaks_:

        with open(f'data/euroleaks/html/{leak}.html', 'r') as page:

            content = page.read()
            soup = BeautifulSoup(content, 'html.parser')

            date = soup.find(class_='post-date').find(class_='meta-text').text.strip()

            col_speaker = []
            col_speech = []
            col_timestamp = []

            if group == 1:

                interventions = soup.find(id='transcript_without_translation').find_all(class_='intervention')

                for intervention in interventions:
                    # get speaker name
                    col_speaker.append(re.search(speaker_regex, intervention.find(class_='speaker-name').text).group())
                    # get speech
                    col_speech.append(intervention.find(class_='speech').text)
                    # get timestamp
                    timestamp_ = intervention.find(class_='timestamp')
                    col_timestamp.append(format_timestamp(timestamp_.text) if timestamp_ else np.datetime64('NaT'))

            elif group == 2:

                paragraphs = soup.find(id='transcript_without_translation').find_all('p')

                last_speaker = np.nan

                for p in paragraphs:

                    have_speaker = False
                    speech = ''

                    timestamp_ = p.find(class_='timestamp')

                    for line in p.text.split('\n'):
                        if line.endswith(':'):
                            if have_speaker:
                                col_speaker.append(last_speaker)
                                col_speech.append(speech.strip())
                                col_timestamp.append(format_timestamp(timestamp_.text) if timestamp_ else np.datetime64('NaT'))
                            else:
                                have_speaker = not have_speaker

                            last_speaker = re.search(speaker_regex, line).group()
                            speech = ''
                        else:
                            speech = '\n'.join((speech, line.strip()))

                    col_speaker.append(last_speaker)
                    col_speech.append(speech.strip())
                    col_timestamp.append(format_timestamp(timestamp_.text) if timestamp_ else np.datetime64('NaT'))

            elif group == 3:

                paragraphs = soup.find(id='transcript_without_translation').find_all('p')

                last_speaker = np.nan
                timestamp = np.datetime64('NaT')

                for p in paragraphs:

                    if p.text.endswith(':'):
                        last_speaker = re.search(speaker_regex, p.text).group()
                        timestamp = re.search('\(\d{2}:\d{2}\)', p.text).group() if re.search('\(\d{2}:\d{2}\)', p.text) else np.nan

                    else:
                        col_speaker.append(last_speaker)
                        col_speech.append(p.text)
                        if not pd.isnull(timestamp):
                            col_timestamp.append(format_timestamp(timestamp))
                            timestamp = np.datetime64('NaT')
                        else:
                            col_timestamp.append(np.datetime64('NaT'))


            dfs.append(pd.DataFrame({
                'speaker': col_speaker,
                'speech': col_speech,
                'timestamp': col_timestamp,
                'date': pd.to_datetime(np.repeat(date, len(col_timestamp)))
                }))


leaks_df = pd.concat(dfs, ignore_index=True)

leaks_df.to_csv(PROJECT_ROOT / 'data/euroleaks/parsed.csv', index=False)


###################
### communiques ###
###################

col_dates = []
col_titles = []
col_stories = []

for filename in os.listdir(str(PROJECT_ROOT / 'data/communiques/html')):

    date = pd.to_datetime('-'.join(filename.split('-')[:-1]), format='%Y-%m-%d')

    with open(str(PROJECT_ROOT / f'data/communiques/html/{filename}'), 'r') as page:

        content = page.read()
        soup = BeautifulSoup(content, 'html.parser')

        title = soup.find(re.compile('^h1$')).text.replace('\\r\\n', '').strip()

        story = ''

        for p in soup.find(id='main-content').find_all('p')[:-3]:
            text = p.text.replace('\\n', ' ').replace('\\xc2', '').replace('\\xa0', '').strip()
            story = text if not story else '\n'.join((story, text))

        col_dates.append(date)
        col_titles.append(title)
        col_stories.append(story)


df = pd.DataFrame({
    'date': col_dates,
    'title': col_titles,
    'story': col_stories
})

df.to_csv(PROJECT_ROOT / 'data/communiques/parsed.csv', index=False)
