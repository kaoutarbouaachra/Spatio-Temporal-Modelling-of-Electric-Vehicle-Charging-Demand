# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 14:18:51 2024

@author: kdavi
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 11:59:37 2024

@author: kdavi
"""

import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta
from scipy.stats import ks_2samp
from datetime import datetime, time

#bringing in ChargerID and LA data
ChargerID = pd.read_excel('CPID_and_local_authority.xlsx')
#correcting erroneous entries
ChargerID.loc[ChargerID['CPID']==61625, 'local_authority'] = 'Renfrewshire'
ChargerID.loc[ChargerID['CPID']=='CMU2211', 'local_authority'] = 'North Lanarkshire'
#bringing in charging speed data
ChargerSpeeds = pd.read_excel("CPID_and_charger_speed.xlsx")


import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta
from scipy.stats import ks_2samp
from datetime import datetime, time
import os


#bringing in ChargerID and LA data
ChargerID = pd.read_excel('CPID_and_local_authority.xlsx')
#correcting erroneous entries
ChargerID.loc[ChargerID['CPID']==61625, 'local_authority'] = 'Renfrewshire'
ChargerID.loc[ChargerID['CPID']=='CMU2211', 'local_authority'] = 'North Lanarkshire'
#bringing in charging speed data
ChargerSpeeds = pd.read_excel("CPID_and_charger_speed.xlsx")

#bringing in excel charging session data from Oct22 to Mar24

# Chemin vers le dossier des fichiers bruts
chemin22 = "fichiersexceluniformises/2022"
chemin23="fichiersexceluniformises/2023"
chemin24="fichiersexceluniformises/2024"
chemin25 = "fichiersexceluniformises/2025"

# Chargement des fichiers mensuels de sessions de charge
###2022
Oct22 = pd.read_excel(os.path.join(chemin22, '10.xlsx'))
Nov22 = pd.read_excel(os.path.join(chemin22, '11.xlsx'))
Dec22 = pd.read_excel(os.path.join(chemin22, '12.xlsx'))
###2023
Jan23 = pd.read_excel(os.path.join(chemin23, '1.xlsx'))
Feb23 = pd.read_excel(os.path.join(chemin23, '2.xlsx'))
Mar23 = pd.read_excel(os.path.join(chemin23, '3.xlsx'))
Apr23 = pd.read_excel(os.path.join(chemin23, '4.xlsx'))
May23 = pd.read_excel(os.path.join(chemin23, '5.xlsx'))
Jun23 = pd.read_excel(os.path.join(chemin23, '6.xlsx'))
Jul23 = pd.read_excel(os.path.join(chemin23, '7.xlsx'))
Aug23 = pd.read_excel(os.path.join(chemin23, '8.xlsx'))
Sep23 = pd.read_excel(os.path.join(chemin23, '9.xlsx'))
Oct23 = pd.read_excel(os.path.join(chemin23, '10.xlsx'))
Nov23 = pd.read_excel(os.path.join(chemin23, '11.xlsx'))
Dec23 = pd.read_excel(os.path.join(chemin23, '12.xlsx'))
###2024
Jan24 = pd.read_excel(os.path.join(chemin24, '1.xlsx'))
Feb24 = pd.read_excel(os.path.join(chemin24, '2.xlsx'))
Mar24 = pd.read_excel(os.path.join(chemin24, '3.xlsx'))
May24 = pd.read_excel(os.path.join(chemin24, '5.xlsx'))
Jun24 = pd.read_excel(os.path.join(chemin24, '6.xlsx'))
Jul24 = pd.read_excel(os.path.join(chemin24, '7.xlsx'))
Aug24 = pd.read_excel(os.path.join(chemin24, '8.xlsx'))
Sep24 = pd.read_excel(os.path.join(chemin24, '9.xlsx'))
Oct24 = pd.read_excel(os.path.join(chemin24, '10.xlsx'))
Nov24 = pd.read_excel(os.path.join(chemin24, '11.xlsx'))
Dec24 = pd.read_excel(os.path.join(chemin24, '12.xlsx'))
Apr24 = pd.read_excel(os.path.join(chemin24, '4.xlsx'))
###2025
Jan25 = pd.read_excel(os.path.join(chemin25, '1.xlsx'))
Feb25 = pd.read_excel(os.path.join(chemin25, '2.xlsx'))
Apr25 = pd.read_excel(os.path.join(chemin25, '4.xlsx'))

#combining monthly CPS sessions data
df = pd.concat([Oct22, Nov22, Dec22, Jan23, Feb23, Mar23, Apr23, May23, Jun23, Jul23, Aug23, Sep23, Oct23, Nov23, Dec23, Jan24, Feb24, Mar24, Apr24, May24, Jun24, Jul24, Aug24, Sep24, Oct24, Nov24, Dec24,Jan25, Feb25, Apr25])

#formatting start date to yyyy-mm-dd
df['Start'] = pd.to_datetime(df['Start'], infer_datetime_format=True)
df['Start'] = df['Start'].dt.strftime('%Y-%m-%d')

#merging Charger ID with df to attach LA data based on CPID
merged_df = pd.merge(df, ChargerID, on='CPID', how='left')

#removing data where energy consumed = 0kWh
merged_df = merged_df[merged_df['Consumed(kWh)']>0]
#removing sessions where duration is 00:00:00
merged_df = merged_df[merged_df['Duration'] != pd.to_datetime('00:00:00').time()]

#removing nulls from merged_df
merged_df = merged_df.dropna()

#bringing in 8-fold rural urban classification
UR8class = pd.read_excel("CPID_and_UR_Classification.xlsx")
#correcting nulls from GIS
UR8class.loc[UR8class['CPID']==62931, 'UR8Class'] = 5
UR8class.loc[UR8class['CPID']==62932, 'UR8Class'] = 5
#merging 8-fold with session data based on CPID
merged_df = pd.merge(merged_df, UR8class, on='CPID', how='left')
#removing nulls
merged_df = merged_df.dropna()

#bringing in SIMD full rank
SIMD = pd.read_excel("CPID_and_SIMD.xlsx")
#correcting nulls from GIS
SIMD.loc[SIMD['CPID']==62931, 'Rankv2'] = 558
SIMD.loc[SIMD['CPID']==62932, 'Rankv2'] = 558
SIMD.loc[SIMD['CPID']==50540, 'Rankv2'] = 3763
SIMD.loc[SIMD['CPID']==50796, 'Rankv2'] = 3763
SIMD.loc[SIMD['CPID']==50797, 'Rankv2'] = 3763
SIMD.loc[SIMD['CPID']==51500, 'Rankv2'] = 3763
SIMD.loc[SIMD['CPID']==51961, 'Rankv2'] = 1400
SIMD.loc[SIMD['CPID']==52112, 'Rankv2'] = 1400
SIMD.loc[SIMD['CPID']=='1712508020/B94060093', 'Rankv2'] = 1400
SIMD.loc[SIMD['CPID']=='T54-1T1-1319-117', 'Rankv2'] = 1400
#merging SIMD rank data with the rest
merged_df = pd.merge(merged_df, SIMD, on='CPID', how='left')
#removing any nulls in updated main dataset
merged_df = merged_df.dropna()

#bringing in SIMD, geographical accessibility rank only
GAcc = pd.read_excel("CPID_and_GA.xlsx")
#correcting nulls from GIS
GAcc.loc[GAcc['CPID']==62931, 'GAccRank'] = 6516
GAcc.loc[GAcc['CPID']==62932, 'GAccRank'] = 6516
GAcc.loc[GAcc['CPID']==50540, 'GAccRank'] = 5336
GAcc.loc[GAcc['CPID']==50796, 'GAccRank'] = 5336
GAcc.loc[GAcc['CPID']==50797, 'GAccRank'] = 5336
GAcc.loc[GAcc['CPID']==51500, 'GAccRank'] = 5336
GAcc.loc[GAcc['CPID']==51961, 'GAccRank'] = 4652
GAcc.loc[GAcc['CPID']==52112, 'GAccRank'] = 4652
GAcc.loc[GAcc['CPID']=='1712508020/B94060093', 'GAccRank'] = 4652
GAcc.loc[GAcc['CPID']=='T54-1T1-1319-117', 'GAccRank'] = 4652
#merging SIMD GeoAccess rank data with the rest
merged_df = pd.merge(merged_df, GAcc, on='CPID', how='left')
#removing any nulls in updated main dataset
merged_df = merged_df.dropna()

#bringing in and attaching postcodes
postcodes = pd.read_excel('CPID_and_postcode.xlsx')
merged_df = pd.merge(merged_df, postcodes, on='CPID', how='left')
merged_df = merged_df.dropna()

#removing any duplicated sessions
data = merged_df.drop_duplicates()
##removing sessions where >118kWh was drawn
##These sessions are incompatible with the usable battery capacity of the EV
##with the larges usable battery capacity according to EV Database
##https://ev-database.org/uk/cheatsheet/useable-battery-capacity-electric-car
data = data[data['Consumed(kWh)']<=118]
##removing sessions where amount paid is >£1471 based on cost of 24h duration charge
##for 118kWh battery on an East Renfrewshire Council rapid charger (largest tariff
##plus overstay fee on CPS network at time of writing)
data = data[data['Amount']<=1471]

#adding charger speed data
data = pd.merge(data, ChargerSpeeds, on='CPID', how='left')
#assigning missing data
data.loc[data['CPID']==60942, 'Connector_Type'] = 'AC'
data.loc[data['CPID']==62009, 'Connector_Type'] = 'AC'
data.loc[data['CPID']==60979, 'Connector_Type'] = 'AC'
data.loc[data['CPID']=='APT51333', 'Connector_Type'] = 'Rapid'

#removing anomalous data
data2 = data.copy()
dates_to_remove = ['2022-10-30', '2023-10-01', '2024-02-04', '2023-03-06', '2023-03-07', '2023-03-08', '2023-03-09', '2023-03-10', '2023-03-11', '2023-03-12', '2023-06-05', '2023-06-06', '2023-06-07', '2023-06-08', '2023-06-09', '2023-06-10', '2023-06-11']
data2 = data2[~data2['Start'].isin(dates_to_remove)]
#converting Start to date format
data2['Start'] = pd.to_datetime(data2['Start']).dt.date

#assigning quintiles according to ScotGov values
def assign_quintile(x):
    if x <= 1395:
        return 1
    elif x <= 2790:
        return 2
    elif x <= 4185:
        return 3
    elif x <= 5580:
        return 4
    else:
        return 5

data2['Rankv2_quintile'] = data2['Rankv2'].apply(assign_quintile)
data2['GAccRank_quintile'] = data2['GAccRank'].apply(assign_quintile)

######finding average GAcc rank/quintile of chargers in each LA
avg_acc = data2[['CPID', 'local_authority', 'GAccRank_quintile']].drop_duplicates()
avg_acc = avg_acc.groupby('local_authority')['GAccRank_quintile'].mean().reset_index()
avg_acc = avg_acc.rename(columns={'GAccRank_quintile':'avg_GAcc_quin'})

avg_acc2 = data2[['CPID', 'local_authority', 'GAccRank']].drop_duplicates()
avg_acc2 = avg_acc2.groupby('local_authority')['GAccRank'].mean().reset_index()
avg_acc2 = avg_acc2.rename(columns={'GAccRank':'avg_GAcc'})

###################################PLOTTING####################################

#####plotting number of daily sessions and number of chargers observed

#grouping by start date and finding number of unique CPIDs as they appear on daily basis
unique_CPIDs_per_day = data2.groupby('Start')['CPID'].apply(lambda x: x.unique()).reset_index()

#counting number of unique CPIDs as they appear in the dataset
cumulative_unique_ids_day = set()
cumulative_counts = []

for _, row in unique_CPIDs_per_day.iterrows():
    cumulative_unique_ids_day.update(row['CPID'])
    cumulative_counts.append({
        'Start': row['Start'],
        'Cumulative_Unique_CPID_Count_Day': len(cumulative_unique_ids_day)
    })

#converting cumulative counts to a dataframe
cumulative_counts_CPID = pd.DataFrame(cumulative_counts)

#finding the total number of sessions per day
sessions_per_day = data2.groupby('Start').size().reset_index(name='session_count')

#merging to give a dataframe with the total number of sessions per day and the cumulative number of chargers observed
sessions_chargers = pd.merge(sessions_per_day, cumulative_counts_CPID, how='left', left_on='Start', right_on='Start')

#plotting
fig, ax1 = plt.subplots()

color = '#4059AD'
ax1.set_xlabel('Date') 
ax1.set_ylabel('Number of Daily Sessions', color = color) 
plt.xticks(rotation=45)
ax1.plot(sessions_chargers.Start, sessions_chargers.session_count, color = color) 
ax1.tick_params(axis ='y', labelcolor = color) 

ax2 = ax1.twinx() 

color = '#F4B942'
ax2.set_ylabel('Number of Chargers', color = color) 
ax2.plot(sessions_chargers.Start, sessions_chargers.Cumulative_Unique_CPID_Count_Day, color = color) 
ax2.tick_params(axis ='y', labelcolor = color)

plt.show()

###############################################################################

###separating data into different dataframes by characteristic
data2_urban1 = data2[data2['UR8Class']==1]
data2_urban8 = data2[data2['UR8Class']==8]
data2_SIMD1 = data2[data2['Rankv2_quintile']==1]
data2_SIMD5 = data2[data2['Rankv2_quintile']==5]
data2_GA1 = data2[data2['GAccRank_quintile']==1]
data2_GA5 = data2[data2['GAccRank_quintile']==5]

#####plotting where the chargers are

###UR Class 

#isolating only AC chargers
data2_AC = data2[data2['Connector_Type']=='AC']
#finding the total number of AC chargers in each UR Class
chargers_per_URClass_AC = data2_AC.groupby('UR8Class')['CPID'].nunique().reset_index()

#isolating only rapid and ultra-rapid chargers
data2_Rapid = data2[data2['Connector_Type'].isin(['Rapid', 'Ultra-Rapid'])]
#finding the total number of rapid and ultra-rapid chargers in each UR Class
chargers_per_URClass_Rapid = data2_Rapid.groupby('UR8Class')['CPID'].nunique().reset_index()

#renaming columns
chargers_per_URClass_AC.columns = ['UR8Class', 'AC']
chargers_per_URClass_Rapid.columns = ['UR8Class', 'Rapid/Ultra-Rapid']

#merging into one dataframe
chargers_per_URClass_byspeed = pd.merge(chargers_per_URClass_AC, chargers_per_URClass_Rapid, on='UR8Class')
#converting URClass from float to int so the plots don't include .0 in the axis
chargers_per_URClass_byspeed['UR8Class'] = chargers_per_URClass_byspeed['UR8Class'].astype(int)

#plotting
ax=chargers_per_URClass_byspeed.plot.bar(x='UR8Class',stacked=True, color=['#6600CC', 'xkcd:sky blue'])
plt.xlabel('Urban Rural Classification')
plt.ylabel('Number of chargers')
plt.xticks(rotation=360)

#adding annotation to label urban/rural direction of UR Class
#leaving space underneath chart area for the addition
plt.subplots_adjust(bottom=0.25)

#adding urban/rural labels under x-axis outwith chart area
ax.figure.text(0.15, 0.08, 'Urban', ha='center', va='center')
ax.figure.text(0.85, 0.08, 'Rural', ha='center', va='center')

#adding the double headed arrow
ax.annotate(
    '', xy=(0.075, -0.33), xytext=(0.9, -0.33),
    xycoords='axes fraction', textcoords='axes fraction',
    arrowprops=dict(arrowstyle='<->', color='black')
)

plt.show()

###UR Class by population

#importing population of UR Class bands
UR8Class_pop = pd.read_excel("UR_Classification_populations_from_NRS.xlsx")

#merging population data with UR Class and number of AC and rapid/ultra-rapid chargers data
URClass_speed_pop = pd.merge(chargers_per_URClass_byspeed, UR8Class_pop, on='UR8Class', how='left')
#renaming columns
URClass_speed_pop.columns = ['UR8Class','AC_CPID', 'Rapid/Ultra-Rapid_CPID', 'Population']
#finding AC chargers per 100,000 people
URClass_speed_pop['AC'] = (URClass_speed_pop['AC_CPID']/URClass_speed_pop['Population'])*100000
#finding rapid/ultra-rapid chargers per 100,000 people
URClass_speed_pop['Rapid/Ultra-Rapid'] = (URClass_speed_pop['Rapid/Ultra-Rapid_CPID']/URClass_speed_pop['Population'])*100000
#dropping unnecessary columns
URClass_speed_pop = URClass_speed_pop.drop(columns=['Population', 'Rapid/Ultra-Rapid_CPID', 'AC_CPID'])

#plotting
ax=URClass_speed_pop.plot.bar(x='UR8Class',stacked=True, color=['#6600CC', 'xkcd:sky blue'])
plt.xlabel('Urban Rural Classification')
plt.ylabel('Number of chargers per \n 100,000 people')
plt.xticks(rotation=360)
#adding annotation to label urban/rural direction of UR Class
#leaving space underneath chart area for the addition
plt.subplots_adjust(bottom=0.25)

#adding urban/rural labels under x-axis outwith chart area
ax.figure.text(0.15, 0.08, 'Urban', ha='center', va='center')
ax.figure.text(0.85, 0.08, 'Rural', ha='center', va='center')

#adding the double headed arrow
ax.annotate(
    '', xy=(0.08, -0.33), xytext=(0.9, -0.33),
    xycoords='axes fraction', textcoords='axes fraction',
    arrowprops=dict(arrowstyle='<->', color='black')
)

plt.show()

###SIMD quintiles

#finding number of AC chargers per SIMD quintile
chargers_per_simdquin_AC = data2_AC.groupby('Rankv2_quintile')['CPID'].nunique().reset_index()
#finding number of rapid/ultra-rapid chargers per SIMD quintile
chargers_per_simdquin_Rapid = data2_Rapid.groupby('Rankv2_quintile')['CPID'].nunique().reset_index()
#renaming columns
chargers_per_simdquin_AC.columns = ['Rankv2_quintile', 'AC_CPID']
chargers_per_simdquin_Rapid.columns = ['Rankv2_quintile', 'Rapid_UltraRapid_CPID']
#merging into one dataframe
chargers_per_simdquin_byspeed = pd.merge(chargers_per_simdquin_AC, chargers_per_simdquin_Rapid, on='Rankv2_quintile')
#renaming columns
chargers_per_simdquin_byspeed.columns = ['Rankv2_quintile', 'AC', 'Rapid/Ultra-Rapid']

#plotting
ax=chargers_per_simdquin_byspeed.plot.bar(x='Rankv2_quintile',stacked=True, color=['#6600CC', 'xkcd:sky blue'])
plt.xlabel('Scottish Index of Multiple Deprivation Quintile')
plt.ylabel('Number of chargers')
plt.xticks(rotation=360)
#adding annotation to label urban/rural direction of SIMD
#leaving space underneath chart area for the addition
plt.subplots_adjust(bottom=0.2)

#adding urban/rural labels under x-axis outwith chart area
ax.figure.text(0.15, 0.08, 'More Deprived', ha='center', va='center')
ax.figure.text(0.85, 0.08, 'Less Deprived', ha='center', va='center')

#adding the double headed arrow
ax.annotate(
    '', xy=(0.075, -0.25), xytext=(0.9, -0.25),
    xycoords='axes fraction', textcoords='axes fraction',
    arrowprops=dict(arrowstyle='<->', color='black')
)

plt.show()

###GA index quintiles

#finding number of AC chargers per GA quintile
chargers_per_gaccquin_AC = data2_AC.groupby('GAccRank_quintile')['CPID'].nunique().reset_index()
#finding number of rapid/ultra-rapid chargers per GA quintile
chargers_per_gaccquin_Rapid = data2_Rapid.groupby('GAccRank_quintile')['CPID'].nunique().reset_index()
#renaming columns
chargers_per_gaccquin_AC.columns = ['GAccRank_quintile', 'AC_CPID']
chargers_per_gaccquin_Rapid.columns = ['GAccRank_quintile', 'Rapid_UltraRapid_CPID']
#merging
chargers_per_gaccquin_byspeed = pd.merge(chargers_per_gaccquin_AC, chargers_per_gaccquin_Rapid, on='GAccRank_quintile')
#renaming columns
chargers_per_gaccquin_byspeed.columns = ['GAccRank_quintile', 'AC', 'Rapid/Ultra-Rapid']

#plotting
ax=chargers_per_gaccquin_byspeed.plot.bar(x='GAccRank_quintile',stacked=True, color=['#6600CC', 'xkcd:sky blue'])
plt.xlabel('Geographical Accessibility Quintile')
plt.ylabel('Number of chargers')
plt.xticks(rotation=360)
#adding annotation to label urban/rural direction of SIMD
#leaving space underneath chart area for the addition
plt.subplots_adjust(bottom=0.2)

#adding urban/rural labels under x-axis outwith chart area
ax.figure.text(0.15, 0.08, 'Less Accessible', ha='center', va='center')
ax.figure.text(0.85, 0.08, 'More Accessible', ha='center', va='center')

#adding the double headed arrow
ax.annotate(
    '', xy=(0.075, -0.25), xytext=(0.9, -0.25),
    xycoords='axes fraction', textcoords='axes fraction',
    arrowprops=dict(arrowstyle='<->', color='black')
)

plt.show()

###SIMD and GA number of chargers per 100,000 people charts

#bringing in population data
SIMD_pop = pd.read_excel("SIMD_populations_from_NRS.xlsx")
GAcc_pop = pd.read_excel("GA_populations.xlsx")

#merging population data 
SIMD_speed_pop = pd.merge(chargers_per_simdquin_byspeed, SIMD_pop, on='Rankv2_quintile', how='left')
#renaming columns
SIMD_speed_pop.columns = ['Rankv2_quintile','AC_CPID', 'Rapid/Ultra-Rapid_CPID', 'Population']
#finding number of chargers per 100,000 people
SIMD_speed_pop['AC'] = (SIMD_speed_pop['AC_CPID']/SIMD_speed_pop['Population'])*100000
SIMD_speed_pop['Rapid/Ultra-Rapid'] = (SIMD_speed_pop['Rapid/Ultra-Rapid_CPID']/SIMD_speed_pop['Population'])*100000
#dropping unneccessary columns
SIMD_speed_pop = SIMD_speed_pop.drop(columns=['Population', 'Rapid/Ultra-Rapid_CPID', 'AC_CPID'])

#merging population data 
GAcc_speed_pop = pd.merge(chargers_per_gaccquin_byspeed, GAcc_pop, on='GAccRank_quintile', how='left')
GAcc_speed_pop.columns = ['GAccRank_quintile','AC_CPID', 'Rapid/Ultra-Rapid_CPID', 'Population']
#finding number of chargers per 100,000 people
GAcc_speed_pop['AC'] = (GAcc_speed_pop['AC_CPID']/GAcc_speed_pop['Population'])*100000
GAcc_speed_pop['Rapid/Ultra-Rapid'] = (GAcc_speed_pop['Rapid/Ultra-Rapid_CPID']/GAcc_speed_pop['Population'])*100000
GAcc_speed_pop = GAcc_speed_pop.drop(columns=['Population', 'Rapid/Ultra-Rapid_CPID', 'AC_CPID'])

#plotting
ax=SIMD_speed_pop.plot.bar(x='Rankv2_quintile',stacked=True, color=['#6600CC', 'xkcd:sky blue'])
plt.xlabel('Scottish Index of Multiple Deprivation Quintile')
plt.ylabel('Number of chargers per 100,000 people')
plt.subplots_adjust(bottom=0.22)
plt.xticks(rotation=360)
#adding urban/rural labels under x-axis outwith chart area
ax.figure.text(0.15, 0.09, 'More Deprived', ha='center', va='center')
ax.figure.text(0.85, 0.09, 'Less Deprived', ha='center', va='center')

#adding the double headed arrow
ax.annotate(
    '', xy=(0.075, -0.24), xytext=(0.9, -0.24),
    xycoords='axes fraction', textcoords='axes fraction',
    arrowprops=dict(arrowstyle='<->', color='black')
)

plt.show()

ax=GAcc_speed_pop.plot.bar(x='GAccRank_quintile',stacked=True, color=['#6600CC', 'xkcd:sky blue'])
plt.xlabel('Geographical Accessibility Quintile')
plt.ylabel('Number of chargers per 100,000 people')
plt.subplots_adjust(bottom=0.22)
plt.xticks(rotation=360)
#adding urban/rural labels under x-axis outwith chart area
ax.figure.text(0.15, 0.09, 'Less Accessible', ha='center', va='center')
ax.figure.text(0.85, 0.09, 'More Accessible', ha='center', va='center')

#adding the double headed arrow
ax.annotate(
    '', xy=(0.075, -0.24), xytext=(0.9, -0.24),
    xycoords='axes fraction', textcoords='axes fraction',
    arrowprops=dict(arrowstyle='<->', color='black')
)
plt.show()

###############################################################################

#####plotting when the chargers are used

#######by day of the week#######

#copying main dataframe to add day of week tag, all sessions
data_week = data2.copy()
#converting Start to datetime
data_week['Start'] = pd.to_datetime(data_week['Start'])
#adding day of week tag
data_week['day_of_week'] = data_week['Start'].dt.dayofweek
#finding number of sessions per day and day of week tag
week_dailysessions = data_week.groupby(data_week['Start'].dt.date).size().reset_index(name='session_count')
week_dailysessions['day_of_week'] = pd.to_datetime(week_dailysessions['Start']).dt.dayofweek
#finding the average number of sessions per day of week
avgweek = week_dailysessions.groupby('day_of_week')['session_count'].mean().reset_index(name='average_session_count')
#naming the days
day_name_map = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
#applying the name of the days
avgweek['day_of_week'] = avgweek['day_of_week'].map(day_name_map)
#finding the standard deviation
stdev_week = week_dailysessions.groupby('day_of_week')['session_count'].std().reset_index(name='average_session_count')
stdev_week['day_of_week'] = stdev_week['day_of_week'].map(day_name_map)

#sessions per 100,000 people (2021 population of Scotland is 5479900 according to National Records of Scotland, 2021 because the SIMD, UR, GA populations are from this year)
avgweek['average_session_count_per100000'] = (avgweek['average_session_count']/5479900)*100000
stdev_week['average_session_count_per100000'] = (stdev_week['average_session_count']/5479900)*100000

#copying main dataframe to add day of week tag, UR1
data_week_UR1 = data2_urban1.copy()
#converting Start to datetime
data_week_UR1['Start'] = pd.to_datetime(data_week_UR1['Start'])
#adding day of week tag
data_week_UR1['day_of_week'] = data_week_UR1['Start'].dt.dayofweek
#finding number of sessions per day and day of week tag
week_dailysessions_UR1 = data_week_UR1.groupby(data_week_UR1['Start'].dt.date).size().reset_index(name='session_count')
week_dailysessions_UR1['day_of_week'] = pd.to_datetime(week_dailysessions_UR1['Start']).dt.dayofweek
#finding the average number of sessions per day of week
avgweek_UR1 = week_dailysessions_UR1.groupby('day_of_week')['session_count'].mean().reset_index(name='average_session_count')
#applying the name of the days
avgweek_UR1['day_of_week'] = avgweek_UR1['day_of_week'].map(day_name_map)
#finding the standard deviation
stdev_week_UR1 = week_dailysessions_UR1.groupby('day_of_week')['session_count'].std().reset_index(name='average_session_count')
stdev_week_UR1['day_of_week'] = stdev_week_UR1['day_of_week'].map(day_name_map)

#sessions per 100,000 people (population in UR1 is 2061049 people)
avgweek_UR1['average_session_count_per100000'] = (avgweek_UR1['average_session_count']/2061049)*100000
stdev_week_UR1['average_session_count_per100000'] = (stdev_week_UR1['average_session_count']/2061049)*100000

#copying main dataframe to add day of week tag, UR8
data_week_UR8 = data2_urban8.copy()
#converting Start to datetime
data_week_UR8['Start'] = pd.to_datetime(data_week_UR8['Start'])
#adding day of week tag
data_week_UR8['day_of_week'] = data_week_UR8['Start'].dt.dayofweek
#finding number of sessions per day and day of week tag
week_dailysessions_UR8 = data_week_UR8.groupby(data_week_UR8['Start'].dt.date).size().reset_index(name='session_count')
week_dailysessions_UR8['day_of_week'] = pd.to_datetime(week_dailysessions_UR8['Start']).dt.dayofweek
#finding the average number of sessions per day of week
avgweek_UR8 = week_dailysessions_UR8.groupby('day_of_week')['session_count'].mean().reset_index(name='average_session_count')
#applying the name of the days
avgweek_UR8['day_of_week'] = avgweek_UR8['day_of_week'].map(day_name_map)
#finding the standard deviation
stdev_week_UR8 = week_dailysessions_UR8.groupby('day_of_week')['session_count'].std().reset_index(name='average_session_count')
stdev_week_UR8['day_of_week'] = stdev_week_UR8['day_of_week'].map(day_name_map)

#sessions per 100,000 people (population in UR8 is 151039 people)
avgweek_UR8['average_session_count_per100000'] = (avgweek_UR8['average_session_count']/151039)*100000
stdev_week_UR8['average_session_count_per100000'] = (stdev_week_UR8['average_session_count']/151039)*100000

#copying main dataframe to add day of week tag, SIMD 1st quintile
data_week_SIMD1 = data2_SIMD1.copy()
#converting Start to datetime
data_week_SIMD1['Start'] = pd.to_datetime(data_week_SIMD1['Start'])
#adding day of week tag
data_week_SIMD1['day_of_week'] = data_week_SIMD1['Start'].dt.dayofweek
#finding number of sessions per day and day of week tag
week_dailysessions_SIMD1 = data_week_SIMD1.groupby(data_week_SIMD1['Start'].dt.date).size().reset_index(name='session_count')
week_dailysessions_SIMD1['day_of_week'] = pd.to_datetime(week_dailysessions_SIMD1['Start']).dt.dayofweek
#finding the average number of sessions per day of week
avgweek_SIMD1 = week_dailysessions_SIMD1.groupby('day_of_week')['session_count'].mean().reset_index(name='average_session_count')
#applying the name of the days
avgweek_SIMD1['day_of_week'] = avgweek_SIMD1['day_of_week'].map(day_name_map)
#finding the standard deviation
stdev_week_SIMD1 = week_dailysessions_SIMD1.groupby('day_of_week')['session_count'].std().reset_index(name='average_session_count')
stdev_week_SIMD1['day_of_week'] = stdev_week_SIMD1['day_of_week'].map(day_name_map)

#sessions per 100,000 people (population in SIMD1 is 1052976 people)
avgweek_SIMD1['average_session_count_per100000'] = (avgweek_SIMD1['average_session_count']/1052976)*100000
stdev_week_SIMD1['average_session_count_per100000'] = (stdev_week_SIMD1['average_session_count']/1052976)*100000

#copying main dataframe to add day of week tag, SIMD 5th quintile
data_week_SIMD5 = data2_SIMD5.copy()
#converting Start to datetime
data_week_SIMD5['Start'] = pd.to_datetime(data_week_SIMD5['Start'])
#adding day of week tag
data_week_SIMD5['day_of_week'] = data_week_SIMD5['Start'].dt.dayofweek
#finding number of sessions per day and day of week tag
week_dailysessions_SIMD5 = data_week_SIMD5.groupby(data_week_SIMD5['Start'].dt.date).size().reset_index(name='session_count')
week_dailysessions_SIMD5['day_of_week'] = pd.to_datetime(week_dailysessions_SIMD5['Start']).dt.dayofweek
#finding the average number of sessions per day of week
avgweek_SIMD5 = week_dailysessions_SIMD5.groupby('day_of_week')['session_count'].mean().reset_index(name='average_session_count')
#applying the name of the days
avgweek_SIMD5['day_of_week'] = avgweek_SIMD5['day_of_week'].map(day_name_map)
#finding the standard deviation
stdev_week_SIMD5 = week_dailysessions_SIMD5.groupby('day_of_week')['session_count'].std().reset_index(name='average_session_count')
stdev_week_SIMD5['day_of_week'] = stdev_week_SIMD5['day_of_week'].map(day_name_map)

#sessions per 100,000 people (population in SIMD5 is 1131425)
avgweek_SIMD5['average_session_count_per100000'] = (avgweek_SIMD5['average_session_count']/1131425)*100000
stdev_week_SIMD5['average_session_count_per100000'] = (stdev_week_SIMD5['average_session_count']/1131425)*100000

#copying main dataframe to add day of week tag, GA 1st quintile
data_week_GA1 = data2_GA1.copy()
#converting Start to datetime
data_week_GA1['Start'] = pd.to_datetime(data_week_GA1['Start'])
#adding day of week tag
data_week_GA1['day_of_week'] = data_week_GA1['Start'].dt.dayofweek
#finding number of sessions per day and day of week tag
week_dailysessions_GA1 = data_week_GA1.groupby(data_week_GA1['Start'].dt.date).size().reset_index(name='session_count')
week_dailysessions_GA1['day_of_week'] = pd.to_datetime(week_dailysessions_GA1['Start']).dt.dayofweek
#finding the average number of sessions per day of week
avgweek_GA1 = week_dailysessions_GA1.groupby('day_of_week')['session_count'].mean().reset_index(name='average_session_count')
#applying the name of the days
avgweek_GA1['day_of_week'] = avgweek_GA1['day_of_week'].map(day_name_map)
#finding the standard deviation
stdev_week_GA1 = week_dailysessions_GA1.groupby('day_of_week')['session_count'].std().reset_index(name='average_session_count')
stdev_week_GA1['day_of_week'] = stdev_week_GA1['day_of_week'].map(day_name_map)

#sessions per 100,000 people (population in GA1 is 1108317)
avgweek_GA1['average_session_count_per100000'] = (avgweek_GA1['average_session_count']/1108317)*100000
stdev_week_GA1['average_session_count_per100000'] = (stdev_week_GA1['average_session_count']/1108317)*100000

#copying main dataframe to add day of week tag, GA 5th quintile
data_week_GA5 = data2_GA5.copy()
#converting Start to datetime
data_week_GA5['Start'] = pd.to_datetime(data_week_GA5['Start'])
#adding day of week tag
data_week_GA5['day_of_week'] = data_week_GA5['Start'].dt.dayofweek
#finding number of sessions per day and day of week tag
week_dailysessions_GA5 = data_week_GA5.groupby(data_week_GA5['Start'].dt.date).size().reset_index(name='session_count')
week_dailysessions_GA5['day_of_week'] = pd.to_datetime(week_dailysessions_GA5['Start']).dt.dayofweek
#finding the average number of sessions per day of week
avgweek_GA5 = week_dailysessions_GA5.groupby('day_of_week')['session_count'].mean().reset_index(name='average_session_count')
#applying the name of the days
avgweek_GA5['day_of_week'] = avgweek_GA5['day_of_week'].map(day_name_map)
#finding the standard deviation
stdev_week_GA5 = week_dailysessions_GA5.groupby('day_of_week')['session_count'].std().reset_index(name='average_session_count')
stdev_week_GA5['day_of_week'] = stdev_week_GA5['day_of_week'].map(day_name_map)

#plotting sessions per 100,000 people (population in GA1 is 1086595)
avgweek_GA5['average_session_count_per100000'] = (avgweek_GA5['average_session_count']/1086595)*100000
stdev_week_GA5['average_session_count_per100000'] = (stdev_week_GA5['average_session_count']/1086595)*100000

#all day of week plots combined
#creating both plots on one figure with two stacked subplots (2 rows, 1 column)
fig, axes = plt.subplots(4, 2, figsize=(15, 20))

axes = axes.flatten()

#plot 1
plt.sca(axes[0]) 
plt.errorbar(avgweek_UR1['day_of_week'], avgweek_UR1['average_session_count_per100000'], yerr=stdev_week_UR1['average_session_count_per100000'], capsize=4, capthick=1, color='#66FF66', marker='s', elinewidth=1)
plt.ylim(50, 200)
plt.xlabel('Day of the Week', fontsize=15)
plt.ylabel('Average number of sessions per \n 100,000 people, Urban Rural \n Classification 1', fontsize=15)
plt.xticks(rotation=45, fontsize=14)
plt.yticks(fontsize=14)

#plot 2
plt.sca(axes[1])
plt.errorbar(avgweek_UR8['day_of_week'], avgweek_UR8['average_session_count_per100000'], yerr=stdev_week_UR8['average_session_count_per100000'], capsize=4, capthick=1, color='#99CC00', marker='s', elinewidth=1)
plt.ylim(50, 200)
plt.xlabel('Day of the Week', fontsize=15)
plt.ylabel('Average number of sessions per \n 100,000 people, Urban Rural \n Classification 8', fontsize=15)
plt.xticks(rotation=45, fontsize=14)
plt.yticks(fontsize=14)

#plot 3
plt.sca(axes[2]) 
plt.errorbar(avgweek_SIMD1['day_of_week'], avgweek_SIMD1['average_session_count_per100000'], yerr=stdev_week_SIMD1['average_session_count_per100000'], capsize=4, capthick=1, color='#66FF66', marker='s', elinewidth=1)
plt.ylim(50, 200)
plt.xlabel('Day of the Week', fontsize=15)
plt.ylabel('Average number of sessions per \n 100,000 people, 1st Scottish Index \n of Multiple Deprivation Quintile', fontsize=15)
plt.xticks(rotation=45, fontsize=14)
plt.yticks(fontsize=14)

#plot 4
plt.sca(axes[3])
plt.errorbar(avgweek_SIMD5['day_of_week'], avgweek_SIMD5['average_session_count_per100000'], yerr=stdev_week_SIMD5['average_session_count_per100000'], capsize=4, capthick=1, color='#99CC00', marker='s', elinewidth=1)
plt.ylim(50, 200)
plt.xlabel('Day of the Week', fontsize=15)
plt.ylabel('Average number of sessions per \n 100,000 people, 5th Scottish Index \n of Multiple Deprivation Quintile', fontsize=15)
plt.xticks(rotation=45, fontsize=14)
plt.yticks(fontsize=14)

#plot 5
plt.sca(axes[4])
plt.errorbar(avgweek_GA1['day_of_week'], avgweek_GA1['average_session_count_per100000'], yerr=stdev_week_GA1['average_session_count_per100000'], capsize=4, capthick=1, color='#66FF66', marker='s', elinewidth=1)
plt.ylim(50, 200)
plt.xlabel('Day of the Week', fontsize=15)
plt.ylabel('Average number of sessions per \n 100,000 people, 1st Geographical \n Accessibility Quintile', fontsize=15)
plt.xticks(rotation=45, fontsize=14)
plt.yticks(fontsize=14)

#plot 6
plt.sca(axes[5])
plt.errorbar(avgweek_GA5['day_of_week'], avgweek_GA5['average_session_count_per100000'], yerr=stdev_week_GA5['average_session_count_per100000'], capsize=4, capthick=1, color='#99CC00', marker='s', elinewidth=1)
plt.ylim(50, 200)
plt.xlabel('Day of the Week', fontsize=15)
plt.ylabel('Average number of sessions per \n 100,000 people, 5th Geographical \n Accessibility Quintile', fontsize=15)
plt.xticks(rotation=45, fontsize=14)
plt.yticks(fontsize=14)

#plot 7
plt.sca(axes[6])
plt.errorbar(avgweek['day_of_week'], avgweek['average_session_count_per100000'], yerr=stdev_week['average_session_count_per100000'], capsize=4, capthick=1, color='green', marker='s', elinewidth=1)
plt.ylim(50, 200)
plt.xlabel('Day of the Week', fontsize=15)
plt.ylabel('Average number of sessions per \n 100,000 people, all sessions', fontsize=15)
plt.xticks(rotation=45, fontsize=14)
plt.yticks(fontsize=14)

#removing last empty plot
axes[7].axis('off')

#preventing overlap
plt.tight_layout()

#showing combined figure
plt.show()

#########by hour of day########

##all sessions

#identifying weekends and weekdays
data_week['WEEKDAY'] = data_week.Start.dt.dayofweek
data_week['WEEKEND'] = np.where(data_week.Start.dt.dayofweek.isin([5,6]), 1, 0)
weekends = data_week[data_week['WEEKEND']==1]
workdays = data_week[data_week['WEEKEND']!=1]

#rounding start time down to the nearest hour
weekends_copy = weekends.copy()
weekends_copy['rounded_time'] = weekends_copy['Time'].apply(lambda x: x.replace(minute=0, second=0))
workdays_copy = workdays.copy()
workdays_copy['rounded_time'] = workdays_copy['Time'].apply(lambda x: x.replace(minute=0, second=0))

#finding how many times each rounded time appears
weekends_freq = weekends_copy['rounded_time'].value_counts().sort_index()
#finding the total number of weekend sessions
weekends_tot=weekends_freq.sum()
#finding the percentage of sessions starting at each time
weekends_perc = (weekends_freq/weekends_tot)*100

#finding how many times each rounded time appears
workdays_freq = workdays_copy['rounded_time'].value_counts().sort_index()
#finding the total number of weekend sessions
workdays_tot=workdays_freq.sum()
#finding the percentage of sessions starting at each time
workdays_perc = (workdays_freq/workdays_tot)*100

##UR1

#identifying weekends and weekdays
data_week_UR1['WEEKDAY'] = data_week_UR1.Start.dt.dayofweek
data_week_UR1['WEEKEND'] = np.where(data_week_UR1.Start.dt.dayofweek.isin([5,6]), 1, 0)
weekends_UR1 = data_week_UR1[data_week_UR1['WEEKEND']==1]
workdays_UR1 = data_week_UR1[data_week_UR1['WEEKEND']!=1]

#rounding start time down to the nearest hour
weekends_copy_UR1 = weekends_UR1.copy()
weekends_copy_UR1['rounded_time'] = weekends_copy_UR1['Time'].apply(lambda x: x.replace(minute=0, second=0))
workdays_copy_UR1 = workdays_UR1.copy()
workdays_copy_UR1['rounded_time'] = workdays_copy_UR1['Time'].apply(lambda x: x.replace(minute=0, second=0))

#finding how many times each rounded time appears
weekends_freq_UR1 = weekends_copy_UR1['rounded_time'].value_counts().sort_index()
#finding the total number of weekend sessions
weekends_tot_UR1=weekends_freq_UR1.sum()
#finding the percentage of sessions starting at each time
weekends_perc_UR1 = (weekends_freq_UR1/weekends_tot_UR1)*100

#finding how many times each rounded time appears
workdays_freq_UR1 = workdays_copy_UR1['rounded_time'].value_counts().sort_index()
#finding the total number of weekend sessions
workdays_tot_UR1=workdays_freq_UR1.sum()
#finding the percentage of sessions starting at each time
workdays_perc_UR1 = (workdays_freq_UR1/workdays_tot_UR1)*100

##UR8

#identifying weekends and weekdays
data_week_UR8['WEEKDAY'] = data_week_UR8.Start.dt.dayofweek
data_week_UR8['WEEKEND'] = np.where(data_week_UR8.Start.dt.dayofweek.isin([5,6]), 1, 0)
weekends_UR8 = data_week_UR8[data_week_UR8['WEEKEND']==1]
workdays_UR8 = data_week_UR8[data_week_UR8['WEEKEND']!=1]

#rounding start time down to the nearest hour
weekends_copy_UR8 = weekends_UR8.copy()
weekends_copy_UR8['rounded_time'] = weekends_copy_UR8['Time'].apply(lambda x: x.replace(minute=0, second=0))
workdays_copy_UR8 = workdays_UR8.copy()
workdays_copy_UR8['rounded_time'] = workdays_copy_UR8['Time'].apply(lambda x: x.replace(minute=0, second=0))

#finding how many times each rounded time appears
weekends_freq_UR8 = weekends_copy_UR8['rounded_time'].value_counts().sort_index()
#finding the total number of weekend sessions
weekends_tot_UR8=weekends_freq_UR8.sum()
#finding the percentage of sessions starting at each time
weekends_perc_UR8 = (weekends_freq_UR8/weekends_tot_UR8)*100

#finding how many times each rounded time appears
workdays_freq_UR8 = workdays_copy_UR8['rounded_time'].value_counts().sort_index()
#finding the total number of weekend sessions
workdays_tot_UR8=workdays_freq_UR8.sum()
#finding the percentage of sessions starting at each time
workdays_perc_UR8 = (workdays_freq_UR8/workdays_tot_UR8)*100

#plotting
bar_width = 0.3
r1 = np.arange(len(workdays_perc))   
r2 = [x + bar_width for x in r1] 
r3 = [x + bar_width for x in r2]

#creating both plots on one figure with two stacked subplots (2 rows, 1 column)
fig, axes = plt.subplots(2, 1, figsize=(18, 16))

#plot one
plt.sca(axes[0])  
plt.bar(r1, workdays_perc, color='green', width=bar_width, label='All sessions')
plt.bar(r2, workdays_perc_UR1, color='#66FF66', width=bar_width, label='Urban Rural Classification 1 Sessions')
plt.bar(r3, workdays_perc_UR8, color='#99CC00', width=bar_width, label='Urban Rural Classification 8 Sessions')
plt.ylim(0, 10.2)
plt.xlabel('Start Time', fontsize=20)
plt.ylabel('Percentage of Sessions (%)', fontsize=20)
plt.title('Weekdays', fontsize=24)
plt.xticks([r + bar_width for r in range(len(workdays_perc))], workdays_perc.index)  #positioning xticks in the centre
plt.xticks(rotation=45)
plt.yticks(fontsize=18)
plt.xticks(fontsize=18)
plt.legend(fontsize=18)

r1 = np.arange(len(weekends_perc))  
r2 = [x + bar_width for x in r1] 
r3 = [x + bar_width for x in r2]

#plot two
plt.sca(axes[1]) 
plt.bar(r1, weekends_perc, color='green', width=bar_width, label='All Sessions')
plt.bar(r2, weekends_perc_UR1, color='#66FF66', width=bar_width, label='Urban Rural Classification 1')
plt.bar(r3, weekends_perc_UR8, color='#99CC00', width=bar_width, label='Urban Rural Classification 8')
plt.ylim(0, 10.2)
plt.xlabel('Start Time', fontsize=20)
plt.ylabel('Percentage of Sessions (%)', fontsize=20)
plt.title('Weekends', fontsize=24)
plt.xticks([r + bar_width for r in range(len(weekends_perc))], weekends_perc.index)
plt.xticks(rotation=45)
plt.yticks(fontsize=18)
plt.xticks(fontsize=18)
#plt.legend(fontsize=15)

#preventing overlap
plt.tight_layout()

#showing combined figure
plt.show()

##SIMD1

#identifying weekends and weekdays
data_week_SIMD1['WEEKDAY'] = data_week_SIMD1.Start.dt.dayofweek
data_week_SIMD1['WEEKEND'] = np.where(data_week_SIMD1.Start.dt.dayofweek.isin([5,6]), 1, 0)
weekends_SIMD1 = data_week_SIMD1[data_week_SIMD1['WEEKEND']==1]
workdays_SIMD1 = data_week_SIMD1[data_week_SIMD1['WEEKEND']!=1]

#rounding start time down to the nearest hour
weekends_copy_SIMD1 = weekends_SIMD1.copy()
weekends_copy_SIMD1['rounded_time'] = weekends_copy_SIMD1['Time'].apply(lambda x: x.replace(minute=0, second=0))
workdays_copy_SIMD1 = workdays_SIMD1.copy()
workdays_copy_SIMD1['rounded_time'] = workdays_copy_SIMD1['Time'].apply(lambda x: x.replace(minute=0, second=0))

#finding how many times each rounded time appears
weekends_freq_SIMD1 = weekends_copy_SIMD1['rounded_time'].value_counts().sort_index()
#finding the total number of weekend sessions
weekends_tot_SIMD1=weekends_freq_SIMD1.sum()
#finding the percentage of sessions starting at each time
weekends_perc_SIMD1 = (weekends_freq_SIMD1/weekends_tot_SIMD1)*100

#finding how many times each rounded time appears
workdays_freq_SIMD1 = workdays_copy_SIMD1['rounded_time'].value_counts().sort_index()
#finding the total number of weekend sessions
workdays_tot_SIMD1=workdays_freq_SIMD1.sum()
#finding the percentage of sessions starting at each time
workdays_perc_SIMD1 = (workdays_freq_SIMD1/workdays_tot_SIMD1)*100

##SIMD5

#identifying weekends and weekdays
data_week_SIMD5['WEEKDAY'] = data_week_SIMD5.Start.dt.dayofweek
data_week_SIMD5['WEEKEND'] = np.where(data_week_SIMD5.Start.dt.dayofweek.isin([5,6]), 1, 0)
weekends_SIMD5 = data_week_SIMD5[data_week_SIMD5['WEEKEND']==1]
workdays_SIMD5 = data_week_SIMD5[data_week_SIMD5['WEEKEND']!=1]

#rounding start time down to the nearest hour
weekends_copy_SIMD5 = weekends_SIMD5.copy()
weekends_copy_SIMD5['rounded_time'] = weekends_copy_SIMD5['Time'].apply(lambda x: x.replace(minute=0, second=0))
workdays_copy_SIMD5 = workdays_SIMD5.copy()
workdays_copy_SIMD5['rounded_time'] = workdays_copy_SIMD5['Time'].apply(lambda x: x.replace(minute=0, second=0))

#finding how many times each rounded time appears
weekends_freq_SIMD5 = weekends_copy_SIMD5['rounded_time'].value_counts().sort_index()
#finding the total number of weekend sessions
weekends_tot_SIMD5=weekends_freq_SIMD5.sum()
#finding the percentage of sessions starting at each time
weekends_perc_SIMD5 = (weekends_freq_SIMD5/weekends_tot_SIMD5)*100

#finding how many times each rounded time appears
workdays_freq_SIMD5 = workdays_copy_SIMD5['rounded_time'].value_counts().sort_index()
#finding the total number of weekend sessions
workdays_tot_SIMD5=workdays_freq_SIMD5.sum()
#finding the percentage of sessions starting at each time
workdays_perc_SIMD5 = (workdays_freq_SIMD5/workdays_tot_SIMD5)*100

#plotting
bar_width = 0.3
r1 = np.arange(len(workdays_perc))  
r2 = [x + bar_width for x in r1] 
r3 = [x + bar_width for x in r2]

#creating both plots on one figure with two stacked subplots (2 rows, 1 column)
fig, axes = plt.subplots(2, 1, figsize=(18, 16))

#plot one
plt.sca(axes[0])  
plt.bar(r1, workdays_perc, color='green', width=bar_width, label='All Sessions')
plt.bar(r2, workdays_perc_SIMD1, color='#66FF66', width=bar_width, label='Scottish Index of Multiple Deprivation 1st Quintile Sessions')
plt.bar(r3, workdays_perc_SIMD5, color='#99CC00', width=bar_width, label='Scottish Index of Multiple Deprivation 5th Quintile Sessions')
plt.ylim(0, 10.2)
plt.xlabel('Start Time', fontsize=20)
plt.ylabel('Percentage of Sessions (%)', fontsize=20)
plt.title('Weekdays', fontsize=24)
plt.xticks([r + bar_width for r in range(len(workdays_perc))], workdays_perc.index)  #positioning xticks in the centre
plt.xticks(rotation=45)
plt.yticks(fontsize=18)
plt.xticks(fontsize=18)
plt.legend(fontsize=18)

r1 = np.arange(len(weekends_perc))  
r2 = [x + bar_width for x in r1] 
r3 = [x + bar_width for x in r2]

#plot two
plt.sca(axes[1]) 
plt.bar(r1, weekends_perc, color='green', width=bar_width, label='All Sessions')
plt.bar(r2, weekends_perc_SIMD1, color='#66FF66', width=bar_width, label='Scottish Index of Multiple Deprivation 1st Quintile Sessions')
plt.bar(r3, weekends_perc_SIMD5, color='#99CC00', width=bar_width, label='Scottish Index of Multiple Deprivation 5th Quintile Sessions')
plt.ylim(0, 10.2)
plt.xlabel('Start Time', fontsize=20)
plt.ylabel('Percentage of Sessions (%)', fontsize=20)
plt.title('Weekends', fontsize=24)
plt.xticks([r + bar_width for r in range(len(weekends_perc))], weekends_perc.index)
plt.xticks(rotation=45)
plt.yticks(fontsize=18)
plt.xticks(fontsize=18)
#plt.legend(fontsize=15)

#preventing overlap
plt.tight_layout()

#showing combined figure
plt.show()

##GA1

#identifying weekends and weekdays
data_week_GA1['WEEKDAY'] = data_week_GA1.Start.dt.dayofweek
data_week_GA1['WEEKEND'] = np.where(data_week_GA1.Start.dt.dayofweek.isin([5,6]), 1, 0)
weekends_GA1 = data_week_GA1[data_week_GA1['WEEKEND']==1]
workdays_GA1 = data_week_GA1[data_week_GA1['WEEKEND']!=1]

#rounding start time down to the nearest hour
weekends_copy_GA1 = weekends_GA1.copy()
weekends_copy_GA1['rounded_time'] = weekends_copy_GA1['Time'].apply(lambda x: x.replace(minute=0, second=0))
workdays_copy_GA1 = workdays_GA1.copy()
workdays_copy_GA1['rounded_time'] = workdays_copy_GA1['Time'].apply(lambda x: x.replace(minute=0, second=0))

#finding how many times each rounded time appears
weekends_freq_GA1 = weekends_copy_GA1['rounded_time'].value_counts().sort_index()
#finding the total number of weekend sessions
weekends_tot_GA1=weekends_freq_GA1.sum()
#finding the percentage of sessions starting at each time
weekends_perc_GA1 = (weekends_freq_GA1/weekends_tot_GA1)*100

#finding how many times each rounded time appears
workdays_freq_GA1 = workdays_copy_GA1['rounded_time'].value_counts().sort_index()
#finding the total number of weekend sessions
workdays_tot_GA1=workdays_freq_GA1.sum()
#finding the percentage of sessions starting at each time
workdays_perc_GA1 = (workdays_freq_GA1/workdays_tot_GA1)*100

##GA5

#identifying weekends and weekdays
data_week_GA5['WEEKDAY'] = data_week_GA5.Start.dt.dayofweek
data_week_GA5['WEEKEND'] = np.where(data_week_GA5.Start.dt.dayofweek.isin([5,6]), 1, 0)
weekends_GA5 = data_week_GA5[data_week_GA5['WEEKEND']==1]
workdays_GA5 = data_week_GA5[data_week_GA5['WEEKEND']!=1]

#rounding start time down to the nearest hour
weekends_copy_GA5 = weekends_GA5.copy()
weekends_copy_GA5['rounded_time'] = weekends_copy_GA5['Time'].apply(lambda x: x.replace(minute=0, second=0))
workdays_copy_GA5 = workdays_GA5.copy()
workdays_copy_GA5['rounded_time'] = workdays_copy_GA5['Time'].apply(lambda x: x.replace(minute=0, second=0))

#finding how many times each rounded time appears
weekends_freq_GA5 = weekends_copy_GA5['rounded_time'].value_counts().sort_index()
#finding the total number of weekend sessions
weekends_tot_GA5=weekends_freq_GA5.sum()
#finding the percentage of sessions starting at each time
weekends_perc_GA5 = (weekends_freq_GA5/weekends_tot_GA5)*100

#finding how many times each rounded time appears
workdays_freq_GA5 = workdays_copy_GA5['rounded_time'].value_counts().sort_index()
#finding the total number of weekend sessions
workdays_tot_GA5=workdays_freq_GA5.sum()
#finding the percentage of sessions starting at each time
workdays_perc_GA5 = (workdays_freq_GA5/workdays_tot_GA5)*100

#plotting
bar_width = 0.3
r1 = np.arange(len(workdays_perc))  
r2 = [x + bar_width for x in r1] 
r3 = [x + bar_width for x in r2]

#creating both plots on one figure with two stacked subplots (2 rows, 1 column)
fig, axes = plt.subplots(2, 1, figsize=(18, 16))

#plot one
plt.sca(axes[0])  
plt.bar(r1, workdays_perc, color='green', width=bar_width, label='All Sessions')
plt.bar(r2, workdays_perc_GA1, color='#66FF66', width=bar_width, label='Geographical Accessibility 1st Quintile Sessions')
plt.bar(r3, workdays_perc_GA5, color='#99CC00', width=bar_width, label='Geographical Accessibility 5th Quintile Sessions')
plt.ylim(0, 10.2)
plt.xlabel('Start Time', fontsize=20)
plt.ylabel('Percentage of Sessions (%)', fontsize=20)
plt.title('Weekdays', fontsize=24)
plt.xticks([r + bar_width for r in range(len(workdays_perc))], workdays_perc.index)  #positioning xticks in the centre
plt.xticks(rotation=45)
plt.yticks(fontsize=18)
plt.xticks(fontsize=18)
plt.legend(fontsize=18)

r1 = np.arange(len(weekends_perc))  
r2 = [x + bar_width for x in r1] 
r3 = [x + bar_width for x in r2]

#plot two
plt.sca(axes[1]) 
plt.bar(r1, weekends_perc, color='green', width=bar_width, label='All Sessions')
plt.bar(r2, weekends_perc_GA1, color='#66FF66', width=bar_width, label='Geographical Accessibility 1st Quintile Sessions')
plt.bar(r3, weekends_perc_GA5, color='#99CC00', width=bar_width, label='Geographical Accessibility 5th Quintile Sessions')
plt.ylim(0, 10.2)
plt.xlabel('Start Time', fontsize=20)
plt.ylabel('Percentage of Sessions (%)', fontsize=20)
plt.title('Weekends', fontsize=24)
plt.xticks([r + bar_width for r in range(len(weekends_perc))], weekends_perc.index)
plt.xticks(rotation=45)
plt.yticks(fontsize=18)
plt.xticks(fontsize=18)
#plt.legend(fontsize=15)

#preventing overlap
plt.tight_layout()

#showing combined figure
plt.show()

###East Lothian TOU

#isolating the chargers included
ELoth_tariff = data2[data2['CPID'].isin([51695, 51696, 52438, 52439, 52443, 52444, 51576, 51578, 51579, 52449, 51607, 51608])]

#separating into dataframes before and after the introduction of time-of-use tariffs, with a one week buffer either side to allow behaviour shift
#Time Of Use introduction date
intro_ELoth_TOU = datetime(2023,3,1).date()
#one week before and after
ELoth_tariff_pre = intro_ELoth_TOU - timedelta(weeks=1)
ELoth_tariff_post = intro_ELoth_TOU + timedelta(weeks=1)
#separating into before and after dataframes
ELoth_before_TOU = ELoth_tariff[ELoth_tariff['Start']<=ELoth_tariff_pre]
ELoth_after_TOU = ELoth_tariff[ELoth_tariff['Start']>=ELoth_tariff_post]

ELoth_before = ELoth_before_TOU.copy()
#rounding start time down
ELoth_before['rounded_time'] = ELoth_before['Time'].apply(lambda x: x.replace(minute=0, second=0))
#finding how many times each rounded time appears
ELoth_before_freq = ELoth_before['rounded_time'].value_counts().sort_index()
#finding the total number of sessions before
ELoth_before_tot=ELoth_before_freq.sum()
#finding the percentage of sessions starting at each time
ELoth_before_perc = (ELoth_before_freq/ELoth_before_tot)*100

#adding in hours wih 0 sessions for plots
#making index datetime.time format
ELoth_before_perc.index = pd.to_datetime(ELoth_before_perc.index, format='%H:%M:%S').time
#create a complete time index from 00:00:00 to 23:00:00 with hourly frequency
full_time_index = pd.date_range(start="00:00:00", end="23:00:00", freq='H').time
#reindexing the series to include all times and fill the original missing ones with 0
ELoth_before_perc = ELoth_before_perc.reindex(full_time_index, fill_value=0)

ELoth_after = ELoth_after_TOU.copy()
#rounding start time down
ELoth_after['rounded_time'] = ELoth_after['Time'].apply(lambda x: x.replace(minute=0, second=0))
#finding how many times each rounded time appears
ELoth_after_freq = ELoth_after['rounded_time'].value_counts().sort_index()
#finding the total number of sessions after
ELoth_after_tot=ELoth_after_freq.sum()
#finding the percentage of sessions starting at each time
ELoth_after_perc = (ELoth_after_freq/ELoth_after_tot)*100

#adding in hours wih 0 sessions for plots
#making index datetime.time format
ELoth_after_perc.index = pd.to_datetime(ELoth_after_perc.index, format='%H:%M:%S').time
#reindexing the series to include all times and fill the original missing ones with 0
ELoth_after_perc = ELoth_after_perc.reindex(full_time_index, fill_value=0)
#ELoth_after_perc.index = [f"{t.hour:02}:{t.minute:02}:{t.second:02}" for t in ELoth_after_perc.index]

###Finding average plug-in time

##before TOU tariff

#converting to dataframe and giving the time data its own column rather than the index
ELoth_before_perc2 = ELoth_before_perc.to_frame().reset_index()
#sorting by time order
ELoth_before_perc2 = ELoth_before_perc2.sort_values(by='index')
#converting time data to numerical format
ELoth_before_perc2['HourDecimal'] = ELoth_before_perc2['index'].apply(lambda t: t.hour + t.minute / 60)

#converting percentages to probabilities
ELoth_before_perc2['Probability'] = ELoth_before_perc2['rounded_time'] / 100

#calculating the weighted average time
weighted_sum_before = (ELoth_before_perc2['HourDecimal'] * ELoth_before_perc2['Probability']).sum()
total_probability_before = ELoth_before_perc2['Probability'].sum()

#removing possibility of division by zero in case total_probability is 0
if total_probability_before > 0:
    average_time_before = weighted_sum_before / total_probability_before
else:
    average_time_before = float('nan')  

#converting the average time to hours and minutes
average_hour_before = int(average_time_before)
average_minute_before = int((average_time_before - average_hour_before) * 60)

print(f"Average Plug-in Time Before: {average_hour_before}:{average_minute_before:02d}")

##after TOU tariff

#converting to dataframe and giving the time data its own column rather than the index
ELoth_after_perc2 = ELoth_after_perc.to_frame().reset_index()
#sorting
ELoth_after_perc2 = ELoth_after_perc2.sort_values(by='index')
#converting time data to numerical format
ELoth_after_perc2['HourDecimal'] = ELoth_after_perc2['index'].apply(lambda t: t.hour + t.minute / 60)
#converting percentages to probabilities
ELoth_after_perc2['Probability'] = ELoth_after_perc2['rounded_time'] / 100

#calculating the weighted average time
weighted_sum_after = (ELoth_after_perc2['HourDecimal'] * ELoth_after_perc2['Probability']).sum()
total_probability_after = ELoth_after_perc2['Probability'].sum()

#removing possibility of division by zero in case total_probability is 0
if total_probability_after > 0:
    average_time_after = weighted_sum_after / total_probability_after
else:
    average_time_after = float('nan')  

#converting the average time to hours and minutes
average_hour_after = int(average_time_after)
average_minute_after = int((average_time_after - average_hour_after) * 60)

print(f"Average Plug-in Time After: {average_hour_after}:{average_minute_after:02d}")

#adding a zero for times with no sessions
missing_time = pd.DataFrame({
    'index': ['03:00:00'],
    'rounded_time': [0],
    'HourDecimal': [3],
    'Probability': [0]
})
ELoth_before_perc2 = pd.concat([ELoth_before_perc2, missing_time], ignore_index=True)
#dropping extra entry
ELoth_before_perc2 = ELoth_before_perc2.drop([24])
#sorting
ELoth_before_perc2 = ELoth_before_perc2.sort_values(by='HourDecimal').reset_index(drop=True)
ELoth_after_perc2 = pd.concat([ELoth_after_perc2, missing_time], ignore_index=True)
#dropping extra entry
ELoth_after_perc2 = ELoth_after_perc2.drop([24])
#sorting
ELoth_after_perc2 = ELoth_after_perc2.sort_values(by='HourDecimal').reset_index(drop=True)

#plotting
#creating both plots on one figure with two stacked subplots (2 rows, 1 column)
fig, axes = plt.subplots(2, 1, figsize=(18, 16))

#plot one
plt.sca(axes[0])  
plt.bar(ELoth_before_perc2['HourDecimal'], ELoth_before_perc2['rounded_time'], tick_label=ELoth_before_perc2['index'], color='green', width=0.6)
plt.ylim(0, 12)
plt.ylabel('Percentage of Sessions (%)', fontsize=20)
plt.xlabel('Start Time', fontsize=20)
plt.axvline(12.24, color='black', linestyle='--', lw=2)
plt.annotate('Average Plug-In Time',xy=(12.5, 10), fontsize=20)
plt.xticks(rotation=45, fontsize=20)
plt.yticks(fontsize=20)
plt.title('Pre Time-of-Use Tariff', fontsize=24)

#plot two
plt.sca(axes[1]) 
plt.bar(ELoth_after_perc2['HourDecimal'], ELoth_after_perc2['rounded_time'], tick_label=ELoth_after_perc2['index'], color='green', width=0.6)
plt.ylim(0, 12)
plt.ylabel('Percentage of Sessions (%)',fontsize=20)
plt.xlabel('Start Time', fontsize=20)
plt.axvline(12.28, color='black', linestyle='--', lw=2)
plt.annotate('Average Plug-In Time',xy=(12.5, 10), fontsize=20)
plt.xticks(rotation=45, fontsize=20)
plt.yticks(fontsize=20)
plt.title('Post Time-of-Use Tariff', fontsize=24)
#preventing overlap
plt.tight_layout()

#showing combined figure
plt.show()

##########Kolmogorov-Smirnov test

#isolating just the start time data from before/after TOU introduction
before_TOU_test = ELoth_before.drop(columns=['CPID', 'Consumed(kWh)', 'Duration', 'Start', 'Amount', 'local_authority', 'UR8Class', 'Rankv2', 'GAccRank', 'Postcode', 'Connector_Type', 'Rankv2_quintile', 'GAccRank_quintile', 'rounded_time'])
after_TOU_test = ELoth_after.drop(columns=['CPID', 'Consumed(kWh)', 'Duration', 'Start', 'Amount', 'local_authority', 'UR8Class', 'Rankv2', 'GAccRank', 'Postcode', 'Connector_Type', 'Rankv2_quintile', 'GAccRank_quintile', 'rounded_time'])

#converting time to a decimal
def time_to_decimal(time_obj):
    return time_obj.hour + time_obj.minute / 60 + time_obj.second / 3600

#applying function to time column
after_TOU_test['time_decimal'] = after_TOU_test['Time'].apply(time_to_decimal)

before_TOU_test['time_decimal'] = before_TOU_test['Time'].apply(time_to_decimal)

#removing original time data
after_TOU_test=after_TOU_test.drop(columns=['Time'])
before_TOU_test=before_TOU_test.drop(columns=['Time'])

#converting the dataframe to format to perform KS test
sample1 = before_TOU_test['time_decimal'].values
sample2 = after_TOU_test['time_decimal'].values

#performing the KS test
statistic, p_value = ks_2samp(sample1, sample2)
#printing the result
print(f"KS Statistic: {statistic}")
print(f"P-value: {p_value}")

###############################################################################

#####North Lanarkshire sessions/sessions per charger
NorthLanarkshire = data2[data2['local_authority']=='North Lanarkshire'].copy()

sessions_per_day_nlan = NorthLanarkshire.groupby('Start').size().reset_index(name='session_count')

unique_CPIDs_per_day_nlan = NorthLanarkshire.groupby('Start')['CPID'].apply(lambda x: x.unique()).reset_index()

cumulative_unique_ids_day_nlan = set()
cumulative_counts_nlan = []

for _, row in unique_CPIDs_per_day_nlan.iterrows():
    cumulative_unique_ids_day_nlan.update(row['CPID'])
    cumulative_counts_nlan.append({
        'Start': row['Start'],
        'Cumulative_Unique_CPID_Count_Day_nlan': len(cumulative_unique_ids_day_nlan)
    })

#converting the cumulative counts to a dataframe
cumulative_counts_nlan_df = pd.DataFrame(cumulative_counts_nlan)

merging_nlan = pd.merge(sessions_per_day_nlan, cumulative_counts_nlan_df, how='left', left_on='Start', right_on='Start')
merging_nlan['sessions_per_charger_day_nlan'] = merging_nlan['session_count'] / merging_nlan['Cumulative_Unique_CPID_Count_Day_nlan']

#plotting number of sessions
fig, ax1 = plt.subplots()
color = '#4059AD'
ax1.set_xlabel('Date') 
ax1.set_ylabel('Number of daily sessions, North Lanarkshire', color = color) 
plt.xticks(rotation=45)
ax1.plot(merging_nlan.Start, merging_nlan.session_count, color = color) 
ax1.tick_params(axis ='y', labelcolor = color) 

ax2 = ax1.twinx() 

color = '#F4B942'
ax2.set_ylabel('Number of chargers, North Lanarkshire', color = color) 
ax2.plot(merging_nlan.Start, merging_nlan.Cumulative_Unique_CPID_Count_Day_nlan, color = color) 
ax2.tick_params(axis ='y', labelcolor = color)

ax2.axvline(pd.to_datetime('2023-01-04'), color='black', linestyle='--', lw=2)
ax2.annotate('Tariff Introduction',xy=(pd.to_datetime('2023-01-15'), 136))

plt.show()

#####East Renfrewshire sessions/sessions per charger
EastRen = data2[data2['local_authority']=='East Renfrewshire'].copy()

sessions_per_day_EastRen = EastRen.groupby('Start').size().reset_index(name='session_count')

unique_CPIDs_per_day_EastRen = EastRen.groupby('Start')['CPID'].apply(lambda x: x.unique()).reset_index()

cumulative_unique_ids_day_EastRen = set()
cumulative_counts_EastRen = []

for _, row in unique_CPIDs_per_day_EastRen.iterrows():
    cumulative_unique_ids_day_EastRen.update(row['CPID'])
    cumulative_counts_EastRen.append({
        'Start': row['Start'],
        'Cumulative_Unique_CPID_Count_Day_EastRen': len(cumulative_unique_ids_day_EastRen)
    })

#converting the cumulative counts to a dataframe
cumulative_counts_EastRen_df = pd.DataFrame(cumulative_counts_EastRen)

merging_EastRen = pd.merge(sessions_per_day_EastRen, cumulative_counts_EastRen_df, how='left', left_on='Start', right_on='Start')
merging_EastRen['sessions_per_charger_day_EastRen'] = merging_EastRen['session_count'] / merging_EastRen['Cumulative_Unique_CPID_Count_Day_EastRen']

#plotting number of sessions
fig, ax1 = plt.subplots()
color = '#4059AD'
ax1.set_xlabel('Date') 
ax1.set_ylabel('Number of daily sessions, East Renfrewshire', color = color) 
plt.xticks(rotation=45)
ax1.plot(merging_EastRen.Start, merging_EastRen.session_count, color = color) 
ax1.tick_params(axis ='y', labelcolor = color) 

ax2 = ax1.twinx() 

color = '#F4B942'
ax2.set_ylabel('Number of chargers, East Renfrewshire', color = color) 
ax2.plot(merging_EastRen.Start, merging_EastRen.Cumulative_Unique_CPID_Count_Day_EastRen, color = color) 
ax2.tick_params(axis ='y', labelcolor = color)

ax2.axvline(pd.to_datetime('2023-10-01'), color='black', linestyle='--', lw=2)
ax2.annotate('Tariff Introduction',xy=(pd.to_datetime('2023-10-12'), 16))

plt.show()

####Dundee City sessions/sessions per charger
DundeeCity = data2[data2['local_authority']=='Dundee City'].copy()

sessions_per_day_dundee = DundeeCity.groupby('Start').size().reset_index(name='session_count')

unique_CPIDs_per_day_dundee = DundeeCity.groupby('Start')['CPID'].apply(lambda x: x.unique()).reset_index()

cumulative_unique_ids_day_dundee = set()
cumulative_counts_dundee = []

for _, row in unique_CPIDs_per_day_dundee.iterrows():
    cumulative_unique_ids_day_dundee.update(row['CPID'])
    cumulative_counts_dundee.append({
        'Start': row['Start'],
        'Cumulative_Unique_CPID_Count_Day_dundee': len(cumulative_unique_ids_day_dundee)
    })

#converting the cumulative counts to a dataframe
cumulative_counts_dundee_df = pd.DataFrame(cumulative_counts_dundee)

merging_dundee = pd.merge(sessions_per_day_dundee, cumulative_counts_dundee_df, how='left', left_on='Start', right_on='Start')
merging_dundee['sessions_per_charger_day_dundee'] = merging_dundee['session_count'] / merging_dundee['Cumulative_Unique_CPID_Count_Day_dundee']

#plotting sessions per day
fig, ax1 = plt.subplots()
color = '#4059AD'
ax1.set_xlabel('Date') 
ax1.set_ylabel('Number of daily sessions, Dundee City', color = color) 
plt.xticks(rotation=45)
ax1.plot(merging_dundee.Start, merging_dundee.session_count, color = color) 
ax1.tick_params(axis ='y', labelcolor = color) 

ax2 = ax1.twinx() 

color = '#F4B942'
ax2.set_ylabel('Number of chargers, Dundee City', color = color) 
ax2.plot(merging_dundee.Start, merging_dundee.Cumulative_Unique_CPID_Count_Day_dundee, color = color) 
ax2.tick_params(axis ='y', labelcolor = color)

plt.show()

###############################################################################

##########Pre/Post Tariff Analysis

###Clackmannanshire
Clackm = data2[data2['local_authority']=='Clackmannanshire']

dailysessions_Clackm = Clackm.groupby('Start').size().reset_index(name='session_count')

##adding daily energy consumed
dailyconsumed_Clackm = Clackm.groupby('Start')['Consumed(kWh)'].sum().reset_index(name='daily_consumed')

dailysessions_Clackm = pd.merge(dailysessions_Clackm, dailyconsumed_Clackm, on='Start')

##Clackmannanshire census 2022 population is 51800 people
dailysessions_Clackm['Sessionsper100000'] = (dailysessions_Clackm['session_count']/51800)*100000
dailysessions_Clackm['kWhper100000'] = (dailysessions_Clackm['daily_consumed']/51800)*100000

##one week buffer before and after tariff intro (01/07/2023) to allow for behaviour shift
intro_Clackm = datetime(2023,7,1).date()
pre_Clackm = intro_Clackm - timedelta(weeks=1)
post_Clackm = intro_Clackm + timedelta(weeks=1)

Clackm_before = dailysessions_Clackm[dailysessions_Clackm['Start']<=pre_Clackm]
Clackm_after = dailysessions_Clackm[dailysessions_Clackm['Start']>=post_Clackm]

###East Dunbartonshire
EDun = data2[data2['local_authority']=='East Dunbartonshire']

dailysessions_EDun = EDun.groupby('Start').size().reset_index(name='session_count')

##adding daily energy consumed
dailyconsumed_EDun = EDun.groupby('Start')['Consumed(kWh)'].sum().reset_index(name='daily_consumed')

dailysessions_EDun = pd.merge(dailysessions_EDun, dailyconsumed_EDun, on='Start')

##EDun census 2022 population is 109000 people
dailysessions_EDun['Sessionsper100000'] = (dailysessions_EDun['session_count']/109000)*100000
dailysessions_EDun['kWhper100000'] = (dailysessions_EDun['daily_consumed']/109000)*100000

##one week buffer before and after tariff intro to allow for behaviour shift
intro_EDun = datetime(2023,10,2).date()
pre_EDun = intro_EDun - timedelta(weeks=1)
post_EDun = intro_EDun + timedelta(weeks=1)

EDun_before = dailysessions_EDun[dailysessions_EDun['Start']<=pre_EDun]
EDun_after = dailysessions_EDun[dailysessions_EDun['Start']>=post_EDun]

###East Renfrewshire (2)
EastRen2 = data2[data2['local_authority']=='East Renfrewshire']

dailysessions_EastRen2 = EastRen2.groupby('Start').size().reset_index(name='session_count')

##adding daily energy consumed
dailyconsumed_EastRen2 = EastRen2.groupby('Start')['Consumed(kWh)'].sum().reset_index(name='daily_consumed')

dailysessions_EastRen2 = pd.merge(dailysessions_EastRen2, dailyconsumed_EastRen2, on='Start')

##EastRen census 2022 population is 96800 people
dailysessions_EastRen2['Sessionsper100000'] = (dailysessions_EastRen2['session_count']/96800)*100000
dailysessions_EastRen2['kWhper100000'] = (dailysessions_EastRen2['daily_consumed']/96800)*100000

##one week buffer before and after tariff intro to allow for behaviour shift
intro_EastRen2 = datetime(2023,10,1).date()
pre_EastRen2 = intro_EastRen2 - timedelta(weeks=1)
post_EastRen2 = intro_EastRen2 + timedelta(weeks=1)

EastRen2_before = dailysessions_EastRen2[dailysessions_EastRen2['Start']<=pre_EastRen2]
EastRen2_after = dailysessions_EastRen2[dailysessions_EastRen2['Start']>=post_EastRen2]

###Glasgow City
Glas = data2[data2['local_authority']=='Glasgow City']

dailysessions_Glas = Glas.groupby('Start').size().reset_index(name='session_count')

##adding daily energy consumed
dailyconsumed_Glas = Glas.groupby('Start')['Consumed(kWh)'].sum().reset_index(name='daily_consumed')

dailysessions_Glas = pd.merge(dailysessions_Glas, dailyconsumed_Glas, on='Start')

##Glas census 2022 population is 620700 people
dailysessions_Glas['Sessionsper100000'] = (dailysessions_Glas['session_count']/620700)*100000
dailysessions_Glas['kWhper100000'] = (dailysessions_Glas['daily_consumed']/620700)*100000

##one week buffer before and after tariff intro to allow for behaviour shift
intro_Glas = datetime(2023,4,11).date()
pre_Glas = intro_Glas - timedelta(weeks=1)
post_Glas = intro_Glas + timedelta(weeks=1)

Glas_before = dailysessions_Glas[dailysessions_Glas['Start']<=pre_Glas]
Glas_after = dailysessions_Glas[dailysessions_Glas['Start']>=post_Glas]

###North Lanarkshire (2)
NLan = data2[data2['local_authority']=='North Lanarkshire']

dailysessions_NLan = NLan.groupby('Start').size().reset_index(name='session_count')

##adding daily energy consumed
dailyconsumed_NLan = NLan.groupby('Start')['Consumed(kWh)'].sum().reset_index(name='daily_consumed')

dailysessions_NLan = pd.merge(dailysessions_NLan, dailyconsumed_NLan, on='Start')

##NLan census 2022 population is 341000 people
dailysessions_NLan['Sessionsper100000'] = (dailysessions_NLan['session_count']/341000)*100000
dailysessions_NLan['kWhper100000'] = (dailysessions_NLan['daily_consumed']/341000)*100000

##one week buffer before and after tariff intro to allow for behaviour shift
intro_NLan = datetime(2023,1,4).date()
pre_NLan = intro_NLan - timedelta(weeks=1)
post_NLan = intro_NLan + timedelta(weeks=1)

NLan_before = dailysessions_NLan[dailysessions_NLan['Start']<=pre_NLan]
NLan_after = dailysessions_NLan[dailysessions_NLan['Start']>=post_NLan]

###Perth and Kinross (2)
Perth2 = data2[data2['local_authority']=='Perth and Kinross']

dailysessions_Perth2 = Perth2.groupby('Start').size().reset_index(name='session_count')

##adding daily energy consumed
dailyconsumed_Perth2 = Perth2.groupby('Start')['Consumed(kWh)'].sum().reset_index(name='daily_consumed')

dailysessions_Perth2 = pd.merge(dailysessions_Perth2, dailyconsumed_Perth2, on='Start')

##Perth2 census 2022 population is 150800 people
dailysessions_Perth2['Sessionsper100000'] = (dailysessions_Perth2['session_count']/150800)*100000
dailysessions_Perth2['kWhper100000'] = (dailysessions_Perth2['daily_consumed']/150800)*100000

##one week buffer before and after tariff intro to allow for behaviour shift
intro_Perth2 = datetime(2023,1,1).date()
pre_Perth2 = intro_Perth2 - timedelta(weeks=1)
post_Perth2 = intro_Perth2 + timedelta(weeks=1)

Perth2_before = dailysessions_Perth2[dailysessions_Perth2['Start']<=pre_Perth2]
Perth2_after = dailysessions_Perth2[dailysessions_Perth2['Start']>=post_Perth2]

###Renfrewshire (2)
Renf2 = data2[data2['local_authority']=='Renfrewshire']

dailysessions_Renf2 = Renf2.groupby('Start').size().reset_index(name='session_count')

##adding daily energy consumed
dailyconsumed_Renf2 = Renf2.groupby('Start')['Consumed(kWh)'].sum().reset_index(name='daily_consumed')

dailysessions_Renf2 = pd.merge(dailysessions_Renf2, dailyconsumed_Renf2, on='Start')

##Renf2 census 2022 population is 183800 people
dailysessions_Renf2['Sessionsper100000'] = (dailysessions_Renf2['session_count']/183800)*100000
dailysessions_Renf2['kWhper100000'] = (dailysessions_Renf2['daily_consumed']/183800)*100000

##one week buffer before and after tariff intro to allow for behaviour shift
intro_Renf2 = datetime(2023,4,1).date()
pre_Renf2 = intro_Renf2 - timedelta(weeks=1)
post_Renf2 = intro_Renf2 + timedelta(weeks=1)

Renf2_before = dailysessions_Renf2[dailysessions_Renf2['Start']<=pre_Renf2]
Renf2_after = dailysessions_Renf2[dailysessions_Renf2['Start']>=post_Renf2]

###Shetland Islands
Shet = data2[data2['local_authority']=='Shetland Islands']

dailysessions_Shet = Shet.groupby('Start').size().reset_index(name='session_count')

##adding daily energy consumed
dailyconsumed_Shet = Shet.groupby('Start')['Consumed(kWh)'].sum().reset_index(name='daily_consumed')

dailysessions_Shet = pd.merge(dailysessions_Shet, dailyconsumed_Shet, on='Start')

##Shet census 2022 population is 22900 people
dailysessions_Shet['Sessionsper100000'] = (dailysessions_Shet['session_count']/22900)*100000
dailysessions_Shet['kWhper100000'] = (dailysessions_Shet['daily_consumed']/22900)*100000

##one week buffer before and after tariff intro to allow for behaviour shift
intro_Shet = datetime(2023,4,11).date()
pre_Shet = intro_Shet - timedelta(weeks=1)
post_Shet = intro_Shet + timedelta(weeks=1)

Shet_before = dailysessions_Shet[dailysessions_Shet['Start']<=pre_Shet]
Shet_after = dailysessions_Shet[dailysessions_Shet['Start']>=post_Shet]

###South Lanarkshire
SLan = data2[data2['local_authority']=='South Lanarkshire']

dailysessions_SLan = SLan.groupby('Start').size().reset_index(name='session_count')

##adding daily energy consumed
dailyconsumed_SLan = SLan.groupby('Start')['Consumed(kWh)'].sum().reset_index(name='daily_consumed')

dailysessions_SLan = pd.merge(dailysessions_SLan, dailyconsumed_SLan, on='Start')

##SLan census 2022 population is 327200 people
dailysessions_SLan['Sessionsper100000'] = (dailysessions_SLan['session_count']/327200)*100000
dailysessions_SLan['kWhper100000'] = (dailysessions_SLan['daily_consumed']/327200)*100000

##one week buffer before and after tariff intro to allow for behaviour shift
intro_SLan = datetime(2023,11,1).date()
pre_SLan = intro_SLan - timedelta(weeks=1)
post_SLan = intro_SLan + timedelta(weeks=1)

SLan_before = dailysessions_SLan[dailysessions_SLan['Start']<=pre_SLan]
SLan_after = dailysessions_SLan[dailysessions_SLan['Start']>=post_SLan]

###Stirling
Stir = data2[data2['local_authority']=='Stirling']

dailysessions_Stir = Stir.groupby('Start').size().reset_index(name='session_count')

##adding daily energy consumed
dailyconsumed_Stir = Stir.groupby('Start')['Consumed(kWh)'].sum().reset_index(name='daily_consumed')

dailysessions_Stir = pd.merge(dailysessions_Stir, dailyconsumed_Stir, on='Start')

##Stir census 2022 population is 92600 people
dailysessions_Stir['Sessionsper100000'] = (dailysessions_Stir['session_count']/92600)*100000
dailysessions_Stir['kWhper100000'] = (dailysessions_Stir['daily_consumed']/92600)*100000

##one week buffer before and after tariff intro to allow for behaviour shift
intro_Stir = datetime(2023,2,1).date()
pre_Stir = intro_Stir - timedelta(weeks=1)
post_Stir = intro_Stir + timedelta(weeks=1)

Stir_before = dailysessions_Stir[dailysessions_Stir['Start']<=pre_Stir]
Stir_after = dailysessions_Stir[dailysessions_Stir['Start']>=post_Stir]

###West Dunbartonshire
WDun = data2[data2['local_authority']=='West Dunbartonshire']

dailysessions_WDun = WDun.groupby('Start').size().reset_index(name='session_count')

##adding daily energy consumed
dailyconsumed_WDun = WDun.groupby('Start')['Consumed(kWh)'].sum().reset_index(name='daily_consumed')

dailysessions_WDun = pd.merge(dailysessions_WDun, dailyconsumed_WDun, on='Start')

##WDun census 2022 population is 88400 people
dailysessions_WDun['Sessionsper100000'] = (dailysessions_WDun['session_count']/88400)*100000
dailysessions_WDun['kWhper100000'] = (dailysessions_WDun['daily_consumed']/88400)*100000

##one week buffer before and after tariff intro to allow for behaviour shift
intro_WDun = datetime(2023,6,1).date()
pre_WDun = intro_WDun - timedelta(weeks=1)
post_WDun = intro_WDun + timedelta(weeks=1)

WDun_before = dailysessions_WDun[dailysessions_WDun['Start']<=pre_WDun]
WDun_after = dailysessions_WDun[dailysessions_WDun['Start']>=post_WDun]

###West Lothian
WLot = data2[data2['local_authority']=='West Lothian']

dailysessions_WLot = WLot.groupby('Start').size().reset_index(name='session_count')

##adding daily energy consumed
dailyconsumed_WLot = WLot.groupby('Start')['Consumed(kWh)'].sum().reset_index(name='daily_consumed')

dailysessions_WLot = pd.merge(dailysessions_WLot, dailyconsumed_WLot, on='Start')

##WLot census 2022 population is 181300 people
dailysessions_WLot['Sessionsper100000'] = (dailysessions_WLot['session_count']/181300)*100000
dailysessions_WLot['kWhper100000'] = (dailysessions_WLot['daily_consumed']/181300)*100000

##one week buffer before and after tariff intro to allow for behaviour shift
intro_WLot = datetime(2023,2,1).date()
pre_WLot = intro_WLot - timedelta(weeks=1)
post_WLot = intro_WLot + timedelta(weeks=1)

WLot_before = dailysessions_WLot[dailysessions_WLot['Start']<=pre_WLot]
WLot_after = dailysessions_WLot[dailysessions_WLot['Start']>=post_WLot]

####making a dataframe with all the mean values

LAtariff_dataframes = {
    'Clackmannanshire': {'before': Clackm_before, 'after': Clackm_after},
    'East Dunbartonshire': {'before': EDun_before, 'after': EDun_after},
    'East Renfrewshire': {'before': EastRen2_before, 'after': EastRen2_after},
    'Glasgow City': {'before': Glas_before, 'after': Glas_after},
    'North Lanarkshire': {'before': NLan_before, 'after': NLan_after},
    'Perth and Kinross': {'before': Perth2_before, 'after': Perth2_after},
    'Renfrewshire': {'before': Renf2_before, 'after': Renf2_after},
    'Shetland Islands': {'before': Shet_before, 'after': Shet_after},
    'South Lanarkshire': {'before': SLan_before, 'after': SLan_after},
    'Stirling': {'before': Stir_before, 'after': Stir_after},
    'West Dunbartonshire': {'before': WDun_before, 'after': WDun_after},
    'West Lothian': {'before': WLot_before, 'after': WLot_after}
}

combined_means = []

for LAtariff in LAtariff_dataframes:
    #calculating the mean for the 'before' dataframe
    mean_before = LAtariff_dataframes[LAtariff]['before'].select_dtypes(include='number').mean()

    #calculating the mean for the 'after' dataframe
    mean_after = LAtariff_dataframes[LAtariff]['after'].select_dtypes(include='number').mean()

    #combining the means into a single dataframe
    combined_df = pd.DataFrame({
        'local_authority': [LAtariff, LAtariff],  #area_name gets dynamically filled
        'Time': ['Before', 'After'],
        'session_count': [mean_before['session_count'], mean_after['session_count']],
        'daily_consumed': [mean_before['daily_consumed'], mean_after['daily_consumed']],
        'Sessionsper100000': [mean_before['Sessionsper100000'], mean_after['Sessionsper100000']],
        'kWhper100000': [mean_before['kWhper100000'], mean_after['kWhper100000']]
    })

    #appending combined dataframe to the list
    combined_means.append(combined_df)
    
beforeaftermeans_df = pd.concat(combined_means, ignore_index=True)

###making a dataframe with % differences before and after

#####sessions per 100000

#initialising empty list to store the % differences
delta_sessionsper100000 = []

#finding the unique local authority names
localauthorities = beforeaftermeans_df['local_authority'].unique()

#iterating over each LA
for LA in localauthorities:
    #extracting the 'Before' and 'After' values for sessions per 100000 people
    before_value = beforeaftermeans_df[(beforeaftermeans_df['local_authority'] == LA) & (beforeaftermeans_df['Time'] == 'Before')]['Sessionsper100000'].values[0]
    after_value = beforeaftermeans_df[(beforeaftermeans_df['local_authority'] == LA) & (beforeaftermeans_df['Time'] == 'After')]['Sessionsper100000'].values[0]
    
    #finding the % difference
    percentage_diff = ((after_value - before_value) / before_value) * 100
    
    #appending the result to the list
    delta_sessionsper100000.append({
        'local_authority': LA,
        'Sessionsper100000_Percentage_Diff': percentage_diff
    })

#converting list to dataframe
delta_sessionsper100000_df = pd.DataFrame(delta_sessionsper100000)

#####kWh consumed per 100000

#initialising empty list to store the % differences
delta_kWhper100000 = []

#finding the unique local authority names
localauthorities = beforeaftermeans_df['local_authority'].unique()

#iterating over each LA
for LA in localauthorities:
    #extracting the 'Before' and 'After' values for sessions per 100000 people
    before_value = beforeaftermeans_df[(beforeaftermeans_df['local_authority'] == LA) & (beforeaftermeans_df['Time'] == 'Before')]['kWhper100000'].values[0]
    after_value = beforeaftermeans_df[(beforeaftermeans_df['local_authority'] == LA) & (beforeaftermeans_df['Time'] == 'After')]['kWhper100000'].values[0]
    
    #finding the % difference
    percentage_diff = ((after_value - before_value) / before_value) * 100
    
    #appending the result to the list
    delta_kWhper100000.append({
        'local_authority': LA,
        'kWhper100000_Percentage_Diff': percentage_diff
    })

#converting list to dataframe
delta_kWhper100000_df = pd.DataFrame(delta_kWhper100000)

###############################################################################

####Buffer analysis

######North Lanarkshire CPIDs within 10km buffer
NL_10km = pd.read_excel("CPID_10km_from_North_Lanarkshire_borders.xlsx")

#removing NL
NL_10km_buffer = NL_10km[NL_10km['local_authority']!='North Lanarkshire']
#removing Falkirk and South Lanarkshire as not free
NL_10km_buffer = NL_10km_buffer[NL_10km_buffer['local_authority']!='Falkirk']
NL_10km_buffer = NL_10km_buffer[NL_10km_buffer['local_authority']!='South Lanarkshire']

#merging with session data
NL_10km_buffer = NL_10km_buffer.drop(columns='local_authority')
NL_10km_buffer_sessions = pd.merge(data2, NL_10km_buffer, on='CPID')
#finding number of daily sessions by free chargers within 10k of NL borders
dailysessionsNL_NL_10km_buffer = NL_10km_buffer_sessions.groupby('Start').size().reset_index(name='session_count')

plt.plot(dailysessionsNL_NL_10km_buffer.Start, dailysessionsNL_NL_10km_buffer.session_count, color = '#4059AD')
#plt.xticks(rotation, ha)
plt.xlabel('Date')
plt.ylabel('Number of daily sessions, free chargers \n within 10km of North Lanarkshire borders')
plt.axvline(pd.to_datetime('2023-01-04'), color='black', linestyle='--', lw=2)
plt.annotate('North Lanarkshire Tariff Introduction',xy=(pd.to_datetime('2023-01-15'), 85))
#plt.title('Daily Sessions')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

####Perth and Kinross 10km buffer
Perth_10km = pd.read_excel("CPID_10km_from_Perth_and_Kinross_borders.xlsx")

#Removing Perth and Kinross itself
Perth_10km_buffer = Perth_10km[Perth_10km['local_authority']!='Perth and Kinross']
#removing LAs not free
Perth_10km_buffer = Perth_10km_buffer[Perth_10km_buffer['local_authority']!='Angus']
Perth_10km_buffer = Perth_10km_buffer[Perth_10km_buffer['local_authority']!='Aberdeenshire']
Perth_10km_buffer = Perth_10km_buffer[Perth_10km_buffer['local_authority']!='Highland']
Perth_10km_buffer = Perth_10km_buffer[Perth_10km_buffer['local_authority']!='Argyll and Bute']
Perth_10km_buffer = Perth_10km_buffer[Perth_10km_buffer['local_authority']!='Fife']
Perth_10km_buffer = Perth_10km_buffer[Perth_10km_buffer['local_authority']!='Dundee City']

#merging with session data
Perth_10km_buffer = Perth_10km_buffer.drop(columns='local_authority')
Perth_10km_buffer_sessions = pd.merge(data2, Perth_10km_buffer, on='CPID')
#finding number of daily sessions by free chargers within 10k of Perth borders
dailysessionsPerth_10km_buffer = Perth_10km_buffer_sessions.groupby('Start').size().reset_index(name='session_count')

plt.plot(dailysessionsPerth_10km_buffer.Start, dailysessionsPerth_10km_buffer.session_count, color = '#4059AD')
#plt.xticks(rotation, ha)
plt.xlabel('Date')
plt.ylabel('Number of daily sessions, free chargers \n within 10km of Perth and Kinross borders')
plt.axvline(pd.to_datetime('2023-01-01'), color='black', linestyle='--', lw=2)
plt.annotate('Perth and Kinross Tariff Introduction',xy=(pd.to_datetime('2023-01-11'), 5))
#plt.title('Daily Sessions')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

#####Renfrewshire 10km buffer
Renf_10km = pd.read_excel("CPID_10km_from_Renfrewshire_borders.xlsx")
#removing Renfrewshire and LAs that are not free
Renf_10km_buffer = Renf_10km[Renf_10km['local_authority']!='Renfrewshire']
Renf_10km_buffer = Renf_10km_buffer[Renf_10km_buffer['local_authority']!='Inverclyde']
Renf_10km_buffer = Renf_10km_buffer[Renf_10km_buffer['local_authority']!='Glasgow City']
Renf_10km_buffer = Renf_10km_buffer[Renf_10km_buffer['local_authority']!='Argyll and Bute']
Renf_10km_buffer = Renf_10km_buffer[Renf_10km_buffer['local_authority']!='Stirling']
Renf_10km_buffer = Renf_10km_buffer[Renf_10km_buffer['local_authority']!='South Lanarkshire']

#merging with session data
Renf_10km_buffer = Renf_10km_buffer.drop(columns='local_authority')
Renf_10km_buffer_sessions = pd.merge(data2, Renf_10km_buffer, on='CPID')
#finding daily sessions
dailysessionsRenf_10km_buffer = Renf_10km_buffer_sessions.groupby('Start').size().reset_index(name='session_count')

plt.plot(dailysessionsRenf_10km_buffer.Start, dailysessionsRenf_10km_buffer.session_count, color = '#4059AD')
#plt.xticks(rotation, ha)
plt.xlabel('Date')
plt.ylabel('Number of daily sessions, free chargers \n within 10km of Renfrewshire borders')
plt.axvline(pd.to_datetime('2023-04-01'), color='black', linestyle='--', lw=2)
plt.annotate('Renfrewshire Tariff Introduction',xy=(pd.to_datetime('2023-04-07'), 20))
#plt.title('Daily Sessions')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

###############################################################################

########Charger utilisation

###isolating paid sessions only
data2_paid = data2[data2['Amount']>0]

#finding the total number of sessions recorded for each CPID
sessions_per_CPID_paid = data2_paid.groupby('CPID').size().reset_index(name='session_count')

#finding first appearance of each CPID
first_appearance_CPID_paid = data2_paid.groupby('CPID')['Start'].min().reset_index(name='first_appearance')
#converting to datetime
first_appearance_CPID_paid['first_appearance']=pd.to_datetime(first_appearance_CPID_paid['first_appearance'])
#finding the last appearance of each CPID
last_appearance_CPID_paid = data2_paid.groupby('CPID')['Start'].max().reset_index(name='last_appearance')
#converting to datetime
last_appearance_CPID_paid['last_appearance']=pd.to_datetime(last_appearance_CPID_paid['last_appearance'])

#finding the average number of days between sessions for each CPID
days_between = data2.sort_values(by=['CPID', 'Start'])
#converting to datetime
days_between['Start']=pd.to_datetime(days_between['Start'])
days_between['days_between_sessions'] = days_between.groupby('CPID')['Start'].diff().dt.days
avg_days_between = days_between.groupby('CPID')['days_between_sessions'].mean().reset_index()

#dropping CPIDs with NaN average days between sessions from analysis
avg_days_between = avg_days_between.dropna()

#finding last date in dataset
#print(data2_paid['Start'].max())

#last possible session date
end_date = pd.to_datetime('2024-03-31')

#finding how many days there are between the end of the dataset and each CPID's last appearance
last_appearance_CPID_paid['days_inactive_before_end']=(end_date - last_appearance_CPID_paid['last_appearance']).dt.days

#merging CPID last appearance date, the average days between sessions and days inactive before end date
last_appearance_CPID_paid = pd.merge(last_appearance_CPID_paid, avg_days_between, on='CPID', how='left')
#finding the potential last date if the average number of days between sessions < the number of days between last appearance and end date
last_appearance_CPID_paid['potential_last_active_date'] = last_appearance_CPID_paid['last_appearance'] + pd.to_timedelta(last_appearance_CPID_paid['days_between_sessions'], unit='D')

#If the average number of days between sessions < the number of days between last appearance and end date then potential last active date is applied
#otherwise the last active date is assigned the dataset end date
def calculate_last_active(row):
    if row['days_inactive_before_end'] > row['days_between_sessions']:
        return row['potential_last_active_date']
    else:
        return end_date

last_appearance_CPID_paid['last_active_date'] = last_appearance_CPID_paid.apply(calculate_last_active, axis=1)

#converting from datetime to date
last_appearance_CPID_paid['last_active_date'] = last_appearance_CPID_paid['last_active_date'].dt.date
first_appearance_CPID_paid['first_appearance'] = first_appearance_CPID_paid['first_appearance'].dt.date

#finding the number of days each charger was active, assuming the first appearance was the first possible date the CPID could be used
sessions_per_CPID_paid['total_days_active'] = (last_appearance_CPID_paid['last_active_date'] - first_appearance_CPID_paid['first_appearance']).dt.days
#finding the average number of sessions per CPID
sessions_per_CPID_paid['average_daily_sessions'] = sessions_per_CPID_paid['session_count']/sessions_per_CPID_paid['total_days_active']

#dropping unnecessary columns and sorting CPIDs from most utilised to least
avgsessions_CPID_paid = sessions_per_CPID_paid.drop(columns=['session_count', 'total_days_active'])
avgsessions_CPID_paid = avgsessions_CPID_paid.sort_values(by='average_daily_sessions', ascending=False)
#dropping divisions by zero (six CPIDs had 0 total days active)
avgsessions_CPID_paid = avgsessions_CPID_paid.drop([1944,592,1404,2135,2050,33])

#merging charger characteristics
avgsessions_CPID_paid = pd.merge(avgsessions_CPID_paid, UR8class, on='CPID', how='left')
avgsessions_CPID_paid = pd.merge(avgsessions_CPID_paid, SIMD, on='CPID', how='left')
avgsessions_CPID_paid = pd.merge(avgsessions_CPID_paid, GAcc, on='CPID', how='left')
avgsessions_CPID_paid = pd.merge(avgsessions_CPID_paid, ChargerID, on='CPID', how='left')
avgsessions_CPID_paid = pd.merge(avgsessions_CPID_paid, postcodes, on='CPID', how='left')
avgsessions_CPID_paid = pd.merge(avgsessions_CPID_paid, ChargerSpeeds, on='CPID', how='left')

#splitting into AC and rapid/ultra-rapid dataframes
avgsessions_CPID_paid_AC = avgsessions_CPID_paid[avgsessions_CPID_paid['Connector_Type']=='AC']
avgsessions_CPID_paid_Rapid = avgsessions_CPID_paid[avgsessions_CPID_paid['Connector_Type'].isin(['Rapid', 'Ultra-Rapid'])]

#isolating chargers used at least once a day
ACpaid_1 = avgsessions_CPID_paid_AC[avgsessions_CPID_paid_AC.average_daily_sessions>=1]
Rapidpaid_1 = avgsessions_CPID_paid_Rapid[avgsessions_CPID_paid_Rapid.average_daily_sessions>=1]

#combining both donuts in one figure
labels = ['Used on average \n at least once a day', 'Used on average \n less than once a day']
sizes1 = [35, 65]
sizes2 = [86, 14]
colors = ['#00CC99','#CC0066']

fig, axes = plt.subplots(1, 2, figsize=(12, 6)) 

#plot 1
plt.sca(axes[0]) 
axes[0].pie(sizes1, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=90, labeldistance=1.1, textprops={'fontsize': 14})
centre_circle1 = plt.Circle((0, 0), 0.70, fc='white')
fig.gca().add_artist(centre_circle1)
axes[0].axis('equal') 
axes[0].set_title('AC Chargers', fontsize=20)

#plot 2
plt.sca(axes[1]) 
axes[1].pie(sizes2, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=90, labeldistance=1.1, textprops={'fontsize': 14})
centre_circle2 = plt.Circle((0, 0), 0.70, fc='white')
fig.gca().add_artist(centre_circle2)
axes[1].axis('equal')  
axes[1].set_title('Rapid/Ultra-Rapid Chargers', fontsize=20)

#avoiding overlapping
plt.tight_layout()

plt.show()

#############top 5% most used chargers

###Rapid

#setting top 5% cutoff
cutoffRapid = avgsessions_CPID_paid_Rapid['average_daily_sessions'].quantile(0.95)
#finding top 5% most utilised chargers on average
top5_Rapid = avgsessions_CPID_paid_Rapid[avgsessions_CPID_paid_Rapid['average_daily_sessions'] >= cutoffRapid]

top5_Rapid_UR = top5_Rapid.groupby('UR8Class')['CPID'].nunique().reset_index()

top5_Rapid_UR = top5_Rapid_UR.sort_values(by='UR8Class').reset_index(drop=True)

missing_data = pd.DataFrame({
    'UR8Class': [4, 5, 7, 8],
    'CPID': [0, 0, 0, 0]
})
top5_Rapid_UR = pd.concat([top5_Rapid_UR, missing_data], ignore_index=True)
top5_Rapid_UR = top5_Rapid_UR.sort_values(by='UR8Class').reset_index(drop=True)

ax=top5_Rapid_UR.plot.bar(x='UR8Class', y='CPID', rot=0, legend=False, color='xkcd:sky blue')
plt.xlabel('Urban Rural Classification')
plt.ylabel('Number of chargers within the top 5% \n most utilised Rapid/Ultra-Rapid Chargers \n on average')
plt.subplots_adjust(bottom=0.22)

#adding urban/rural labels under x-axis outwith chart area
ax.figure.text(0.15, 0.09, 'Urban', ha='center', va='center')
ax.figure.text(0.85, 0.09, 'Rural', ha='center', va='center')

#adding the double headed arrow
ax.annotate(
    '', xy=(0.075, -0.24), xytext=(0.9, -0.24),
    xycoords='axes fraction', textcoords='axes fraction',
    arrowprops=dict(arrowstyle='<->', color='black')
)

plt.show()

#assigning SIMD quintiles
top5_RapidSIMD = top5_Rapid.copy()
top5_RapidSIMD['Rankv2_quintile'] = top5_RapidSIMD['Rankv2'].apply(assign_quintile)
#finding and plotting the number of top 5% chargers found in each SIMD quintile
top5_RapidSIMD = top5_RapidSIMD.groupby('Rankv2_quintile')['CPID'].nunique().reset_index()

ax=top5_RapidSIMD.plot.bar(x='Rankv2_quintile', y='CPID', rot=0, legend=False, color='xkcd:sky blue')
plt.xlabel('Scottish Index of Multiple Deprivation Quintile')
plt.ylabel('Number of chargers within the top 5% \n most utilised Rapid/Ultra-Rapid Chargers \n on average')
plt.subplots_adjust(bottom=0.22)

#adding urban/rural labels under x-axis outwith chart area
ax.figure.text(0.15, 0.09, 'More Deprived', ha='center', va='center')
ax.figure.text(0.85, 0.09, 'Less Deprived', ha='center', va='center')

#adding the double headed arrow
ax.annotate(
    '', xy=(0.075, -0.24), xytext=(0.9, -0.24),
    xycoords='axes fraction', textcoords='axes fraction',
    arrowprops=dict(arrowstyle='<->', color='black')
)

plt.show()

#same for GA index
top5_RapidGAcc = top5_Rapid.copy()
top5_RapidGAcc['GAccRank_quintile'] = top5_RapidGAcc['GAccRank'].apply(assign_quintile)
#finding and plotting the number of top 5% chargers found in each SIMD quintile
top5_RapidGAcc = top5_RapidGAcc.groupby('GAccRank_quintile')['CPID'].nunique().reset_index()

ax=top5_RapidGAcc.plot.bar(x='GAccRank_quintile', y='CPID', rot=0, legend=False, color='xkcd:sky blue')
plt.xlabel('Geographical Accessibility Quintile')
plt.ylabel('Number of chargers within the top 5% \n most utilised Rapid/Ultra-Rapid Chargers \n on average')
plt.subplots_adjust(bottom=0.22)

#adding urban/rural labels under x-axis outwith chart area
ax.figure.text(0.15, 0.09, 'Less Accessible', ha='center', va='center')
ax.figure.text(0.85, 0.09, 'More Accessible', ha='center', va='center')

#adding the double headed arrow
ax.annotate(
    '', xy=(0.075, -0.24), xytext=(0.9, -0.24),
    xycoords='axes fraction', textcoords='axes fraction',
    arrowprops=dict(arrowstyle='<->', color='black')
)

plt.show()

###AC

#setting top 5% cutoff
cutoffAC = avgsessions_CPID_paid_AC['average_daily_sessions'].quantile(0.95)
#finding top 5% most utilised chargers on average
top5_AC = avgsessions_CPID_paid_AC[avgsessions_CPID_paid_AC['average_daily_sessions'] >= cutoffAC]

top5_AC_UR = top5_AC.groupby('UR8Class')['CPID'].nunique().reset_index()

#adding in the UR Class without top 5% chargers and sorting for plot
missing_data2 = pd.DataFrame({
    'UR8Class': [4, 5],
    'CPID': [0, 0]
})
top5_AC_UR = pd.concat([top5_AC_UR, missing_data2], ignore_index=True)
top5_AC_UR = top5_AC_UR.sort_values(by='UR8Class').reset_index(drop=True)

ax=top5_AC_UR.plot.bar(x='UR8Class', y='CPID', rot=0, legend=False, color='#6600CC')
plt.xlabel('Urban Rural Classification')
plt.ylabel('Number of chargers within the top 5% \n most utilised AC chargers on average')
plt.subplots_adjust(bottom=0.22)

#adding urban/rural labels under x-axis outwith chart area
ax.figure.text(0.15, 0.09, 'Urban', ha='center', va='center')
ax.figure.text(0.85, 0.09, 'Rural', ha='center', va='center')

#adding the double headed arrow
ax.annotate(
    '', xy=(0.075, -0.24), xytext=(0.9, -0.24),
    xycoords='axes fraction', textcoords='axes fraction',
    arrowprops=dict(arrowstyle='<->', color='black')
)
plt.show()

#assigning SIMD quintiles
top5_ACSIMD = top5_AC.copy()
top5_ACSIMD['Rankv2_quintile'] = top5_ACSIMD['Rankv2'].apply(assign_quintile)
#finding and plotting the number of top 5% chargers found in each SIMD quintile
top5_ACSIMD = top5_ACSIMD.groupby('Rankv2_quintile')['CPID'].nunique().reset_index()

ax=top5_ACSIMD.plot.bar(x='Rankv2_quintile', y='CPID', rot=0, legend=False, color='#6600CC')
plt.xlabel('Scottish Index of Multiple Deprivation Quintile')
plt.ylabel('Number of chargers within the top 5% \n most utilised AC Chargers on average')
plt.subplots_adjust(bottom=0.22)

#adding urban/rural labels under x-axis outwith chart area
ax.figure.text(0.15, 0.09, 'More Deprived', ha='center', va='center')
ax.figure.text(0.85, 0.09, 'Less Deprived', ha='center', va='center')

#adding the double headed arrow
ax.annotate(
    '', xy=(0.075, -0.24), xytext=(0.9, -0.24),
    xycoords='axes fraction', textcoords='axes fraction',
    arrowprops=dict(arrowstyle='<->', color='black')
)

plt.show()

#same for GA index
top5_ACGAcc = top5_AC.copy()
top5_ACGAcc['GAccRank_quintile'] = top5_ACGAcc['GAccRank'].apply(assign_quintile)
#finding and plotting the number of top 5% chargers found in each SIMD quintile
top5_ACGAcc = top5_ACGAcc.groupby('GAccRank_quintile')['CPID'].nunique().reset_index()

ax=top5_ACGAcc.plot.bar(x='GAccRank_quintile', y='CPID', rot=0, legend=False, color='#6600CC')
plt.xlabel('Geographical Accessibility Quintile')
plt.ylabel('Number of chargers within the top 5% \n most utilised AC Chargers on average')
plt.subplots_adjust(bottom=0.22)

#adding urban/rural labels under x-axis outwith chart area
ax.figure.text(0.15, 0.09, 'Less Accessible', ha='center', va='center')
ax.figure.text(0.85, 0.09, 'More Accessible', ha='center', va='center')

#adding the double headed arrow
ax.annotate(
    '', xy=(0.075, -0.24), xytext=(0.9, -0.24),
    xycoords='axes fraction', textcoords='axes fraction',
    arrowprops=dict(arrowstyle='<->', color='black')
)
plt.show()

###############################################################################