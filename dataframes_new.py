from datetime import datetime
from ftplib import FTP
from io import BytesIO

import numpy as np
import pandas as pd
from pysftp import CnOpts, Connection

from config import host, port, pwd, user

cnOpts = CnOpts()
cnOpts.hostkeys = None


### GET FILE THTOUGH FTP
def get_df(dfname="ac_util.csv"):
    """
    This function creates a pandas dataframe from csv's pulled from the sftp. The dataframe name must be specified:

    aircraft utilization:   ac_util
    fleet utilization:      fleet_util
    component utilization:  comp_util
    mel usage:              mel_use
    mel workorders:         mel_wo
    part removals:          part_rel
    PIREP/MAREP:            sys_rel

    """
    with Connection(host, user, None, pwd, int(port), cnopts=cnOpts) as sftp:
        sftp.cwd("amos_aims_intfc/emr_dash_test")
        with sftp.open(dfname) as f:
            df = pd.read_csv(f)

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
