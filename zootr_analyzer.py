# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 17:34:46 2018

@author: cleartonic
"""

import pandas as pd
import numpy as np
import os
import random
import pickle
import time

MAIN_DIR = os.getcwd()
RENDER_TIME = str(int(time.time()))
ASSIGN_CLASS_MODIFICATIONS = False
PICKLE_LOAD = False
LOAD_DIST = True
LOAD_REQ = False
LOAD_PLAY = False
LOAD_GOMODE = False
LOAD_SEED_CLASSES = True

pd.options.display.max_rows = 100
pd.options.display.max_columns = 10


# TO DO 
# Create filter on play_map for Small / Boss Keys, Kokiri Shop


###############
# CLASSES
###############

class Seed:
    def __init__(self, seed, check_dict, req_dict, play_dict, mst_map, length, settings):
        # Seed = seed
        # items = dictionary of 1:1 items by check e.g. [{'Mido Chest Top Left':'Bow'}]. from DISTRIBUTION
        # Settings = settings for seed - fast ganon, etc. 
        
        self.name = seed
        self.check_dict = check_dict
        self.req_dict = req_dict
        self.play_dict = play_dict
        self.mst = mst_map
        self.length = length
        self.settings = settings

   
        
        # Clean play_dict into a map without Gold Skulltulas
        
        self.play_map = {}
        temp_play_dict = {k: v for k, v in self.play_dict.items() if "GS" not in k }
        temp_play_dict = {k: v for k, v in temp_play_dict.items() if "Key" not in v }
        num = 0
        for item in temp_play_dict:
            self.play_map[num] = {item:temp_play_dict[item]}
            num = num + 1
        
        # Create gomode_mst mapping (step 1):
        
        list_of_mst = self.mst.split(" ")
        gomode_list = []
        for mst in list_of_mst:
            for item in go_mode_dict[mst]:
                gomode_list.append(item)
        for item in go_mode_dict['All']:
            gomode_list.append(item)
        gomode_list = list(set(gomode_list))
        if "Water" in self.mst:
            gomode_list.append('Progressive Hookshot')
        if "Spirit" in self.mst:
            gomode_list.append('Progressive Strength Upgrade')
        self.gomode_items = gomode_list
        self.gomode_mst_dict = {k:v for k, v in self.check_dict.items() if v in gomode_list}

        # create songs
        self.filter_checklist(songs)
        self.songs_dict = self.output_checks

        # Create final gomode mapping (step 2):
        
        check_ranks = check_lookup[['requirements','rank']].to_dict()['rank']
        w = self.gomode_items.copy() # list of gomode items
        y = self.req_dict.copy()
        y_values = sorted(list(y.values()).copy())   # the req dict's existing values

        # Specific clause for hookshot/scale/strength. If these are in the playthru log MORE than the required_items dict, then they need to be manually added to gomode items
        problem_items = ['Progressive Strength Upgrade','Progressive Scale','Progressive Hookshot']
        for item in problem_items:
            num1 = w.count(item)
            num2 = y_values.count(item)
            num3 = list(self.play_dict.values()).count(item)
            max_num = max(num1,num2,num3)
            if max_num > num1:
                w.append(item)        
                
        final_dict = self.req_dict.copy() # Final_dict will start with at least what's in req_dict
        for reward in y_values:
            if reward in w:
                w.remove(reward)
                

        # With a list via missing_items, we need to update the req_dict until it has at least everything in the gomode dict. 
        for item in w:
            #print("-------------------")
            #print("CHECKING ITEM "+item)
            # For each item in the missing list, now find a matching dictionary entry for the reward. 
            # Then see if its in final_dict. If it isnt, good, add it. If not, keep searching
            
            list_of_checks = filter_dict(self.check_dict,item,'vals') # returns a list of matching checks for that item
            #print("LIST OF CHECKS: "+' | '.join(list_of_checks))
            
            local_rank = {}
            for check in list_of_checks: # look at each check
                local_rank[check] = check_ranks[check]
            list_of_checks = pd.DataFrame.from_dict(local_rank,orient='index').sort_values(0).index.tolist()  # this is a convoluted way of sorting the dictionary by values, using a dataframe and returning an ordered list

            for check in list_of_checks: # look at each check              
                #print("Check "+check,"Rank "+str(local_rank[check]))
                if check in final_dict.keys(): # if its already in the list, then keep searching the others 
                    #print("Check "+check+" already in dict, pass.")
                    pass  
                else:        # Assign highest scoring rank
                    #print("Check "+check+" assigned.")
                    final_dict[check] = item
                    break
        self.gomode_dict = final_dict
            
    def filter_checklist(self,filter_list):
        self.output_checks = { your_key: self.check_dict[your_key] for your_key in filter_list }
    def filter_rewardlist(self,filter_list):
        self.output_rewards = {k:v for k, v in self.check_dict.items() if v in filter_list}
        
    def filter_gomode_checks(self,filter_list):
        self.output_checks = { your_key: self.gomode_dict[your_key] for your_key in filter_list }
    def filter_gomode_rewards(self,filter_list):
        self.output_rewards = {k:v for k, v in self.gomode_dict.items() if v in filter_list}
        
    def info(self):
        print("-----")
        print("Distribution:")
        for item in self.check_dict:            
            print('{:.55}'.format('{:55}'.format("  "+item+": "))+" "+self.check_dict[item])
        print("-----")
        print("Songs:")
        for item in self.songs_dict:
            print('{:.55}'.format('{:55}'.format("  "+item+": "))+" "+self.songs_dict[item])
        print("-----")
        print("Playthrough:")
        for item in self.play_map:
            print('{:.55}'.format('{:55}'.format("  "+str(item)+" "
                            +str(list(self.play_map[item].keys())[0])))
                            +" "
                            +str(list(self.play_map[item].values())[0]))
        print("-----")
        print("Required Items:")
        for item in self.req_dict:
            print('{:.55}'.format('{:55}'.format("  "+item+": "))+" "+self.req_dict[item])
        print("-----")
        print("Go Mode checks (refined from required items):")
        gomode_temp = sorted(self.gomode_dict.items(), key=lambda x: x[1])
        for item in gomode_temp:
            print('{:.55}'.format('{:55}'.format("  "+item[0]+": "))+" "+item[1])
        print("-----")
        print('{:.55}'.format('{:55}'.format("Seed: "))+self.name)
        print('{:.55}'.format('{:55}'.format("Length: "))+self.length)
        print('{:.55}'.format('{:55}'.format("Dungeons: "))+self.mst)        
        
        
        
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
    
    
def filter_check_rank(rank_num):
    # Arguments: dictionary, filter string, filter_type
    # filter_type = eiter keys or values of the dictionary
    # returns a LIST
    if rank_num > 10:
        print("Error on rank num. Use an integer less than 11.")
    else:
        return list(check_lookup[check_lookup['rank']==rank_num].index)

    
def filter_seedlist(original_seed_list, filter_method_list):
    # Arguments: Original seed list
    
    # filter_method = 'mst' - returns seed_list with matching MST contents
    # MANUAL for now
    
    if 'mst' in filter_method_list:
        new_seed_list = []
        for seed in original_seed_list:
            if 'Deku' in seed.mst and 'Water' in seed.mst and 'Dodongo' in seed.mst and 'Forest' in seed.mst and 'Spirit' in seed.mst and 'Shadow' not in seed.mst and 'Fire' not in seed.mst and 'Jabu' not in seed.mst:
                if 'Jabu Shadow Dodongo Water Forest Deku Spirit Fire' not in seed.mst: # Not all dungeons
                    new_seed_list.append(seed)
        original_seed_list = new_seed_list[:] # Update for future arguments in this function to use the curated new list

    # filter_method = 'no-mismatch-dungeons' - any dungeons with playthru items that are NOT in the mst are take nout
    if 'no-mismatch-dungeons' in filter_method_list:
        new_seed_list = []
        # Get list of missing dungeons
        all_dungeons =  ['Dodongo', 'Water', 'Forest', 'Deku', 'Spirit', 'Fire', 'Shadow', 'Jabu']
        seed_dungeons = seed.mst.split(" ")
        nonseed_dungeons = []
        for dungeon in all_dungeons:
            if dungeon not in seed_dungeons:
                nonseed_dungeons.append(dungeon)
        
        for seed in original_seed_list:
            list_of_reqs = list(seed.req_dict.keys())
            pass_check = True                   # This becomes false if there's a nonseed dungeon in the reqs
            for dungeon in nonseed_dungeons:
                for req in list_of_reqs:
                    if dungeon in req:
                        pass_check = False
                    else:
                        pass
            if pass_check:
                new_seed_list.append(seed) # If it doesnt match any req for the non-seed dungeon, then include in list
        original_seed_list = new_seed_list[:] # Update for future arguments in this function to use the curated new list
    
    
    return new_seed_list

# Func to stringify 'multiple' metric
def apply_multiple(x):
    x = round(x,2) + 1
    x = str(x)[0:3] + "x"
    return x

# Func to stringify 'multiple' metric based on 2 columns
def apply_multiple_2(x,y):
    try:
        z = x/y
        z = round(z,2) + 1
        z = str(z)[0:3] + "x"
    except:
        z = 'n/a'
    return z

# Func for applying song # 
def apply_songcount(x,y):
    if x == 0:
        return 0
    else:
        return y



def call_random_seed():    
    local_seed = seed_list[random.randint(0,len(seed_list))] # test seed
    local_seed.info()
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
go_mode_dict = {'Deku':['Slingshot'],
                'Dodongo':['Progressive Strength Upgrade','Bomb Bag'],
                'Jabu':['Bottle with Letter','Boomerang'],
                'Forest':['Progressive Strength Upgrade','Bow','Progressive Hookshot'],
                'Fire':['Progressive Strength Upgrade','Bomb Bag','Hammer'],
                'Water':['Progressive Strength Upgrade','Iron Boots','Bow','Progressive Hookshot'],
                'Shadow':['Progressive Strength Upgrade','Zeldas Lullaby','Bow','Magic Meter','Progressive Hookshot','Hover Boots','Lens of Truth','Dins Fire'],
                'Spirit':['Progressive Strength Upgrade','Zeldas Lullaby','Bow','Progressive Hookshot','Mirror Shield'],
                'All':['Bow','Magic Meter','Light Arrows']}
songs = ['Impa at Castle','Song from Malon','Song from Saria','Song at Windmill','Song from Composer Grave','Sheik Forest Song','Sheik at Temple','Sheik at Colossus','Sheik in Crater','Sheik in Ice Cavern','Sheik in Kakariko','Song from Ocarina of Time']
songs_rewards = ["Bolero of Fire","Eponas Song","Minuet of Forest","Nocturne of Shadow","Prelude of Light","Requiem of Spirit","Sarias Song","Serenade of Water","Song of Storms","Song of Time","Suns Song","Zeldas Lullaby"]


if PICKLE_LOAD:
    print("Loading saved pickle file...")
    df_dist, df_gomode, df_play, df_req, seed_list = pickle.load(open('latest_build/Output/combined/saved_analysis_files.p', "rb"))
    

if LOAD_DIST:
    os.chdir('latest_build/Output/combined/')
    print("Loading dist...")
    # Distribution
    df_dist = pd.read_csv('data_dist.csv')
    df_dist = df_dist.join(check_lookup,on='check')
    df_dist = df_dist.join(reward_lookup,on='reward')
    os.chdir(MAIN_DIR)    
    
if LOAD_REQ:
    # Required items only
    os.chdir('latest_build/Output/combined/')
    print("Loading req...")    
    df_req = pd.read_csv('data_req.csv')
    os.chdir(MAIN_DIR)
if LOAD_PLAY:    
    # Playthrough only
    os.chdir('latest_build/Output/combined/')
    print("Loading play...")
    df_play = pd.read_csv('data_play.csv')
    os.chdir(MAIN_DIR)
    
if LOAD_GOMODE:    
    # Gomode only
    os.chdir('latest_build/Output/combined/')
    print("Loading gomode...")
    df_gomode = pd.read_csv('data_gomode.csv')
    os.chdir(MAIN_DIR)
    
if LOAD_SEED_CLASSES:
    print("Loading seed classes...")
    # Seed classes    
    if True:
        seed_list = pickle.load(open('latest_build/Output/combined/saved_seeds.p', "rb"))
        seed_list_master = seed_list[:]
        
        seed_list_medallions = []
        seed_list_alldungeons = []
        
        for seed in seed_list:
            if seed.length == 'all_dungeons':
                seed_list_alldungeons.append(seed)
            else:
                seed_list_medallions.append(seed)
        seed_list_medallions_len = len(seed_list_medallions)
        seed_list_alldungeons_len = len(seed_list_alldungeons)
        
    seed = seed_list[random.randint(0,len(seed_list))] # test seed
    #seed = find_seed('YOB9PI0MUZ')
    #seed = find_seed('3WVI7S05OW')
    os.chdir(MAIN_DIR)
    
    


# # # THIS SHOULD BE BUILT IN ON SEED GENERATION:
if ASSIGN_CLASS_MODIFICATIONS:
    if False:
        print("Assiging seed class modifications to mst gomode...")
        for seed in seed_list:
            list_of_mst = seed.mst.split(" ")
            gomode_list = []
            for mst in list_of_mst:
                for item in go_mode_dict[mst]:
                    gomode_list.append(item)
            for item in go_mode_dict['All']:
                gomode_list.append(item)
            gomode_list = list(set(gomode_list))
            if "Water" in seed.mst:
                gomode_list.append('Progressive Hookshot')
            if "Spirit" in seed.mst:
                gomode_list.append('Progressive Strength Upgrade')
            seed.gomode_items = gomode_list
            seed.gomode_mst_dict = {k:v for k, v in seed.check_dict.items() if v in gomode_list}
        
            
            seed.filter_checklist(songs)
            seed.songs_dict = seed.output_checks
    
        pickle.dump(seed_list, open("latest_build/Output/combined/saved_seeds.p", "wb"))
    
    
    if False:
        print("Assigning gomode list")
        
        
        check_ranks = check_lookup[['requirements','rank']].to_dict()['rank']
        for seed in seed_list:
            seed_list_copy = seed_list.copy()
            w = seed.gomode_items.copy() # list of gomode items
            #x = seed.gomode_mst_dict.copy()
            y = seed.req_dict.copy()
            y_values = sorted(list(y.values()).copy())   # the req dict's existing values

            # Specific clause for hookshot/scale/strength. If these are in the playthru log MORE than the required_items dict, then they need to be manually added to gomode items
            problem_items = ['Progressive Strength Upgrade','Progressive Scale','Progressive Hookshot']
            for item in problem_items:
                num1 = w.count(item)
                num2 = y_values.count(item)
                num3 = list(seed.play_dict.values()).count(item)
                max_num = max(num1,num2,num3)
                if max_num > num1:
                    w.append(item)        
                    
            final_dict = seed.req_dict.copy() # Final_dict will start with at least what's in req_dict
            for reward in y_values:
                if reward in w:
                    w.remove(reward)
                    

            # With a list via missing_items, we need to update the req_dict until it has at least everything in the gomode dict. 
            for item in w:
                #print("-------------------")
                #print("CHECKING ITEM "+item)
                # For each item in the missing list, now find a matching dictionary entry for the reward. 
                # Then see if its in final_dict. If it isnt, good, add it. If not, keep searching
                
                list_of_checks = filter_dict(seed.check_dict,item,'vals') # returns a list of matching checks for that item
                rejected_checks = []
                item_satisfied = False
                #print("LIST OF CHECKS: "+' | '.join(list_of_checks))
                
                local_rank = {}
                for check in list_of_checks: # look at each check
                    local_rank[check] = check_ranks[check]
                list_of_checks = pd.DataFrame.from_dict(local_rank,orient='index').sort_values(0).index.tolist()  # this is a convoluted way of sorting the dictionary by values, using a dataframe and returning an ordered list

                for check in list_of_checks: # look at each check              
                    #print("Check "+check,"Rank "+str(local_rank[check]))
                    if check in final_dict.keys(): # if its already in the list, then keep searching the others 
                        #print("Check "+check+" already in dict, pass.")
                        pass  
                    else:        # Assign highest scoring rank
                        #print("Check "+check+" assigned.")
                        final_dict[check] = item
                        break
            seed.gomode_dict = final_dict
        pickle.dump(seed_list, open("latest_build/Output/combined/saved_seeds.p", "wb"))
    
    
    if False:
        print("Generating gomode dataframe...")
        num1 = 0
        num2 = 100
        while num1 < len(seed_list):
            print('Processing gomode batch '+str(num1))
            df_master = pd.DataFrame()
            for seed in seed_list[num1:num2]:
                df = pd.DataFrame.from_dict(seed.gomode_dict,orient='index')
                df.reset_index(inplace=True)
                df.columns = ['check','reward']
                df['seed'] = seed.name
                df['count'] = 1
                df['mst'] = seed.mst
                df['length'] = seed.length
                df_master = df_master.append(df)    
            num1 = num1 + 100
            num2 = num2 + 100
            df_master.to_csv('latest_build/Output/processing/gomode_processed/data_gomode'+str(num1)+'.csv')
        
        df_master = pd.DataFrame()
        for csv in os.listdir('latest_build/Output/processing/gomode_processed/'):
            df = pd.read_csv('latest_build/Output/processing/gomode_processed/'+csv)
            df_master = df_master.append(df)
            
        df_master.drop('Unnamed: 0',axis=1,inplace=True)
        df_master.to_csv('latest_build/Output/combined/data_gomode.csv')
        
        df_pivot_c = df_master.pivot_table(index=['check'],values='count',columns='length',aggfunc=np.sum).fillna(0)
        df_pivot_c['all_dungeons_%'] = round((df_pivot_c['all_dungeons'] / seed_list_alldungeons_len) * 100,4)
        df_pivot_c['medallions_%'] = round((df_pivot_c['medallions'] / seed_list_medallions_len) * 100,4)
        df_pivot_c['delta'] = df_pivot_c['all_dungeons_%'] - df_pivot_c['medallions_%']
        df_pivot_c = df_pivot_c.sort_values(by='delta',ascending=False)
        df_pivot_c.to_csv('latest_build/Output/combined/data_gomode_pivotcheck.csv')
        
        df_pivot_cr = df_master.pivot_table(index=['check','reward'],values='count',columns='length',aggfunc=np.sum).fillna(0)
        df_pivot_cr['all_dungeons_%'] = df_pivot_cr['all_dungeons'] / seed_list_alldungeons_len
        df_pivot_cr['medallions_%'] = df_pivot_cr['medallions'] / seed_list_medallions_len
        df_pivot_cr['delta'] = df_pivot_cr['all_dungeons_%'] - df_pivot_cr['medallions_%']
        df_pivot_cr = df_pivot_cr.sort_values(by='delta',ascending=False)
        df_pivot_cr.to_csv('latest_build/Output/combined/data_gomode_pivotcheckreward.csv')
    
        df_gomode = df_master.copy()
        df_gomode_check = df_pivot_c.copy()
        df_gomode_checkreward = df_pivot_cr.copy()

print("Finished init.")




# ANALYSIS
    
    
########################
# Dungeon distribution (A/B for dungeon in / not in seed)
########################    
def dungeon_distribution():
    os.chdir('latest_build/Output/combined')
    
    
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
        df = pd.read_csv('data_play.csv')
        df2 = pd.read_csv('data_play_mst_mapping.csv')
        df2.columns = ['seed','REQUIRED_MST','SEED_LENGTH','count']
        df2.set_index('seed',inplace=True)
        df2.drop('count',axis=1,inplace=True)
        df = df.join(df2,on='seed')
        # Filter out all dungeons
        df = df[df['SEED_LENGTH']=='medallions']
        df_pivot = df.pivot_table(index=['check'],columns='REQUIRED_MST',values='count',aggfunc=np.sum)
        
        
    # Make pivot by CHECK only
    #df_pivot.drop('REWARD',axis=1,inplace=True)
    #df_pivot = df_pivot.pivot_table(index=['CHECK'],aggfunc=np.sum)
    
    
    
    # df_pivot.drop('Jabu Shadow Dodongo Water Forest Deku Spirit Fire',axis=1,inplace=True)
    
    
    # Loads the lookup table for count of each dungeon spread (e.g. "Deku Fire Water Spirit Shadow | 450")
    df_mst_pivot = pd.read_csv('data_play_mst_mapping_pivot.csv')
    df_mst_pivot.set_index('REQUIRED_MST',inplace=True)

    os.chdir(MAIN_DIR)
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
def find_seed_midos_important():
    num = 0
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




def seed_scorer(scorer='manual',sortby='ascending'):
    '''
    Returns seeds_high and seeds_low
    '''
    num = 0
    
    # Playground - mess with parameters for how for loop works, what scoring is, etc. 
    score_list = {}  # dict of seed, score
    for seed in seed_list:
        # print("Processing "+str(num))
        num = num + 1
        score = 0
        if scorer == 'manual':
            # Checking requirements for critical/important/unique
    #        for check_noreq in check_list_noreqs.keys():
    #            if seed.check_dict[check_noreq] in reward_critical:
    #                score = score + 1
                    
             
            # Define reward settings:
            
            REWARD_SETTING = reward_critical
            
            # Define check list by specific matching:
            
            # check_list = list(set( filter_dict(check_dict, 'Mido', 'keys')))  # check_shadow + check_spirit + check_gtg + check_ice +
            check_list = list(set(check_worst))
            # check_list2 = list(set(check_deku + check_dc + check_noreqs))
            
            for check in seed.check_dict.keys():
                if check in check_list:
                    temp_check = seed.check_dict[check]
                    if temp_check in REWARD_SETTING:
                        score = score + 1
    #            if check in check_list2:
    #                temp_check = seed.check_dict[check]
    #                if temp_check in reward_important:
    #                    score = score - 100
                
            score_list[seed.name] = score
                    
            
            # Add lists to seeds
            seed.filter_checklist(check_list)
            seed.filter_rewardlist(REWARD_SETTING)
        if scorer == 'rank':
            check_ranks = check_lookup[['requirements','rank']].to_dict()['rank']
            temp_score = 0
            for k, v in seed.gomode_dict.items():
                temp_score = temp_score + check_ranks[k]
            score = temp_score / len(seed.gomode_dict.keys())  # divide score by # of gomode items for comparable metric among seeds
            score_list[seed.name] = score
            
            
            
    # Standardized output 
    df = pd.DataFrame(pd.Series(score_list))
    df.columns = ['score']
    df['count'] = 1
    df_pivot = df.pivot_table(index=['score',df.index],values=['count'],aggfunc=np.sum)
    print(df_pivot)
    df_pivot_final = df.pivot_table(index=['score'],values=['count'],aggfunc=np.sum)
    if sortby == 'ascending':
        print(df_pivot_final)
    else:
        print(df_pivot_final.sort_values(by='score',ascending=False))

    return df_pivot, df_pivot_final

# =============================================================================
# 
#     # Highest and lowest scoring groups put into seed list
#     seeds_high = []
#     seeds_low = []
#     df_pivot.reset_index(inplace=True)
#     max_score = df_pivot['score'].unique().max()
#     min_score = df_pivot['score'].unique().min()
#     
#     seeds_high_str = df_pivot[df_pivot['score']==max_score]['level_1'].unique().tolist()
#     seeds_low_str = df_pivot[df_pivot['score']==min_score]['level_1'].unique().tolist()
#     
#     for seed_str in seeds_high_str:
#         seeds_high.append(find_seed(seed_str))
#     for seed_str in seeds_low_str:
#         seeds_low.append(find_seed(seed_str))    
#     
#     return seeds_high, seeds_low, df_pivot, df_pivot_final
# =============================================================================



##################
# Find SHORTEST/LONGEST playthrus
##################
        
def find_seed_playthru_length():
    '''
    Returns df_pivot of all playthru length
    '''
    temp_dict = {}
    for seed in seed_list:
        temp_dict[seed.name] = max(seed.play_map.keys())    
    df = pd.DataFrame(pd.Series(temp_dict))
    df.reset_index(inplace=True)
    df.columns = ['seed','play_length']
    df['count'] = 1
    df_pivot = df.pivot_table(index='play_length',values='count',aggfunc=np.sum)    
    
    print(df_pivot)
    df_max = df['play_length'].max()
    df_min = df['play_length'].min()
    print("MAX")
    print(df[df['play_length']==df_max])
    print("MIN")
    print(df[df['play_length']==df_min])
    return df_pivot

#####################
# A/B distributions
#####################

def call_ab_filter(seed_list, criteria, df_choice = 'req', filter_str=''):
    criteria = 'all_dungeons'
    df_choice = 'play'
    # seed_list 
    # criteria = must be from a set number of criteria
    # filter_str = string to filter on. Depends on criteria (rewards, checks, etc.)
    
    
    # GOAL : Generate two seed lists, one that matches the criteria, one that doesn't
    # ALL CRITERIA FUNCTIONS SHOULD RENDER THESE TWO
    if criteria == 'all_dungeons':
        match_seeds, nonmatch_seeds = [], []
        for seed in seed_list:
            if seed.length == 'all_dungeons':
                match_seeds.append(seed.name)
            else:
                nonmatch_seeds.append(seed.name)
                

    
    # After match_seeds and nonmatch_seeds generated, create pivots

    # Choose df
    if df_choice == 'req':
        df = df_req.copy()
    elif df_choice == 'dist' or df_choice == 'distribution':
        df = df_dist.copy()
    elif df_choice == 'play' or df_choice == 'playthrough':
        df = df_play.copy()
    
    # Func to split seed from file name into actual seed name
    def clean_seed(x):
        try:
            return x.split("_")[2]
        except:
            print("Failed to split seed "+x)
            return x
        

        
    df['clean_seed'] = df['seed'].apply(clean_seed)
    # With full match/nonmatch, generate distributions
    df_match = df[df['clean_seed'].isin(match_seeds)]
    df_nonmatch = df[df['clean_seed'].isin(nonmatch_seeds)]
    
    # Apply percentages
    df_match['percent'] = df_match['count'] / len(df_match['clean_seed'].unique())    
    df_nonmatch['percent'] = df_nonmatch['count'] / len(df_nonmatch['clean_seed'].unique())

    
    df_match_pivot = df_match.pivot_table(index=['check'],values = 'percent',aggfunc=np.sum)
    df_nonmatch_pivot = df_nonmatch.pivot_table(index=['check'],values = 'percent',aggfunc=np.sum)
    
    df_match_pivot.reset_index(inplace=True)
    df_match_pivot.columns = ['check','percent_match']
    df_nonmatch_pivot.columns = ['percent_nonmatch']

    df_match_pivot['percent_match'] = df_match_pivot['percent_match'].apply(lambda x: round(x,5))
    df_nonmatch_pivot['percent_nonmatch'] = df_nonmatch_pivot['percent_nonmatch'].apply(lambda x: round(x,5))    
    
    df_final = df_match_pivot.join(df_nonmatch_pivot,on='check')
    df_final = df_final.fillna(0)
    df_final['delta'] = df_final['percent_match'] - df_final['percent_nonmatch']
    df_final['multiple'] = df_final['delta'] / df_final['percent_nonmatch']
    df_final['multiple'] = df_final['multiple'].apply(apply_multiple)
    
    df_final.to_csv('analysis_render/abfilter_'+criteria+"_"+df_choice+"_"+RENDER_TIME+'.csv',index=None)




##################
# SONG DISTRIBUTION
##################
    
    
def song_distribution():
    # Checking if first four songs are correlated to all_dungeons vs. medallions

    seed_list_medallions = []
    seed_list_alldungeons = []
    
    for seed in seed_list:
        if seed.length == 'all_dungeons':
            seed_list_alldungeons.append(seed)
        else:
            seed_list_medallions.append(seed)
            
            
    # FIRST: create an overall dataframe for metrics per song 
    
    
    # All Dungeons
    df = pd.DataFrame()    
    for seed in seed_list_alldungeons:
        temp_dict = dict(zip(songs_rewards,[0]*len(songs_rewards)))
        seed_songs = sorted([seed.songs_dict['Impa at Castle'],seed.songs_dict['Song from Malon'],seed.songs_dict['Song from Saria'],seed.songs_dict['Song at Windmill']])
        for song in seed_songs:
            temp_dict[song] = 1
        temp_dict['length'] = seed.length
        temp_dict['seed'] = seed.name
        temp_dict['seed_songs'] = '|'.join(seed_songs)
        df_temp = pd.DataFrame(temp_dict,index=[0])
        df = df.append(df_temp)
    df_pivot = df.pivot_table(index=['length'],values=list(df.columns[0:12]),aggfunc=np.sum)/(len(seed_list_alldungeons))*100
    df_pivot = df_pivot.transpose()
    # df_pivot.to_csv('analysis_render/songs_metrics_alldungeons_'+RENDER_TIME+'.csv')  # Unnecessary output

    # Medallions
    df2 = pd.DataFrame()    
    for seed in seed_list_medallions:
        temp_dict = dict(zip(songs_rewards,[0]*len(songs_rewards)))
        seed_songs = sorted([seed.songs_dict['Impa at Castle'],seed.songs_dict['Song from Malon'],seed.songs_dict['Song from Saria'],seed.songs_dict['Song at Windmill']])
        for song in seed_songs:
            temp_dict[song] = 1
        temp_dict['length'] = seed.length
        temp_dict['seed'] = seed.name
        temp_dict['seed_songs'] = '|'.join(seed_songs)
        df_temp = pd.DataFrame(temp_dict,index=[0])
        df2 = df2.append(df_temp)
    df_pivot2 = df2.pivot_table(index=['length'],values=list(df.columns[0:12]),aggfunc=np.sum)/(len(seed_list_medallions))*100
    df_pivot2 = df_pivot2.transpose()
    # df_pivot2.to_csv('analysis_render/songs_metrics_medallions_'+RENDER_TIME+'.csv') # Unnecessary output
    
    # Joined clean table
    
    df_pivot3 = df_pivot.join(df_pivot2)
    df_pivot3['delta'] = df_pivot3['medallions'] - df_pivot3['all_dungeons']
    df_pivot3 = df_pivot3.sort_values(by='delta',ascending=False)
    df_pivot3.reset_index(inplace=True)
    df_pivot3.columns = ['songs','all_dungeons','medallions','delta']
    df_pivot3.to_csv('analysis_render/songs_metrics_both_'+RENDER_TIME+'.csv',index=None)


    # SECOND: Correlation matrix
    df = df.append(df2)   # new df 
    df['count'] = 1
    df.to_csv('analysis_render/songs_completeset_'+RENDER_TIME+'.csv')
    df_lookup = df.pivot_table(index=['seed_songs',],values=list(df.columns[0:12]))
    df_lookup.to_csv('analysis_render/songs_lookup_matrix_'+RENDER_TIME+'.csv')
    
    df_pivot = df.pivot_table(index=['seed_songs'],columns=['length'],values='count',aggfunc=np.sum)
    cols = list(df_pivot.columns)
    df_pivot.reset_index(inplace=True)
    df_pivot.columns = ['four_songs'] + cols
    cols = list(df_pivot.columns)
    df_pivot = df_pivot.fillna(0)
    df_pivot['delta'] = df_pivot['medallions'] - df_pivot['all_dungeons']
    df_pivot['multiple'] = np.vectorize(apply_multiple_2)(df_pivot['delta'],df_pivot['all_dungeons'])
    df_pivot = df_pivot[cols[0:3] + ['delta'] + ['multiple']]
    df_pivot = df_pivot.sort_values(by='multiple',ascending=False)  
    df_pivot.to_csv('analysis_render/songs_pivot_combined_'+RENDER_TIME+'.csv',index=None)
    
    
    # Finally, correlations
    df_final = df_pivot.join(df_lookup,on='four_songs')
    df_final.to_csv('analysis_render/songs_pivot_combinedFULL_'+RENDER_TIME+'.csv',index=None)


        
    # NEW METHOD: Correct...?
    
    #   Medallions
    df_final_medallions = df_final.drop('all_dungeons',axis=1)
    for col in df_final_medallions.columns[4:]:
        df_final_medallions[col] = np.vectorize(apply_songcount)(df_final_medallions[col],df_final_medallions['medallions'])
    df_final_medallions_corr = df_final_medallions.corr()[['medallions']].drop(['delta','medallions'])
    
    #   All dungeons
    df_final_all_dungeons = df_final.drop('medallions',axis=1)
    for col in df_final_all_dungeons.columns[4:]:
        df_final_all_dungeons[col] = np.vectorize(apply_songcount)(df_final_all_dungeons[col],df_final_all_dungeons['all_dungeons'])
    df_final_all_dungeons_corr = df_final_all_dungeons.corr()[['all_dungeons']].drop(['delta','all_dungeons'])
    
    # Final corr
    df_corr = df_final_medallions_corr.join(df_final_all_dungeons_corr)
    df_corr = df_corr.round(4)
    df_corr.reset_index(inplace=True)
    df_corr['delta'] = df_corr['medallions'] - df_corr['all_dungeons']
    df_corr.columns = ['songs','medallions','all_dungeons','delta']
    df_corr = df_corr.sort_values(by='delta',ascending=False)
    df_corr = df_corr.fillna(0)
    df_corr.to_csv('analysis_render/songs_corr_combined_'+RENDER_TIME+'.csv',index=None)
    
    
    # Old Method (incorrect...?)
    df_corr = df_final.corr()[['all_dungeons','medallions']].drop(['all_dungeons','medallions','delta'])
    df_corr = df_corr.round(4)
    df_corr['delta'] = df_corr['medallions'] - df_corr['all_dungeons']
    df_corr.reset_index(inplace=True)
    df_corr = df_corr.sort_values(by='delta',ascending=False)
    df_corr = df_corr.fillna(0)
    df_corr.columns = ['songs','all_dungeons','medallions','delta']
    df_corr.to_csv('analysis_render/songs_corr_combined_OLDMETHOD_'+RENDER_TIME+'.csv',index=None)






# =============================================================================
# Scrappy code
# =============================================================================

# 
    

# =============================================================================
# # go mode dist pivot
#     
# #pivot = df_gomode.pivot_table(index='check',columns='length',values='count',aggfunc=np.sum).sort_values(by='check',ascending=False)    
# #pivot.reset_index(inplace=True)
# #pivot['%_all_dungeons'] = pivot['all_dungeons'] / seed_list_alldungeons_len
# #pivot['%_medallions'] = pivot['medallions'] / seed_list_medallions_len
# #pivot['delta'] = pivot['%_all_dungeons'] - pivot['%_medallions']
# #pivot = pivot.fillna(0)
# #pivot2 = pivot.pivot_table(index='check',values=['%_medallions','%_all_dungeons','delta']).sort_values(by='delta',ascending=False)
# #pivot2 = pivot2.round(4) * 100
# #pivot2 = pivot2[['%_medallions','%_all_dungeons','delta']]
# #pivot2.to_csv('analysis_render/GOMODE_DIST.csv')
# =============================================================================


#  all dist pivot
 
# =============================================================================
# pivot = df_dist.pivot_table(index=['check','reward'],values='count',aggfunc=np.sum).sort_values(by='check',ascending=False)
# pivot.reset_index(inplace=True)
# pivot['%'] = pivot['count']/len(seed_list)
# pivot = pivot.fillna(0)
# pivot2 = pivot.pivot_table(index=['check','reward'],values=['%']).sort_values(by=['check','%'],ascending=[True,False])
# pivot2 = pivot2.round(4) * 100
# pivot2.to_csv('analysis_render/DIST_FULL.csv')
# 
# pivot2.reset_index(inplace=True)
# pivot3 = pivot2[pivot2['reward'].isin(reward_unique)]
# pivot3 = pivot3.set_index('check')
# pivot3.to_csv('analysis_render/DIST_UNIQUE.csv')
# =============================================================================
 


# =============================================================================
# # distribution of gomode items in norequirement checks:
#     
# #seed_scores = {}
# #d = filter_check_rank(1)
# #for seed in seed_list:
# #    seed_score = 0
# #    for key in seed.gomode_dict:
# #        if key in d:
# #            seed_score = seed_score + 1
# #    seed_scores[seed.name] = seed_score
# #    
# #d = pd.DataFrame.from_dict(seed_scores,orient='index').reset_index()
# #d['group'] = d[0].astype(int)
# #d.columns = ['seed','count','group']
# #d['count'] = 1
# #x = d.pivot_table(index='group',values='count',aggfunc=np.sum)
# #x = x.reset_index()
# #x.columns = ['Count of gomode items in noreq checks','# of seeds']
# #x['%'] = x['# of seeds'] / len(seed_list)
# #x.to_csv('analysis_render/NOREQ_GOMODE_DIST.csv',index=None)
# #
# 
# # above split by all_dungeons / medallions
#     
# seed_scores = {}
# filter_list = filter_check_rank(1)
# for seed in seed_list_medallions:
#     seed_score = 0
#     for key in seed.gomode_dict:
#         if key in filter_list:
#             seed_score = seed_score + 1
#     seed_scores[seed.name] = seed_score
#     
# d = pd.DataFrame.from_dict(seed_scores,orient='index').reset_index()
# d['group'] = d[0].astype(int)
# d.columns = ['seed','count','group']
# d['count'] = 1
# z = d.pivot_table(index='group',values='count',aggfunc=np.sum)
# z = z.reset_index()
# z.columns = ['Count of gomode items in noreq checks','# of seeds']
# z['%'] = z['# of seeds'] / len(seed_list_medallions)
# #z.to_csv('analysis_render/NOREQ_GOMODE_DIST_MEDALLIONS.csv',index=None)
# 
# seed_scores = {}
# filter_list = filter_check_rank(1)
# for seed in seed_list_alldungeons:
#     seed_score = 0
#     for key in seed.gomode_dict:
#         if key in filter_list:
#             seed_score = seed_score + 1
#     seed_scores[seed.name] = seed_score
#     
# d = pd.DataFrame.from_dict(seed_scores,orient='index').reset_index()
# d['group'] = d[0].astype(int)
# d.columns = ['seed','count','group']
# d['count'] = 1
# y = d.pivot_table(index='group',values='count',aggfunc=np.sum)
# y = y.reset_index()
# y.columns = ['Count of gomode items in noreq checks','# of seeds']
# y['%'] = y['# of seeds'] / len(seed_list_alldungeons)
# #y.to_csv('analysis_render/NOREQ_GOMODE_DIST_ALLDUNGEONS.csv',index=None)
# 
# y = y.set_index('Count of gomode items in noreq checks')
# y.columns = ['# of seeds_alldungeons','%_alldungeons']
# z = z.set_index('Count of gomode items in noreq checks')
# z.columns = ['# of seeds_medallions','%_medallions']
# a = y.join(z)
# a = a.fillna(0)
# a = a.drop(['# of seeds_medallions','# of seeds_alldungeons'],axis=1)
# a.to_csv('analysis_render/NOREQ_GOMODE_DIST_SPLIT.csv')
# =============================================================================

###################
# RUN 
###################


#seeds_high, seeds_low, df_pivot, df_pivot_final = seed_scorer(scorer='rank',sortby='a')