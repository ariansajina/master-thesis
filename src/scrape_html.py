import urllib.request
from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).parent.parent

for name in ['euroleaks', 'communiques']:
    (PROJECT_ROOT / f'data/{name}/html').mkdir(parents=True, exist_ok=True)


#################
### euroleaks ###
#################

# each group has a different html structure
leaks_short = {1: [
            'feb24eurogroup/',
            'mar17ewg/',
            'apr1ewg/',
            'apr24eurogroup/',
            'may11eurogroup/',
            'jun18eurogroup/',
            'jun22eurogroup/',
            'jun24eurogroup/',
            'jun25eurogroup-part1/',
            'jun27eurogroup/',
            'jun30eurogroup/'
            ],
         2: ['jul1eurogroup/'],
         3: ['jun25eurogroup-part-2/']
        }

leaks = {
    group: [{
        'url': f'https://euroleaks.diem25.org/leaks/{leak}',
        'short': leak[:-1]}
        for leak in urls_] for group, urls_ in leaks_short.items()
}

for leaks_ in leaks.values():
    for leak in leaks_:
        urllib.request.urlretrieve(leak['url'],
                PROJECT_ROOT / f'data/euroleaks/html/{leak["short"]}.html')


###################
### communiques ###
###################

communiques = [
    'https://www.consilium.europa.eu/en/press/press-releases/2015/02/12/dijsselbloem-remarks/',
    'https://www.consilium.europa.eu/en/press/press-releases/2015/02/16/eurogroup-remarks/',
    'https://www.consilium.europa.eu/en/press/press-releases/2015/02/20/eurogroup-statement-greece/',
    'https://www.consilium.europa.eu/en/press/press-releases/2015/02/20/eurogroup-press-remarks/',
    'https://www.consilium.europa.eu/en/press/press-releases/2015/02/24/eurogroup-statement-greece/',
    'https://www.consilium.europa.eu/en/press/press-releases/2015/04/24/eurogroup-dijsselbloem-remarks/',
    'https://www.consilium.europa.eu/en/press/press-releases/2015/05/11/eurogroup-statement-greece/',
    'https://www.consilium.europa.eu/en/press/press-releases/2015/05/11/eurogroup-jd-remarks/',
    'https://www.consilium.europa.eu/en/press/press-releases/2015/06/18/press-remarks-eurogroup-president/',
    'https://www.consilium.europa.eu/en/press/press-releases/2015/06/22/eurogroup-press-remarks/',
    'https://www.consilium.europa.eu/en/press/press-releases/2015/06/24/eurogroup-exit-doorstep/',
    'https://www.consilium.europa.eu/en/press/press-releases/2015/06/25/eurogroup-exit-doorstep/',
    'https://www.consilium.europa.eu/en/press/press-releases/2015/06/27/eurogroup-statement-greece/',
    'https://www.consilium.europa.eu/en/press/press-releases/2015/06/27/eurogroup-intermediary-press-remarks/',
    'https://www.consilium.europa.eu/en/press/press-releases/2015/06/27/ministerial-statement/',
    'https://www.consilium.europa.eu/en/press/press-releases/2015/06/27/eurogroup-press-remarks-final/',
    'https://www.consilium.europa.eu/en/press/press-releases/2015/07/01/remarks-eurogroup-jd/',
    'https://www.consilium.europa.eu/en/press/press-releases/2015/07/05/statement-eurogroup-president-following-referendum-greece/'
]

# the following header modification is necessary because www.consilium.europa.eu blocks requests from urllib.request
for i, url in enumerate(communiques, start=1):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    page = str(urllib.request.urlopen(req).read())
    date = re.compile('(\d{4}\/\d{2}\/\d{2})').search(url).group().replace('/','-')
    with open(PROJECT_ROOT / f'data/communiques/html/{date}-{i}.html', 'w') as f:
        f.write(page)

