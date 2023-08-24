from datetime import datetime
from ftplib import FTP
from io import BytesIO

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from pysftp import CnOpts, Connection

from config import host, port, pwd, user

cnOpts = CnOpts()
cnOpts.hostkeys = None


### GET FILE THTOUGH FTP
def get_df(dfname=None, usecols=None):
    """
    This function creates a pandas dataframe from csv's pulled from the sftp. The dataframe name must be specified:

    aircraft utilization:   ac_util
    fleet utilization:      fleet_util
    engine utilization:     eng_util
    apu utilization:        apu_util
    component utilization:  comp_util
    mel usage:              mel_use
    mel workorders:         mel_wo
    part removals:          part_rel
    PIREP/MAREP:            sys_rel

    """
    with Connection(host, user, None, pwd, int(port), cnopts=cnOpts) as sftp:
        sftp.cwd("amos_aims_intfc/emr_dash_test")
        with sftp.open(dfname) as f:
            df = pd.read_csv(f, usecols=usecols)

    return df


### AIRCRFAT REGISTRATIONS IN THE FLEET
def fleet_regs():
    ac_list = get_df("ac_util.csv")["A/C"].sort_values(ascending=True).tolist()

    return ac_list


### NUMBER OF DEPARTURES FROM EACH CITY
def get_deps(period=3, regs=[]):
    coord = pd.read_csv("db/idn_cities.csv")
    flights = (
        pd.read_csv(
            "db/ac_legs.csv", usecols=["A/C", "Serv.Type", "Dep.", "Arr.", "Dep. Date"]
        )
        .replace({"KNO": "DPS", " ": np.nan})
        .dropna(subset=["Serv.Type", "Dep."])
    )

    # Filter
    flights["Dep. Date"] = pd.to_datetime(flights["Dep. Date"], format="%d.%b.%Y")
    queryPeriod = (flights["Dep. Date"].dt.month > datetime.now().month - period) & (
        flights["Dep. Date"].dt.year == datetime.now().year
    )
    queryRegs = flights["A/C"].isin(regs)

    flights = flights[queryPeriod & queryRegs]

    flights = (
        flights[flights["Serv.Type"] == "J"]
        .groupby(by="Dep.")
        .count()
        .reset_index()
        .replace(
            {
                "Dep.": {
                    "CGK": "Jakarta",
                    "DPS": "Denpasar",
                    "SUB": "Surabaya",
                    "YIA": "Yogyakarta",
                    "BDJ": "Banjarmasin",
                    "BPN": "Balikpapan",
                    "PDG": "Padang",
                    "PKU": "Pekanbaru",
                    "PLM": "Palembang",
                    "PNK": "Pontianak",
                }
            }
        )
    )
    flights = flights.rename(columns={"Dep.": "city"})

    coord = coord.merge(flights, how="right")

    return coord


### MONTHLY TECH. DR DATAFRAME
def get_dr(period=None, ytd=False, technical=True):
    """
    Function to calculate the dispatch reliability for a given period.
    """

    df0 = get_df(
        "fleet_util.csv", usecols=["Start", "TAH acc.", "TAC acc."]
    )  # Get monthly fleet utilization (FC)
    df0["Start"] = pd.to_datetime(df0["Start"])
    cycs = df0.set_index("Start").to_period(
        "M"
    )  # The cycles dataframe is index by monthly period

    df1 = get_df("delays.csv", usecols=["A/C", "Date", "Int. Code"])  # Get delays data
    df1["Date"] = pd.to_datetime(df1["Date"])
    dels = df1.set_index("Date").to_period(
        "M"
    )  # Index the delay dataframe by monthly period

    if technical:
        dels = dels[dels["Int. Code"] != 93]  # Only account for initial 4X delay codes

    dels = (
        dels.groupby(level=0)[["Int. Code"]]
        .count()
        .rename(columns={"Int. Code": "Delays"})
    )  # Group and count the delays in monthly period

    dr = cycs.merge(dels, "left", left_index=True, right_index=True).fillna(0)
    rel = []
    for row in dr.itertuples(index=False):
        rel.append(
            round((row[1] - row[2]) * 100 / row[1], 2)
        )  # Calculate the DR (rounded to 2 decimal) and append to the list

    dr["dr"] = rel  # Add the monthly DR list into the dataframe

    # Period filters
    now = f"{datetime.now().year}" + "-" + f"{datetime.now().month-1}"
    if ytd:
        last = f"{datetime.now().year}" + "-1"
    else:
        past = datetime.now() - relativedelta(months=period)
        last = f"{past.year}" + "-" + f"{past.month}"

    return dr.loc[last:now, :]


### MONTHLY APU UTIL DATAFRAME
def get_apu(period):
    get_df(
        "apu_util.csv",
        usecols=["Start", "A/C", "S/N", "APU Cycle Diff", "APU Hours Diff"],
    )
