
import time
import os
import pandas as pd


#Establishing constants from the experiments
SEP = os.sep
REPEAT = 3
CV = 10
MOP='MOP7'
MAXRULE = 60
CRITERIA = 16
EXPERIMENT_SCV ="MOP7 Valid Rates"
EXPERIMENT_DOBSCV = "DOBSCV"
GENERATION = '5000'

#Establishing datasets used in this experiment
datasets = ['australian','iris','magic','newthyroid','page-blocks','penbased','phoneme','ring','satimage','segment','shuttle','pima','vehicle','sonar','wine','yeast']

#Establishing the subtra-valid rates used in this experiment
subrates =["1","2","3","5","7","8","9"]
values = ['Dtra','Dsubtra','Dvalid','Dtst','ruleNum']


# want is the type of MOP formulation for which we want the values(Aka best classifier for the subtraining data,validation data, average between both etc)
def getAveragePopulation(dataset,subrate,want,experiment_cv,values,mop):
    if(mop == 'MOP1'):
        dirName =experiment_cv+SEP+ dataset + "_" + mop + "at5"
        new_dict ={'Dataset':dataset,'ValidRate':"0."+str(10-int(subrate))}
        subrate = '5'
    else:
        dirName =experiment_cv+SEP+ dataset + "_" + mop + "at"+subrate
        new_dict ={}
    
    #dict as a sum ledger to keep track of the values
    sum_dict ={
        'Dtra': 0,
        'Dsubtra':0,
        'Dvalid':0,
        'Dtst':0,
        'ruleNum':0,
        'average':0
        }

    # for each cross validation case (In this case 30)
    for rr in range(REPEAT):
        for cc in range(CV):

            trial = "trial" +str(rr)+str(cc)
            
            fileName = dirName + SEP + trial + SEP + "population"+SEP+"individual" + SEP + "gen"+GENERATION+".csv"
            df = pd.read_csv(fileName)
            #check for non-dominated solutions
            df =df[df['rank'] == 0]
            #sorting by each of the required things
            if(want == 'Dtra'):
                df = df.sort_values(['Dtra','ruleNum','ruleLength'],ascending=True)
            elif(want == 'Dsubtra'):
                df = df.sort_values(['Dsubtra','ruleNum','ruleLength'],ascending=True)
            elif(want == 'Dvalid'):
                df = df.sort_values(['Dvalid','ruleNum','ruleLength'],ascending=True)
            elif(want == 'average_half'):
                df['average'] = (df['Dsubtra'] +df['Dvalid'])/2
                df = df.sort_values(['average','ruleNum','ruleLength'],ascending =True)
            elif(want == 'average_proportional'):
                df['average'] = (df['Dsubtra']*(float("0."+subrate)) + df['Dvalid']*(1-float("0."+subrate)))/2
                df = df.sort_values(['average','ruleNum','ruleLength'],ascending =True)

            #Adding the values to the dictionary(check for average and if and only if it exists then add to dictionary else just omit)
            for value in values:
                if(value == 'average'):
                     if(want == 'average_proportional' or want == 'average_half'):
                         sum_dict[value] = sum_dict[value]+df[value].iloc[0]
                else:
                    sum_dict[value] =sum_dict[value] + df[value].iloc[0]
    
    
    for value in values:
        new_dict[value] = sum_dict[value]/30
    

    return new_dict


#creating dataframes with each of the values I want for each of the MOPs

df_mop_1 = pd.DataFrame(columns        = ['Dataset','ValidRate','Dtra','Dtst','ruleNum'])
df_mop_subtra = pd.DataFrame(columns   = ['Dsubtra','Dtra','Dtst','ruleNum'])
df_mop_valid = pd.DataFrame(columns    = ['Dvalid','Dtra','Dtst','ruleNum'])
df_mop_ave_half = pd.DataFrame(columns = ['average','Dtra','Dtst','ruleNum'])
df_mop_ave_prop = pd.DataFrame(columns = ['average','Dtra','Dtst','ruleNum'])
df_dob_subtra = pd.DataFrame(columns   = ['Dsubtra','Dtra','Dtst','ruleNum'])
df_dob_valid = pd.DataFrame(columns    = ['Dvalid','Dtra','Dtst','ruleNum'])
df_dob_ave_half = pd.DataFrame(columns = ['average','Dtra','Dtst','ruleNum'])
df_dob_ave_prop = pd.DataFrame(columns = ['average','Dtra','Dtst','ruleNum'])

df =pd.DataFrame

for dataset in datasets:
    for subrate in subrates:
        print(dataset+ " " +subrate)
        #basic formulation data
        mop_1 = getAveragePopulation(dataset,subrate,'Dtra',EXPERIMENT_SCV,['Dtra','Dtst','ruleNum'],'MOP1') 

        df_mop_1= df_mop_1.append(mop_1,ignore_index=True)
        #new formulation with SCV
        mop_subtra = getAveragePopulation(dataset,subrate,'Dsubtra',EXPERIMENT_SCV,['Dsubtra','Dtra','Dtst','ruleNum'],MOP)
        mop_valid = getAveragePopulation(dataset,subrate,'Dvalid',EXPERIMENT_SCV,['Dvalid','Dtra','Dtst','ruleNum'],MOP)
        mop_ave_half  = getAveragePopulation(dataset,subrate,'average_half',EXPERIMENT_SCV,['average','Dtra','Dtst','ruleNum'],MOP)
        mop_ave_prop  = getAveragePopulation(dataset,subrate,'average_proportional',EXPERIMENT_SCV,['average','Dtra','Dtst','ruleNum'],MOP)
        
        df_mop_subtra= df_mop_subtra.append(mop_subtra,ignore_index=True)
        df_mop_valid= df_mop_valid.append(mop_valid,ignore_index=True)       
        df_mop_ave_half= df_mop_ave_half.append(mop_ave_half,ignore_index=True)
        df_mop_ave_prop= df_mop_ave_prop.append(mop_ave_prop,ignore_index=True)

        #new formulation with DOB-SCV
        dob_subtra = getAveragePopulation(dataset,subrate,'Dsubtra',EXPERIMENT_DOBSCV,['Dsubtra','Dtra','Dtst','ruleNum'],MOP)
        dob_valid = getAveragePopulation(dataset,subrate,'Dvalid',EXPERIMENT_DOBSCV,['Dvalid','Dtra','Dtst','ruleNum'],MOP)
        dob_ave_half  = getAveragePopulation(dataset,subrate,'average_half',EXPERIMENT_DOBSCV,['average','Dtra','Dtst','ruleNum'],MOP)
        dob_ave_prop  = getAveragePopulation(dataset,subrate,'average_proportional',EXPERIMENT_DOBSCV,['average','Dtra','Dtst','ruleNum'],MOP)
# 
        df_dob_subtra= df_dob_subtra.append(dob_subtra,ignore_index=True)
        df_dob_valid= df_dob_valid.append(dob_valid,ignore_index=True)       
        df_dob_ave_half= df_dob_ave_half.append(dob_ave_half,ignore_index=True)
        df_dob_ave_prop= df_dob_ave_prop.append(dob_ave_prop,ignore_index=True)

df_mop_1[' '] = ""  

#Formatting so that we can know what's after each dataframe
df_mop_subtra['MOPValid->'] = ""
df_mop_valid["MOP_Average ->"] = ""
df_mop_ave_half["MOP_Ave_Prop"] = ""

scv = pd.concat([df_mop_1 ,df_mop_subtra ,df_mop_valid , df_mop_ave_half , df_mop_ave_prop],axis =1)

#Formatting so that we can know what's after each dataframe
df_dob_subtra['DOB Valid ->'] = ""
df_dob_valid['DOB Ave ->'] =""
df_dob_ave_half['DOB Ave Prop ->'] =""

dob = pd.concat([df_mop_1,df_dob_subtra,df_dob_valid,df_dob_ave_half,df_dob_ave_prop],axis =1) 

#Exporting results to csv file
scv.to_csv('exp_csv_results/scv.csv')
dob.to_csv('exp_csv_results/dobscv.csv')

combined = pd.concat([scv,dob],axis=1)
combined.to_csv('exp_csv_results/dob and scv.csv')