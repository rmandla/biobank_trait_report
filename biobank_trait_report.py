import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pylatex as pl
from pylatex.utils import italic, NoEscape
import os
import subprocess
import argparse
sns.set_context('notebook',font_scale=2)

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--data", required=True,
   help="table for input")
ap.add_argument("-n", "--measurement_name", required=True,
   help="name of trait (for report generation)")
ap.add_argument("-vn","--value_name", required=True,
   help="name of the column containing values for trait of interest")
ap.add_argument("-vd","--value_descriptor",required=True,
   help="description of the trait of interest and how it is pulled")
ap.add_argument("-s","--sex_col_name", required=True,
   help="name of the column containing reported Sex. Values should be in 'Male' or 'Female'")
ap.add_argument('-b','--biobank',required=True,
   help="name of the biobank. currently can be AoU or UKBB")
ap.add_argument('-pid','--participant_id',required=False,
   help="name of the column with participant_ids. DEFAULT to person_id")
ap.add_argument('-dt','--descriptor_table',required=True,
   help="name of the file containing descriptor IDs for stratification and a summary of each ID")
ap.add_argument('-sep','--separator',required=False,
   help='character to use a delimiter when reading in tables')
ap.add_argument('-o','--output',required=True,
   help='output name of the pdf report')

args = vars(ap.parse_args())

def check_arguments():
    if args['separator'] == None or args['separator'] == np.nan:
        sep='\t'
    else:
        sep=args['separator']
    try:
        data = pd.read_table(args['data'],sep=sep)
    except:
        raise('ERROR, --data input is not formatted properly and cannot be read in by pandas')
    try:
        data_desc = pd.read_table(args['descriptor_table'],sep=sep)
    except:
        raise('ERROR, --descriptor_table is not formatted properly and cannot be read in by pandas')

    for i in ['value_name','sex_col_name','participant_id']:
        if i == 'participant_id':
            if args['participant_id'] == None or args['participant_id'] == np.nan:
                args['participant_id'] = 'person_id'
        if args[i] not in list(data.columns):
            raise('ERROR, column ' + i + ' cannot be found in --data')

    for i in data_desc.columns:
        if i not in list(data.columns):
            raise('ERROR, columns ' + i + ' cannot be found in --data')

    if args['biobank'] != 'AoU' and args['biobank'] != 'UKBB':
        raise('ERROR, biobank '+ args['biobank'] + ' is not currently supported')

    return(data,data_desc)

def create_overall_hist(data,value_name,measurement_name,biobank):
    sns.kdeplot(data[value_name],fill=True,linewidth=0)
    plt.title('all '+measurement_name+' measurements in '+biobank)
    plt.ticklabel_format(style='plain', axis='y')
    plt.savefig(measurement_name+'_distplot.png',bbox_inches='tight')

def create_overall_table(data,value_name,measurement_name,sex_col_name):
    matrix = {'sex':[],'count':[],'mean':[],'median':[],'std':[],'min':[],'max':[]}
    for sex in ['Male','Female','ALL']:
        if sex != 'ALL':
            df = data[data[sex_col_name]==sex]
        else:
            df = data.copy()
        count = len(df)
        mean = df[value_name].mean()
        median = df[value_name].median()
        sd = df[value_name].std()
        maxv = df[value_name].max()
        minv = df[value_name].min()
        matrix['count'].append(count)
        matrix['mean'].append(np.round(mean,2))
        matrix['median'].append(np.round(median,2))
        matrix['std'].append(np.round(sd,2))
        matrix['max'].append(np.round(maxv,2))
        matrix['min'].append(np.round(minv,2))
        matrix['sex'].append(sex)
    pd.DataFrame(matrix).to_csv(measurement_name+'_table.tsv',sep='\t',index=None)

def create_strat_tables(data,value_name,descriptors,sex_col_name,measurement_name,biobank,participant_id):
    for j in descriptors:
        matrix = {'strata':[],'sex':[],'count':[],'mean':[],'median':[],'std':[],'min':[],'max':[]}
        data[j] = data[j].astype(str)
        for i in data[j].unique():
            for sex in ['Male','Female','ALL']:
                if sex != 'ALL':
                    df = data[data[sex_col_name]==sex]
                else:
                    df = data.copy()
                df = df[df[j]==i]
                count = len(df)
                mean = np.round(df[value_name].mean(),2)
                median = np.round(df[value_name].median(),2)
                sd = np.round(df[value_name].std(),2)
                maxv = np.round(df[value_name].max(),2)
                minv = np.round(df[value_name].min(),2)

                if biobank=='AoU':
                    if len(df[participant_id].unique())<20:
                        count = 'Nobs <20'
                        mean = np.nan
                        median = np.nan
                        sd = np.nan
                        maxv = np.nan
                        minv = np.nan
                matrix['mean'].append(mean)
                matrix['median'].append(median)
                matrix['std'].append(sd)
                matrix['max'].append(maxv)
                matrix['min'].append(minv)
                matrix['count'].append(count)
                matrix['strata'].append(i)
                matrix['sex'].append(sex)

            nobs = len(data[data[j]==i])
            n = len(data[data[j]==i][participant_id].unique())
            i_name = i
            if len(i)>20:
                ilist = [i[x:x+20] for x in range(0, len(i), 20)]
                i_name = '-\n'.join(ilist)
            name = i_name + '\nN_obs='+str(nobs)+'\nN='+str(n)
            data[j][data[j]==i] = name
        pd.DataFrame(matrix).to_csv(measurement_name+'_'+j+'_table.tsv',sep='\t',index=None)
    return(data)

def create_strat_hist(data,value_name,descriptors,measurement_name,sex_col_name,biobank,participant_id):
    data = create_strat_tables(data,value_name,descriptors,sex_col_name,measurement_name,biobank,participant_id)
    for j in descriptors:
        df = data.copy()
        df['N'] = np.nan
        for strata in data[j].unique():
            df['N'][data[j]==strata]=len(data[data[j]==strata][participant_id].unique())
        df = df.sort_values('N',ascending=False)

        g = sns.displot(data=df,x=value_name, col=j, kind="kde",
                col_wrap=6,facet_kws={'sharex':False,'sharey':False,},fill=True,linewidth=0,bw_adjust=1)
        g.set_titles("{col_name}")
        plt.savefig(measurement_name+'_'+j+'_distplot.png')

def generate_latex(measurement_name,value_descriptor,descriptor_table,biobank,participant_id):
    descriptors = descriptor_table.columns
    create_strat_hist(data,value_name,descriptors,measurement_name,sex_col_name,biobank,participant_id)
    full_plot = measurement_name+'_distplot.png'
    full_table = measurement_name+'_table.tsv'

    geometry_options = {"tmargin": "1cm", "lmargin": "1cm", "rmargin": "1cm"}
    doc = pl.Document(geometry_options=geometry_options, lmodern = False)
    doc.packages.append(pl.Package('longtable'))
    doc.packages.append(pl.Package('booktabs'))

    with doc.create(pl.Section(measurement_name)):
        doc.append(value_descriptor)
        doc.append('\n')
        with doc.create(pl.Figure(position='h!')) as figure:
            figure.add_image(full_plot, width='3.5in')
            figure.add_caption('Distribution of all recorded values for all participants')

        df = pd.read_table(full_table)
        doc.append(pl.NoEscape(df.to_latex(escape=False,index=None,longtable=True,caption='Table of all recorded '+measurement_name+' values').replace('%','\%')))
        doc.append(pl.NewPage())

        for descriptor in descriptors:
            with doc.create(pl.Subsection(descriptor)):
                doc.append(descriptor_table[descriptor].to_list()[0])
                with doc.create(pl.Figure(position='h!')) as figure:
                    figure.add_image(full_plot.replace('_distplot','_'+str(descriptor)+'_distplot'),width='7in')
                    figure.add_caption('Distribution of recorded '+measurement_name+' values for all participants stratified by '+descriptor)
                df = pd.read_table(full_table.replace('_table','_'+str(descriptor)+'_table'))
                doc.append(pl.NoEscape(df.to_latex(escape=False,index=None,longtable=True,caption='Table of recorded '+measurement_name+' values for participants stratified by '+descriptor).replace('%','\%')))
            if descriptor != list(descriptors)[-1]:
                doc.append(pl.NewPage())

    doc.generate_tex('test_output')

def clean_latex(output):
    with open(output.replace('.pdf','.tex'),'w') as out:
        with open('test_output.tex','rt') as inpu:
            for i in inpu:
                if 'lastpage' not in i:
                    out.write(i)

def generate_pdf(output):
    tex_file = output.replace('.pdf','.tex')
    subprocess.run('pdflatex  -interaction=nonstopmode '+tex_file,shell=True)

data,descriptor_table = check_arguments()
print('data read in successfully')
value_name = args['value_name']
measurement_name = args['measurement_name']
biobank = args['biobank']
sex_col_name = args['sex_col_name']
value_descriptor = args['value_descriptor']
output = args['output']
participant_id = args['participant_id']

create_overall_hist(data,value_name,measurement_name,biobank)
create_overall_table(data,value_name,measurement_name,sex_col_name)
generate_latex(measurement_name,value_descriptor,descriptor_table,biobank,participant_id)
clean_latex(output)
generate_pdf(output)
