import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pandas import IndexSlice as idx


### UTILS
def get_util_df():
    util_df = pd.read_csv("./db/UTIL.csv")
    util_df['TO_DATETIME'] = pd.to_datetime(util_df['TO_DATE'] + ' ' + util_df['TO_TIME (UTC)'])
    util_df['LAND_DATETIME'] = pd.to_datetime(util_df['LAND_DATE'] + ' ' + util_df['LAND_TIME (UTC)'])
    util_df['FL_DURR'] = util_df['LAND_DATETIME'] - util_df['TO_DATETIME']
    df = util_df.drop(columns=['TO_DATE', 'TO_TIME (UTC)', 'LAND_DATE', 'LAND_TIME (UTC)'])

    return df

def get_mon_util_df():
    mon_util_df = pd.read_csv("./db/monthly_util.csv")
    mon_util_df['END_DATE'] = pd.to_datetime(mon_util_df['END_DATE'])
    mon_util_df = mon_util_df.set_index('END_DATE')

    def durrToMin(x):
        x = x.split(':')
        total_min = int(x[0]) + int(x[1])/60
        return total_min

    mon_util_df['TAH_START'] = mon_util_df['TAH_START'].apply(lambda x: durrToMin(x))
    mon_util_df['TAH_END'] = mon_util_df['TAH_END'].apply(lambda x: durrToMin(x))
    mon_util_df['TAH_PERIOD'] = mon_util_df['TAH_PERIOD'].apply(lambda x: durrToMin(x))

    return mon_util_df


### TECHLOG
def get_techlog_df():
    techlog_raw = pd.read_csv("./db/TECHLOG.csv")
    techlog_raw['DATE'] = pd.to_datetime(techlog_raw['DATE'], format="%Y-%m-%d")
    techlog_raw['ATA'] = techlog_raw['ATA'].astype("category")
    df = techlog_raw

    return df

### Current month's systems reliability (PIREP, MAREP)
def get_mon_pirep(top5=False):
    raw = pd.read_csv("./db/sys_rel.csv", low_memory=False)
    raw['Start'] = pd.to_datetime(raw['Start'])
    raw['End'] = pd.to_datetime(raw['End'])
    raw['ATA - Description'] = raw['ATA'].astype('str') +" - "+ raw['Description']
    df = raw[raw['Start'].dt.month == datetime.now().month].drop(columns=['ATA', 'Description'])

    if top5:
        top5_pirep = df.sort_values('Pir.Rate', ascending=False).head(5)
        return top5_pirep
    else:
        return df

### PIREP
def get_pirep_df(top5=False):
    util_df = get_util_df()
    techlog_raw = get_techlog_df()

    pirep_tbl = techlog_raw[techlog_raw['PM'] == "PIREP"].groupby(['ATA',pd.Grouper(key='DATE', freq='M')])[['PM']].count()
    mon_hrs = util_df.groupby(pd.Grouper(key='TO_DATETIME', freq='M'))[['FL_DURR']].sum()
    mon_hrs['FL_DURR'] = mon_hrs['FL_DURR'].apply(lambda x: x.total_seconds()/3600)

    last12M = (datetime.now() - relativedelta(months=+12))
    thisM = datetime.now()
    last12M_filter = idx[:,last12M:thisM,:] # last 12 month slice
    ata_index = pirep_tbl.index.get_level_values(0).unique()
    date_index = pirep_tbl.index.get_level_values(1).unique()
    period = len(pirep_tbl.loc[last12M_filter].index.get_level_values(1).unique()) # Period length

    pirrate_list = []
    for ind in ata_index:
        for d_ind in date_index:
            pirrate_list.extend(pirep_tbl.loc[idx[ind,d_ind]]['PM'] / (mon_hrs.loc[d_ind]/10)) # The PIREP rate per 10 hrs per month

    pirep_tbl['PIR_RATE'] = pirrate_list

    # Sum of PIREP per ATA for 12-month period
    sum_pirep = [pirep_tbl.loc[idx[ind,last12M:thisM],'PM'].sum() for ind in ata_index]
    sum_pirep = pd.Series(sum_pirep, index=ata_index)

    # Sum of PIREP rate per ATA for the last 12 months
    sum_pirrate = [pirep_tbl.loc[idx[ind,last12M:thisM],'PIR_RATE'].sum() for ind in ata_index]
    sum_pirrate = pd.Series(sum_pirrate, index=ata_index)

    # Mean PIREPS of each ATA for 12-month period
    mean = sum_pirrate / period

    sq_diff = []

    for ind in ata_index:
        sq_diff.extend((pirep_tbl.loc[ind,'PIR_RATE'].values - mean.loc[ind])**2)

    pirep_tbl['sq_diff'] = sq_diff

    # Create UCL table / df
    ucl_tbl = pd.DataFrame(dict(
        ATA=['21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','38','46','49','51','52','54','56','70','71','73','74','75','77'],
        Description=['AIR CONDITIONING', 'AUTO FLIGHT', 'COMMUNICATIONS', 'ELECTRICAL POWER', 'EQUIPMENT/FURNISHING', 'FIRE PROTECTION', 'FLIGHT CONTROLS', 'FUEL', 'HYDRAULIC POWER', 'ICE & RAIN PROTECTION', 'INDICATING / RECORDING SYSTEMS', 'LANDING GEAR', 'LIGHTS', 'NAVIGATION', 'OXYGEN', 'PNEUMATIC', 'WATER / WASTE', 'INFORMATION SYSTEMS', 'AIRBORNE AUXILIARY POWER', 'STANDARDS PRACTICES & STRUCTURE', 'DOORS', 'NACELLES / PYLONS', 'WINDOWS', ' STANDARD PRACTICES & ENGINE', 'POWER PLANT', 'ENGINE FUEL & CONTROL', 'IGNITION', 'ENGINE AIR', 'ENGINE INDICATING'],
        PIREPs=[None]*29,
        PIRRATE_12mth=[None]*29,
        UCL=[None]*29)).set_index('ATA')

    for ind in ata_index:
        ucl = mean[ind] + 2.75*np.sqrt(pirep_tbl.loc[ind,'sq_diff'].sum() / (period-1))
        ucl_tbl['PIREPs'].loc[ind] = sum_pirep.loc[ind]
        ucl_tbl['PIRRATE_12mth'] = ucl_tbl['PIREPs'] / mon_hrs[last12M:thisM]['FL_DURR'].sum()
        ucl_tbl['UCL'].loc[ind] = ucl

    if top5:
        alert = ucl_tbl[ucl_tbl['PIRRATE_12mth'] > ucl_tbl['UCL']]

        if len(alert) > 0:
            top5_tbl = ucl_tbl.sort_values('PIRRATE_12mth', ascending=False).head(5)
        else:
            top5_tbl = ucl_tbl.sort_values('PIREPs', ascending=False).head(5)

        return top5_tbl

    else:
        return ucl_tbl

### FLUIDS
def get_fluids_df():
    techlog_raw = get_techlog_df()
    util_df = get_util_df()

    fluids = techlog_raw[['AC_REG', 'DATE', 'ENG1_OIL', 'ENG2_OIL', 'APU_OIL', 'IDG1_OIL','G_HYD','B_HYD','Y_HYD']].dropna()
    fluids_3day = fluids.groupby(['AC_REG',pd.Grouper(key='DATE',freq='3D')]).sum()
    hrs_3day = util_df.groupby(['AC_REG', pd.Grouper(key='TO_DATETIME', freq='3D',)])[['FL_DURR']].sum()
    hrs_3day['FL_DURR'] = hrs_3day['FL_DURR']/np.timedelta64(1,'s')/3600

    eng1_consum= fluids_3day[fluids_3day['ENG1_OIL']>0][['ENG1_OIL']]
    eng2_consum= fluids_3day[fluids_3day['ENG2_OIL']>0][['ENG2_OIL']]

    list1 = []
    list2 = []
    for reg in eng1_consum.index.get_level_values(0).unique():
        hrs_per_reg = hrs_3day.loc[reg].asfreq('3D', method='ffill')
        for date in eng1_consum.loc[reg].index.get_level_values(0).unique():
            list1.append(eng1_consum.loc[idx[reg,date]]['ENG1_OIL'] / hrs_per_reg.loc[date]['FL_DURR'])

    for reg in eng2_consum.index.get_level_values(0).unique():
        hrs_per_reg = hrs_3day.loc[reg].asfreq('3D', method='ffill')
        for date in eng2_consum.loc[reg].index.get_level_values(0).unique():
            list2.append(eng2_consum.loc[idx[reg,date]]['ENG2_OIL'] / hrs_per_reg.loc[date]['FL_DURR'])

    eng1_consum['ENG1_OIL_QTZ/FH'] = list1
    eng2_consum['ENG2_OIL_QTZ/FH'] = list2
    consum_summary = eng1_consum.join(eng2_consum, how='outer')
    consum_summary = consum_summary.interpolate('linear')

    return consum_summary


