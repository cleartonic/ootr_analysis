# -*- coding: utf-8 -*-
"""
Created on Thu Jun  7 16:11:19 2018

@author: cleartonic
"""

import pandas as pd
import numpy as np
import os
import shutil
import re
import pickle
import datetime
import sys



MAIN_DIR = os.getcwd()
sys.path.append('latest_build/')
time_str = str(datetime.datetime.now()).replace(":","-")
time_now = "archived/archive_"+time_str+"/"
cluster_size = 5
generate_num = 10


#################
# INIT - check if folder structure exists
#################

list_of_dirs = ['latest_build/Output/', 'latest_build/Output/archived','latest_build/Output/combined','latest_build/Output/combined/combined_archive','latest_build/Output/dist','latest_build/Output/hints','latest_build/Output/play','latest_build/Output/processing','latest_build/Output/req','latest_build/Output/settings','latest_build/Output/processing/dist_processed','latest_build/Output/processing/play_processed','latest_build/Output/processing/req_processed',]
for listdir in list_of_dirs:
    if not os.path.exists(listdir):
        os.mkdir(listdir)
#################
# Universal functions
#################


def apply_str1(x):
    y1 = x.split(":")[0]
    return y1.strip()

def apply_str2(x):
    y1 = x.split(":")[1]
    return y1.strip()


def clean_seed(x):
    try:
        return x.split("_")[2]
    except:
        print("Failed to split seed "+x)
        return x

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
# TEMP FILE CLEARING
#############

def clear_files():
    os.chdir(MAIN_DIR)
    os.chdir('latest_build/Output/processing/')
    for file in os.listdir('dist_processed/'):
        os.remove('dist_processed/'+file)
    for file in os.listdir('play_processed/'):
        os.remove('play_processed/'+file)
    for file in os.listdir('req_processed/'):
        os.remove('req_processed/'+file)

    os.chdir('../combined/')
    os.mkdir('combined_archive/'+time_str)
    for file in os.listdir():
        if file.endswith("csv") or file.endswith(".p"):
            shutil.move(file, "combined_archive/"+time_str+"/"+file)
    

# AGGREGATOR

##################
# REQUIRED ITEMS:
##################
    
def aggregate_required():
    print("Begin required items processing.")
    # Location:
    os.chdir(MAIN_DIR)
    os.chdir('latest_build/Output/req')
    
    if len(os.listdir()) == 0:
        print("No files to process.")
    else:
        # Phase 1 - mass handle txt files into chunks of cluster_size 
        num1 = 0
        num2 = cluster_size
        while num1 < len(os.listdir()):
            print("Processing required batch "+str(num1)+"...")
            df_master = pd.DataFrame()
            for file in os.listdir()[num1:num2]:
                df = pd.read_csv(file)
                df['check'] = df['Always Required Locations:'].apply(apply_str1)
                df['reward'] = df['Always Required Locations:'].apply(apply_str2)
                df.drop('Always Required Locations:',axis=1,inplace=True)
                df['seed'] = file
                df['count'] = 1
                df_master = df_master.append(df)
            num1 = num1 + cluster_size
            num2 = num2 + cluster_size
            df_master.to_csv('../processing/req_processed/req_data'+str(num1)+'.csv',index=None)
    
        # Phase 2 - combine prepared csvs into 1 mega table
        
        os.chdir(MAIN_DIR)
        os.chdir('latest_build/Output/processing/req_processed')
        
        df_master = pd.DataFrame()
        for file in os.listdir():
            print("Processing required "+file)
            df = pd.read_csv(file)
            df_master = df_master.append(df)
        df_master.to_csv('../../combined/data_req.csv',index=None)
        df_master.pivot_table(index=['check'],values='count',aggfunc=np.sum).to_csv('../../combined/data_req_checkpivot.csv')
        df_master.pivot_table(index=['check','reward'],values='count',aggfunc=np.sum).to_csv('../../combined/data_req_checkrewardpivot.csv')




##################
# PLAYTHROUGH:
##################
    
def aggregate_playthrough():
    print("Begin playthrough processing.")
    # Location:
    os.chdir(MAIN_DIR)
    os.chdir('latest_build/Output/play')
    
    
    if len(os.listdir()) == 0:
        print("No files to process.")
    else:
        # Phase 1 - mass handle txt files into chunks of cluster_size 
        
        num1 = 0
        num2 = cluster_size
        while num1 < len(os.listdir()):
            df_master = pd.DataFrame()
            print("Processing playthrough batch "+str(num1)+"...")
            for i in os.listdir()[num1:num2]:
                if i.endswith('.txt'):
                    df = pd.read_csv(i)
                    df['seed'] = i
                    df_master = df_master.append(df)            
            num1 = num1 + cluster_size
            num2 = num2 + cluster_size
            df_master.to_csv('../processing/play_processed/play_data'+str(num1)+'.csv',index=None)
    
                
        # Phase 2 - combine prepared csvs into 1 mega table
        
        os.chdir(MAIN_DIR)
        os.chdir('latest_build/Output/processing/play_processed')
        
        # Raw processing
        df_master = pd.DataFrame()
        for file in os.listdir():
            print("Processing "+file)
            df = pd.read_csv(file)
            df_master = df_master.append(df)
    
        os.chdir(MAIN_DIR)        
        df_master.to_csv('latest_build/Output/combined/data_play_raw.csv',index=None)
        
        
        def find_level(x):
            result = re.match("\d*\:\s\{", x)
            if result is not None:
                return x.split(":",2)[0]
            
        def mark_level(x):
            result = re.match("\d*\:\s\{", x)
            if result is not None:
                return 'xxx'
        
        def split_findings_0(x):
            return x.split(":")[0].strip()
        
        def split_findings_1(x):
            try:
                return x.split(":")[1].strip()
            except:
                return ""
        
        df_master['level'] = df_master['Playthrough:'].apply(find_level)
        df_master['mark'] = df_master['Playthrough:'].apply(mark_level)
        df_master['level'] = df_master['level'].fillna(method = 'ffill')
        df_master = df_master.loc[(df_master['mark']!='xxx')]
        df_master = df_master.loc[(df_master[df.columns[0]] != "}")]
        df_master['check'] = df_master['Playthrough:'].apply(split_findings_0)    
        df_master['reward'] = df_master['Playthrough:'].apply(split_findings_1)
        df_master['count'] = 1
        df_master = df_master.drop(['mark', 'Playthrough:'], axis=1)
        df_master = df_master[df_master['check']!='{']
        df_master = df_master[df_master['check']!='}']
        df_master['level'] = df_master['level'].astype(int)
        # df_master_nogs = df_master.loc[df_master['reward'] != 'Gold Skulltulla Token']
    
        os.chdir(MAIN_DIR)
        df_master.to_csv('latest_build/Output/combined/data_play.csv',index=None)
        df_master.pivot_table(index=['check'],values='count',aggfunc = np.sum).to_csv('latest_build/Output/combined/data_play_pivotcheck.csv')
        df_master.pivot_table(index=['check','reward'],values='count',aggfunc = np.sum).to_csv('latest_build/Output/combined/data_play_pivotcheckreward.csv')



#######################
# DISTRIBUTION:
#######################    
    
def aggregate_distribution():
    print("Begin distribution processing.")

    # Location
    os.chdir(MAIN_DIR)
    os.chdir('latest_build/Output/dist')
    
    if len(os.listdir()) == 0:
        print("No files to process.")
    else:

        
        # Phase 1 - mass handle txt files into chunks of cluster_size 
    
        num1 = 0
        num2 = cluster_size
        while num1 < len(os.listdir()):
            print("Processing distribution batch "+str(num1)+"...")
            df_master = pd.DataFrame()
            for file in os.listdir()[num1:num2]:
                df = pd.read_csv(file)
                df['check'] = df['Locations:'].apply(apply_str1)
                df['reward'] = df['Locations:'].apply(apply_str2)
                df.drop('Locations:',axis=1,inplace=True)
                df['seed'] = file
                df['count'] = 1
                df_master = df_master.append(df)
            num1 = num1 + cluster_size
            num2 = num2 + cluster_size
            
            df_master.to_csv('../processing/dist_processed/dist_data'+str(num1)+'.csv',index=None)
    
        # Phase 2 - combine prepared csvs into 1 mega table
        
        os.chdir(MAIN_DIR)
        os.chdir('latest_build/Output/processing/dist_processed')
        df_master = pd.DataFrame()
        for file in os.listdir():
            print("Processing distribution "+file)
            df = pd.read_csv(file)
            df_master = df_master.append(df)
        
        os.chdir(MAIN_DIR)
        df_master.to_csv('latest_build/Output/combined/data_dist.csv',index=None)
        df_master.pivot_table(index=['check'],values='count',aggfunc=np.sum).to_csv('latest_build/Output/combined/data_dist_checkpivot.csv')
        df_master.pivot_table(index=['check','reward'],values='count',aggfunc=np.sum).to_csv('latest_build/Output/combined/data_dist_checkrewardpivot.csv')











#############
# ARCHIVE
#############
    

# Create mst mapping for seeds. This takes the playthrough data and returns a pivot of each seeds' counts per required dungeons

def create_mst():
    print("Begin MST mapping.")
    # References
    mst = ['Forest Medallion','Fire Medallion','Water Medallion','Shadow Medallion','Spirit Medallion','Light Medallion','Kokiri Emerald','Goron Ruby','Zora Sapphire']
    dungeon_dict = {'Queen Gohma':'Deku','King Dodongo':'Dodongo','Barinade':'Jabu','Phantom Ganon':'Forest','Volvagia':'Fire','Morpha':'Water','Bongo Bongo':'Shadow','Twinrova':'Spirit'}

    os.chdir(MAIN_DIR)
    df = pd.read_csv('latest_build/Output/combined/data_play.csv')
    df_mst = pd.DataFrame() # will store the seeds per mst type, be used as lookup for original df
    
    num = 0
    for seed in df['seed'].unique().tolist():
        print("Processing "+str(num)+"...")


        df_temp = df[df['seed'] == seed]
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
    
    
#    # Join df_mst mappings to df, save files 
#    df = df.join(df_mst,on='SEED')
#    df.to_csv('data_play_mst.csv',index=None)
#    df_pivot = df.pivot_table(index=['check','reward'],columns=['REQUIRED_MST'],values='count',aggfunc=np.sum).fillna(0)
#    df_pivot.to_csv('test.csv')
    
    
    df_mst['count'] = 1
    df_mst.to_csv('latest_build/Output/combined/data_play_mst_mapping.csv')
    df_mst_pivot = df_mst.pivot_table(index='REQUIRED_MST',values='count',aggfunc=np.sum)
    df_mst_pivot.to_csv('latest_build/Output/combined/data_play_mst_mapping_pivot.csv')
    
    df_mst.reset_index(inplace=True)
    df_mst.columns = ['seed','REQUIRED_MST','SEED_LENGTH','count']
    return df_mst
    
    
    
    
    
    
    
    
    
    
#############
# ARCHIVE
#############
    
def archive_seeds():  
    print("Archiving seeds...")
    os.chdir(MAIN_DIR)
    os.chdir('latest_build/Output')
    os.mkdir(time_now)
    os.mkdir(time_now+"/dist")
    os.mkdir(time_now+"/settings")
    os.mkdir(time_now+"/hints")
    os.mkdir(time_now+"/req")
    os.mkdir(time_now+"/play")
    
    for file in os.listdir('dist/'):
        shutil.move('dist/'+file, time_now+"dist/"+file)
    for file in os.listdir('play/'):
        shutil.move('play/'+file, time_now+"play/"+file)
    for file in os.listdir('hints/'):
        shutil.move('hints/'+file, time_now+"hints/"+file)
    for file in os.listdir('req/'):        
        shutil.move('req/'+file, time_now+"req/"+file)
    for file in os.listdir('settings/'):        
        shutil.move('settings/'+file, time_now+"settings/"+file)

def clear_dirs():    
    print("Begin clearing directories.")
    os.chdir(MAIN_DIR)
    os.chdir('latest_build/Output')
    print("Clearing dist...")
    for file in os.listdir('dist/'):
        os.remove('dist/'+file)
    print("Clearing play...")
    for file in os.listdir('play/'):
        os.remove('play/'+file)
    print("Clearing hints...")
    for file in os.listdir('hints/'):
        os.remove('hints/'+file)
    print("Clearing reqs...")
    for file in os.listdir('req/'):        
        os.remove('req/'+file)
    print("Clearing settings...")
    for file in os.listdir('settings/'):
        os.remove('settings/'+file)




#################
# CLASS SETUP
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
        
        
        
# Generate Seed classes based off of data, both distribution & required items
def generate_classes():
    print("Begin class generation.")
    # Location
    os.chdir(MAIN_DIR)
    os.chdir('latest_build/Output/combined/')

    df = pd.read_csv('data_dist.csv')
    df_req = pd.read_csv('data_req.csv')
    df_play = pd.read_csv('data_play.csv')
    df_mst = create_mst()
    if df.empty == False:
        num = 0
        df['seed_clean'] = df['seed'].apply(clean_seed)
        df_req['seed_clean'] = df_req['seed'].apply(clean_seed)
        df_play['seed_clean'] = df_play['seed'].apply(clean_seed)
        df_mst['seed_clean'] = df_mst['seed'].apply(clean_seed)
        
        
        seed_list_master = df['seed_clean'].unique().tolist()
        
        seed_list = []
        
        for seed in seed_list_master:
            print("Processing Seed class generation "+str(num)+"...")
            num = num + 1

            # Filter df's for matching
            df_temp = df.loc[np.in1d(df['seed_clean'], [seed])]
            df_req_temp = df_req.loc[np.in1d(df_req['seed_clean'], [seed])]
            df_play_temp = df_play.loc[np.in1d(df_play['seed_clean'], [seed])]
            df_mst_temp = df_mst.loc[np.in1d(df_mst['seed_clean'], [seed])]
            
            
            # Set up basic dictionaries 
            check_dict = pd.Series(df_temp['reward'].values,index=df_temp['check']).to_dict()
            req_dict = pd.Series(df_req_temp['reward'].values,index=df_req_temp['check']).to_dict()
            play_dict = pd.Series(df_play_temp['reward'].values,index=df_play_temp['check']).to_dict()
            
            mst_map = df_mst_temp['REQUIRED_MST'].iloc[0]
            length = df_mst_temp['SEED_LENGTH'].iloc[0]
            
            # Formally instatiate Seed
            seed_list.append(Seed(seed,check_dict,req_dict,play_dict,mst_map,length,'fast_ganon'))
        pickle.dump(seed_list, open("latest_build/Output/combined/saved_seeds.p", "wb"))
    else:
        print("No data in data_dist. Check overall load.")




def generate_gomode():
    os.chdir(MAIN_DIR)
    print("Generating gomode dataframe...")
    seed_list = pickle.load(open("latest_build/Output/combined/saved_seeds.p", "rb"))
    
    seed_list_medallions = []
    seed_list_alldungeons = []
    
    for seed in seed_list:
        if seed.length == 'all_dungeons':
            seed_list_alldungeons.append(seed)
        else:
            seed_list_medallions.append(seed)
    seed_list_medallions_len = len(seed_list_medallions)
    seed_list_alldungeons_len = len(seed_list_alldungeons)

    df_master = pd.DataFrame()
    for seed in seed_list:
        df = pd.DataFrame.from_dict(seed.gomode_dict,orient='index')
        df.reset_index(inplace=True)
        df.columns = ['check','reward']
        df['seed'] = seed.name
        df['count'] = 1
        df['mst'] = seed.mst
        df['length'] = seed.length
        df_master = df_master.append(df)
        
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

    # df_gomode = df_master.copy()
    # df_gomode_check = df_pivot_c.copy()
    # df_gomode_checkreward = df_pivot_cr.copy()

    os.chdir(MAIN_DIR)





####################
# RUN FUNCTION
####################        



def run_seeds():
    os.chdir('latest_build/')
    for i in range(0,generate_num):
            ##############
            # FIX 
            ############
        settings_str = open('../commandline_settings.txt','r').read()
        os.system("python OoTRandomizer.py "+settings_str)
        #subprocess.Popen(["python", "OoTRandomizer.py"+settings_str])

    os.chdir(MAIN_DIR)
        
def run():
    clear_files()
    aggregate_distribution()
    aggregate_playthrough()
    aggregate_required()
    archive_seeds()
    generate_classes()
    generate_gomode()

def run_noarchive():
    clear_files()
    aggregate_distribution()
    aggregate_playthrough()
    aggregate_required()
    generate_classes()
    generate_gomode()

#run_seeds()
#run()
#seed_list = pickle.load(open("latest_build/Output/combined/saved_seeds.p", "rb"))