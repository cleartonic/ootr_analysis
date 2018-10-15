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
cluster_size = 100
generate_num = 10000


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
        df_master.pivot_table(index=['check'],values='count',aggfunc=np.sum).to_csv('../../combined/data_req_checkpivot.csv',index=None)
        df_master.pivot_table(index=['check','reward'],values='count',aggfunc=np.sum).to_csv('../../combined/data_req_checkrewardpivot.csv',index=None)




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
        df_master.pivot_table(index=['check'],values='count',aggfunc=np.sum).to_csv('latest_build/Output/combined/data_dist_checkpivot.csv',index=None)
        df_master.pivot_table(index=['check','reward'],values='count',aggfunc=np.sum).to_csv('latest_build/Output/combined/data_dist_checkrewardpivot.csv',index=None)











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


go_mode_dict = {'Deku':['Slingshot'],
                'Dodongo':['Progressive Strength Upgrade','Bomb Bag'],
                'Jabu':['Bottle with Letter','Boomerang'],
                'Forest':['Progressive Strength Upgrade','Bow','Progressive Hookshot'],
                'Fire':['Progressive Strength Upgrade','Bomb Bag','Hammer'],
                'Water':['Progressive Strength Upgrade','Iron Boots','Bow','Progressive Hookshot'],
                'Shadow':['Progressive Strength Upgrade','Zeldas Lullaby','Bow','Magic Meter','Progressive Hookshot','Hover Boots','Lens of Truth','Dins Fire'],
                'Spirit':['Progressive Strength Upgrade','Zeldas Lullaby','Bow','Progressive Hookshot','Mirror Shield'],
                'All':['Bow','Magic Meter','Light Arrows']}

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
        
        # Create gomode mapping:
        
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
        self.gomode_dict = {k:v for k, v in self.check_dict.items() if v in gomode_list}


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
        
        
        seed_list = df['seed_clean'].unique().tolist()
        
        seed_class_list = []
        
        for seed in seed_list:
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
            seed_class_list.append(Seed(seed,check_dict,req_dict,play_dict,mst_map,length,'fast_ganon'))
        pickle.dump(seed_class_list, open("latest_build/Output/combined/saved_seeds.p", "wb"))
    else:
        print("No data in data_dist. Check overall load.")












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

def run_noarchive():
    clear_files()
    aggregate_distribution()
    aggregate_playthrough()
    aggregate_required()
    generate_classes()
    

#run_seeds()
#run()