'''Bla bla

'''
import pandas as pd
import os
import sqlite3

GP_SOURCE = '../../Desktop/a61p_canceroncology/'
DB_OUT = './a61pCancerPatentsV2.db'
HEURISTIC_FILE_SIZE = 1000000
SPECIAL_ASS = ['Inc', 'Ltd', 'Us Llc', 'Llc', 'LLC', 'L.L.C.',
               'As Represented By', 'As Represented By The Secretary',
               'Incorporated', 'United States of America',
               'Department Of ',
               'L.l.c.', 'Limited', 'Technology and Research']
SPECIAL_ASS += [x.lower() for x in SPECIAL_ASS]
SPECIAL_ASS2 = ['JR', 'SR', 'Jr', 'Sr', 'jr', 'sr']
USA = ['United States Of America','U.S.A.','U.S.A', 'United Staes Of America', 'United Of America', 'United States Government']
USA = USA + [x.lower() for x in USA] + [x.upper() for x in USA]


def extract_vals(array):
    ret = []
    for row in array:
        for val in row:
            ret.append(val.strip().lower())
    return set(ret)

def _unify_usa(x):
    for v in USA:
        x = x.replace(v, 'USA')
    return x

def _fix_comma_special_cases(x):
    if not ',' in x:
        return x
    else:
        for special_chars in SPECIAL_ASS:
            if ', {}'.format(special_chars) in x:
                x = x.replace(', {}'.format(special_chars), ' {}'.format(special_chars))
        return x

def _fix_comma_special_cases_2(x):
    if not ',' in x:
        return x
    else:
        for special_chars in SPECIAL_ASS2:
            if ', {}'.format(special_chars) in x:
                x = x.replace(', {}'.format(special_chars), ' {}'.format(special_chars))
        return x

content_files = []
concept_files = []
for file in os.listdir(GP_SOURCE):
    fp = '{}/{}'.format(GP_SOURCE, file)
    file_size = os.stat(fp).st_size
    if file_size < HEURISTIC_FILE_SIZE:
        content_files.append(fp)
    else:
        concept_files.append(fp)

#
# Create ID to name mapping tables for assigned and inventors
#
all_assignees = set([])
all_inventors = set([])
for fname in content_files:
    df = pd.read_csv(fname, skiprows=0, header=1)

    df['assignee'] = df['assignee'].apply(_fix_comma_special_cases)
    df['assignee'] = df['assignee'].apply(_unify_usa)
    assignees = df['assignee'].str.split(',')
    df['inventor/author'] = df['inventor/author'].apply(_fix_comma_special_cases_2)
    inventors = df['inventor/author'].str.split(',')
    new_assignees = extract_vals(assignees)
    new_inventors = extract_vals(inventors)
    all_assignees = all_assignees.union(new_assignees)
    all_inventors = all_inventors.union(new_inventors)

df = pd.DataFrame(list(all_assignees), columns=['name'])
df.index.name = 'assignee_id'
df.to_csv('assignees.csv')
df.to_sql('assignees', index=True, con=sqlite3.connect(DB_OUT), if_exists='append')
ass_dict = {v : k for k, v in df['name'].to_dict().items()}

df = pd.DataFrame(list(all_inventors), columns=['name'])
df.index.name = 'inventor_id'
df.to_csv('inventors.csv')
df.to_sql('inventors', index=True, con=sqlite3.connect(DB_OUT), if_exists='append')
inv_dict = {v : k for k, v in df['name'].to_dict().items()}

#
# Factor out the patent data and create the mapping between patents and inventors and assignees
#
all_patents = []
patents_inventor = []
patents_ass = []
for fname in content_files:
    df = pd.read_csv(fname, skiprows=0, header=1)
    df = df.set_index('id')
    df['assignee'] = df['assignee'].apply(_fix_comma_special_cases)
    df['assignee'] = df['assignee'].apply(_unify_usa)
    assignees = df['assignee'].str.split(',')
    df['inventor/author'] = df['inventor/author'].apply(_fix_comma_special_cases_2)
    inventors = df['inventor/author'].str.split(',')

    assignees = assignees.apply(lambda x: [ass_dict[y.strip().lower()] for y in x])
    assignees = assignees.explode().reset_index()
    patents_ass.append(assignees)
    inventors = inventors.apply(lambda x: [inv_dict[y.strip().lower()] for y in x])
    inventors = inventors.explode().reset_index()
    patents_inventor.append(inventors)

    df_patent = df[['title', 'priority date', 'filing/creation date', 'publication date', 'grant date', 'result link']]
    all_patents.append(df_patent)

df_patent = pd.concat(all_patents)
df_patent = df_patent.rename(columns={'filing/creation date' : 'filing_date',
                                      'priority date' : 'priority_date',
                                      'publication date' : 'publication_date',
                                      'grant date' : 'grant_date',
                                      'result link' : 'result_link'})
df_patent.to_csv('patents.csv')
df_patent.to_sql('patents', index=True, con=sqlite3.connect(DB_OUT), if_exists='append')

df_inventors = pd.concat(patents_inventor)
df_inventors = df_inventors.rename(columns={'inventor/author' : 'inventor_id'})
df_ass = pd.concat(patents_ass)
df_ass = df_ass.rename(columns={'assignee' : 'assignee_id'})
df_inventors.to_csv('patents_inventors.csv', index=False)
df_inventors.to_sql('patents_inventors', index=False, con=sqlite3.connect(DB_OUT), if_exists='append')
df_ass.to_csv('patents_assignees.csv', index=False)
df_ass.to_sql('patents_assignees', index=False, con=sqlite3.connect(DB_OUT), if_exists='append')

for k_file, fname in enumerate(concept_files):
    df = pd.read_csv(fname, skiprows=0, header=1)
    df = df.rename(columns={'name' : 'concept'})
    df = df.drop(columns=['query match'])
    df['concept'] = df['concept'].str.lower()

    df.to_csv('./concepts_{}.csv'.format(k_file))
    df.to_sql('patents_subjects', index=False, con=sqlite3.connect(DB_OUT), if_exists='append')