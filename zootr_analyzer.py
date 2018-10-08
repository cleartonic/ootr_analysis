# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 17:34:46 2018

@author: cleartonic
"""

import pandas as pd
import numpy as np
import os
import re
import pickle

MAIN_DIR = os.getcwd()

###############
# CLASSES
###############

class Seed:
    def __init__(self, seed, check_dict, req_dict, settings):
        # Seed = seed
        # items = dictionary of 1:1 items by check e.g. [{'Mido Chest Top Left':'Bow'}]. from DISTRIBUTION
        # Settings = settings for seed - fast ganon, etc. 
        
        self.seed = seed
        self.check_dict = check_dict
        self.req_dict = req_dict
        self.settings = settings
        
    def filter_checklist(self,filter_list):
        self.output_checks = { your_key: self.check_dict[your_key] for your_key in filter_list }
        

    def filter_rewardlist(self,filter_list):
        self.output_rewards = {k:v for k, v in self.check_dict.items() if v in filter_list}
        
        
        
###############
# FUNCTIONS
###############        

def filter_dict(input_dict, filter_str, filter_type):
    # Arguments: dictionary, filter string, filter_type
    # filter_type = eiter keys or values of the dictionary
    # returns a LIST
    if filter_type == 'keys':
        return list({k: v for k, v in input_dict.items() if filter_str in k })
    elif filter_type == 'vals':
        return list({k: v for k, v in input_dict.items() if filter_str in v })
    else:
        print("Error on filter_type.")
        return None
    
    
#############
# SEED HANDLER
#############
        
# If you have a SEED string, use this function to find the matching Seed class:
        
def find_seed(seed_str):
    for seed in seed_list:
        if seed.name == seed_str:
            return seed


#################
# DATA LOADER/INIT
#################

# Lookups
check_lookup = pd.read_csv('check_lookup.csv',index_col='check')
reward_lookup = pd.read_csv('reward_lookup.csv',index_col='reward')


# Create dictionaries from lookups
check_dict = check_lookup.to_dict()
check_dict = check_dict['requirements']

reward_dict = reward_lookup.to_dict()
reward_dict_unique = reward_lookup['unique']
reward_dict_critical = reward_lookup['critical']
reward_dict_important = reward_lookup['important']



# Create lists 
reward_important = filter_dict(reward_dict_important, 'y', 'vals')
reward_critical = filter_dict(reward_dict_critical, 'y', 'vals')
reward_unique = filter_dict(reward_dict_unique, 'y', 'vals')
reward_allarrows = ['Bow','Fire Arrows','Ice Arrows','Light Arrows','Magic Meter']

check_deku = filter_dict(check_dict, 'Deku Tree', 'keys')
check_dc = filter_dict(check_dict, 'Dodongos Cavern', 'keys')
check_jabu = filter_dict(check_dict, 'Jabu Jabu', 'keys')
check_forest = filter_dict(check_dict, 'Forest Temple', 'keys')
check_fire = filter_dict(check_dict, 'Fire Temple', 'keys')
check_water = filter_dict(check_dict, 'Water Temple', 'keys')
check_shadow = filter_dict(check_dict, 'Shadow Temple', 'keys')
check_spirit = filter_dict(check_dict, 'Spirit Temple', 'keys')
check_well = filter_dict(check_dict, 'Bottom of the Well', 'keys')
check_gtg = filter_dict(check_dict, 'Gerudo Training Grounds', 'keys')
check_ice = filter_dict(check_dict, 'Ice Cavern', 'keys')
check_ganons = filter_dict(check_dict, 'Ganons Castle', 'keys')

check_bossheart = filter_dict(check_dict, 'Heart', 'keys') # Needs to be fixed, Piece of Heart appears

check_noreqs = filter_dict(check_dict, 'No req', 'vals')
check_reqs = filter_dict(check_dict, 'Reqs', 'vals')
check_songs = filter_dict(check_dict, 'Song', 'vals')

check_worst = ['30 Gold Skulltulla Reward','40 Gold Skulltulla Reward','50 Gold Skulltulla Reward','Deku Theater Mask of Truth','Biggoron','Adult Fishing','Child Fishing','Horseback Archery 1000 Points','Horseback Archery 1500 Points']


# Other
mst = ['Forest Medallion','Fire Medallion','Water Medallion','Shadow Medallion','Spirit Medallion','Light Medallion','Kokiri Emerald','Goron Ruby','Zora Sapphire']
dungeon_dict = {'Queen Gohma':'Deku','King Dodongo':'Dodongo','Barinade':'Jabu','Phantom Ganon':'Forest','Volvagia':'Fire','Morpha':'Water','Bongo Bongo':'Shadow','Twinrova':'Spirit'}






os.chdir('../zootr_dev_9.27.18/Output/combined/')

# Distribution
if False:
    df_dist = pd.read_csv('data_dist.csv')
    df_dist = df_dist.join(check_lookup,on='check')
    df_dist = df_dist.join(reward_lookup,on='reward')

# Required items only
if False:
    df_req = pd.read_csv('data_req.csv')
    
# Seed classes    
if True:
    seed_list = pickle.load(open("saved_seeds.p", "rb"))

os.chdir(MAIN_DIR)






# DATA CLEANER/PREPARER

    
    
    
########################
# Create mst mapping for seeds. This takes the playthrough data and returns a pivot of each seeds' counts per required dungeons
########################
if False:
    
    os.chdir('../zootr_dev_9.27.18/Output/combined')

    df = pd.read_csv('data_play.csv')
    df_mst = pd.DataFrame() # will store the seeds per mst type, be used as lookup for original df
    
    num = 0
    for seed in df['SEED'].unique().tolist():
        print("Processing "+str(num)+"...")

        # df_temp = df[(df['SEED'] == seed)&(df['reward'].isin(mst))&(df['check']!='Links Pocket')]
        df_temp = df[df['SEED'] == seed]
        df_temp = df_temp[df_temp['reward'].isin(mst)]
        df_temp = df_temp[df_temp['check']!='Links Pocket']
        

        required_mst = df_temp['check'].unique().tolist()
        
        
        # You are looking up the BOSS based on the MEDALLION you get, then figuring out the TEMPLE
        # I.e Gohma giving you light medallion
        # Check for what Light Medallion's CHECK is (Gohma)
        # Then return Gohma -> Deku Tree
        
        if len(required_mst) > 7:
            seed_length = 'all_dungeons'
        else:
            seed_length = 'medallions'
        mst_list = ''
        for mst_item in sorted(required_mst):
            mst_item = dungeon_dict[mst_item]
            mst_list = mst_list+' '+mst_item    
        mst_list = mst_list.strip()
        df_append = pd.DataFrame({"REQUIRED_MST":mst_list,"SEED_LENGTH":seed_length},index=[seed])
        df_mst = df_mst.append(df_append)
        num = num + 1
            
    
    # Join df_mst mappings to df, save files 
    df = df.join(df_mst,on='SEED')
    df.to_csv('data_play_mst.csv',index=None)
    df_pivot = df.pivot_table(index=['check','reward'],columns=['REQUIRED_MST'],values='count',aggfunc=np.sum).fillna(0)
    df_pivot.to_csv('test.csv')
    df_mst['count'] = 1
    
    # Want to call the first col here "SEED", but saves without?
    df_mst.to_csv('data_play_mst_mapping.csv')
    df_mst_pivot = df_mst.pivot_table(index='REQUIRED_MST',values='count',aggfunc=np.sum)
    df_mst_pivot.to_csv('data_play_mst_mapping_pivot.csv')
    
    
    








# ANALYSIS
    
    
########################
# Dungeon distribution (A/B for dungeon in / not in seed)
########################    
if False:
    os.chdir('../zootr_dev_9.27.18/Output/combined')
    
    
    if False:   # # # By required items log
        # Read the REQUIRED items, not the playthru (playthru used to generate the dungeon lists, found in data_play_mst_mapping_pivot)
        df = pd.read_csv('data_req.csv')
        df['seed'] = df['seed'].str.replace("req_","play_")  # This allows us to lookup to the play logs
        
        # data_play_mst_mapping holds the seed → dungeon layout lookup
        # If "SEED" throws error, then open file and add column header 
        
        df_lookup = pd.read_csv('data_play_mst_mapping.csv')
        df_lookup = df_lookup.set_index('SEED')
        df_lookup = df_lookup[['REQUIRED_MST','SEED_LENGTH']] #only want this value for lookup
        
        df = df.join(df_lookup,on='seed')
        
        
        # Pivot built off of required df, with lookup to required mst dungeons
        df_pivot = df.pivot_table(index=['check'],columns='REQUIRED_MST',values='count',aggfunc=np.sum)
    
    
    if True:  # # # By playthrough log
        df = pd.read_csv('data_play_mst.csv')
        df_pivot = df.pivot_table(index=['check'],columns='REQUIRED_MST',values='count',aggfunc=np.sum)
        
        
    # Make pivot by CHECK only
    #df_pivot.drop('REWARD',axis=1,inplace=True)
    #df_pivot = df_pivot.pivot_table(index=['CHECK'],aggfunc=np.sum)
    
    
    # Filter out all dungeons
    df_pivot.drop('Jabu Shadow Dodongo Water Forest Deku Spirit Fire',axis=1,inplace=True)
    
    
    # Loads the lookup table for count of each dungeon spread (e.g. "Deku Fire Water Spirit Shadow | 450")
    df_mst_pivot = pd.read_csv('data_play_mst_mapping_pivot.csv')
    df_mst_pivot.set_index('REQUIRED_MST',inplace=True)

    for mst_loc in list(dungeon_dict.values()): # For fire/water/forest... including stones
        print("Processing "+mst_loc+"...")
        list_match = []
        list_nonmatch = []
        for col in df_pivot.columns.tolist():
            if mst_loc in col:
                list_match.append(col)
            else:
                list_nonmatch.append(col)
                
        list_match_sum = df_mst_pivot.loc[list_match].sum()[0]
        list_nonmatch_sum = df_mst_pivot.loc[list_nonmatch].sum()[0]
        
        df_pivot['sum_match'] = df_pivot[list_match].sum(axis=1) / list_match_sum
        df_pivot['sum_nonmatch'] = df_pivot[list_nonmatch].sum(axis=1) / list_nonmatch_sum
        
        df_pivot_out = df_pivot[['sum_match','sum_nonmatch']]
        df_pivot_out.columns = ['sum_match_'+mst_loc,'sum_nonmatch_'+mst_loc]
        df_pivot_out['delta_'+mst_loc] = df_pivot_out['sum_match_'+mst_loc] - df_pivot_out['sum_nonmatch_'+mst_loc]
        # Remove GS
        df_pivot_out.index = df_pivot_out.index.astype('str')
        df_pivot_out = df_pivot_out[df_pivot_out.index.str.contains("GS") == False]
    
        df_pivot_out.sort_values(by='delta_'+mst_loc,ascending=False,inplace=True)        
        df_pivot_out = df_pivot_out.round(2)        
        df_pivot_out.to_csv('mst_match_'+mst_loc+'.csv')

    
    
#####################
# SEED FINDER
#####################
        
# Use distribution with joined check/reward lookups
# Uses Seed CLASS, not dfs

# See if any seeds have 4 important/critical/unique checks in all of Mido's
if False:
    num = 0
    reward_important = ['Progressive Hookshot','Progressive Strength Upgrade','Hammer','Bottle with Letter','Boomerang','Dins Fire','Light Arrows','Iron Boots','Hover Boots','Mirror Shield','Magic Meter','Bow']
    match_list = []
    for seed in seed_list:
        mido_tl = seed.check_dict['Mido Chest Top Left']
        mido_bl = seed.check_dict['Mido Chest Bottom Left']
        mido_tr = seed.check_dict['Mido Chest Top Right']
        mido_br = seed.check_dict['Mido Chest Bottom Right']
        # print("Processing "+str(num),"Check "+mido_tl,mido_tr,mido_bl,mido_br)
        # print("Processing "+str(num))
        num = num + 1
        if mido_tl in reward_important and mido_tr in reward_important and mido_bl in reward_important and mido_br in reward_important:
            print("All match on seed "+seed.name)
            match_list.append(seed)




if True:
    num = 0
    
    # Playground - mess with parameters for how for loop works, what scoring is, etc. 
    score_list = {}  # dict of seed, score
    for seed in seed_list:
        # print("Processing "+str(num))
        num = num + 1
        score = 0
        
        # Checking requirements for critical/important/unique
#        for check_noreq in check_list_noreqs.keys():
#            if seed.check_dict[check_noreq] in reward_critical:
#                score = score + 1
                
         
        # Define check list by specific matching:
        
        check_list = list(set(check_deku + check_dc +check_noreqs))
        
        for check in seed.check_dict.keys():
            if check in check_list:
                temp_check = seed.check_dict[check]
                if temp_check in reward_critical:
                    score = score + 1
                
        score_list[seed.name] = score
                
        
        # Add lists to seeds
        seed.filter_checklist(check_list)
        seed.filter_rewardlist(reward_critical)
    
        
        
        
    # Standardized output 
    df = pd.DataFrame(pd.Series(score_list))
    df.columns = ['val']
    df['count'] = 1
    df_pivot = df.pivot_table(index=['val',df.index],values=['count'],aggfunc=np.sum)
    print(df_pivot)
    df_pivot_final = df.pivot_table(index=['val'],values=['count'],aggfunc=np.sum)
    print(df_pivot_final)



    # Highest and lowest scoring groups put into seed list
    seeds_high = []
    seeds_low = []
    df_pivot.reset_index(inplace=True)
    max_score = df_pivot['val'].unique().max()
    min_score = df_pivot['val'].unique().min()
    
    seeds_high_str = df_pivot[df_pivot['val']==max_score]['level_1'].unique().tolist()
    seeds_low_str = df_pivot[df_pivot['val']==min_score]['level_1'].unique().tolist()
    
    for seed_str in seeds_high_str:
        seeds_high.append(find_seed(seed_str))
    for seed_str in seeds_low_str:
        seeds_low.append(find_seed(seed_str))    
    












