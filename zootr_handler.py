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




MAIN_DIR = os.getcwd()
time_str = str(datetime.datetime.now()).replace(":","-")
time_now = "archived/archive_"+time_str+"/"
cluster_size = 1

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

    




#################
# CLASS SETUP
#################


class Seed:
    def __init__(self, seed, check_dict, req_dict, play_dict, settings):
        # Seed = seed
        # items = dictionary of 1:1 items by check e.g. [{'Mido Chest Top Left':'Bow'}]. from DISTRIBUTION
        # Settings = settings for seed - fast ganon, etc. 
        
        self.name = seed
        self.check_dict = check_dict
        self.req_dict = req_dict
        self.req_dict = play_dict
        self.settings = settings
        



# Generate Seed classes based off of data, both distribution & required items

def generate_classes():
    
    # Location
    os.chdir(MAIN_DIR)
    os.chdir('latest_build/Output/combined/')

    df = pd.read_csv('data_dist.csv')
    df_req = pd.read_csv('data_req.csv')
    df_play = pd.read_csv('data_play.csv')
    if df.empty == False:
        num = 0
        df['seed_clean'] = df['seed'].apply(clean_seed)
        df_req['seed_clean'] = df_req['seed'].apply(clean_seed)
        df_play['seed_clean'] = df_play['seed'].apply(clean_seed)
        
        seed_list = df['seed_clean'].unique().tolist()
        
        seed_class_list = []
        
        for seed in seed_list:
            print("Processing Seed class generation "+str(num)+"...")
            num = num + 1
            # Filter both dataframes for seed
            #df_temp = df[df['seed_clean']==seed]
            #df_req_temp = df_req[df_req['seed_clean']==seed]
            
            df_temp = df.loc[np.in1d(df['seed_clean'], [seed])]
            df_req_temp = df_req.loc[np.in1d(df_req['seed_clean'], [seed])]
            df_play_temp = df_play.loc[np.in1d(df_play['seed_clean'], [seed])]
            
            check_dict = pd.Series(df_temp['reward'].values,index=df_temp['check']).to_dict()
            req_dict = pd.Series(df_req_temp['reward'].values,index=df_req_temp['check']).to_dict()
            play_dict = pd.Series(df_play_temp['reward'].values,index=df_play_temp['check']).to_dict()
            
            seed_class_list.append(Seed(seed,check_dict,req_dict,play_dict,'fast_ganon'))
        pickle.dump(seed_class_list, open("saved_seeds.p", "wb"))
    else:
        print("No data in data_dist. Check overall load.")












####################
# RUN FUNCTION
####################        

os.chdir('latest_build/')
from latest_build import OoTRandomizer
OoTRandomizer.start()

os.chdir(MAIN_DIR)
        
def run():
    clear_files()
    aggregate_distribution()
    aggregate_playthrough()
    aggregate_required()
    # archive_seeds()
    generate_classes()
    
run()