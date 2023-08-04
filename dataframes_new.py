from datetime import datetime
from ftplib import FTP
from io import BytesIO

import numpy as np
import pandas as pd

from config import host, port, pwd, user


### GET FILE THTOUGH FTP
def get_df(dfname=None):
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

    ftp = FTP(timeout=20)
    ftp.connect("103.126.58.35", 2222)
    ftp.login("user", "asdQJ!@341!")
    ftp.cwd("amos_aims_intfc/emr_dash_test")
    file = BytesIO()
    # Store the retrieved file as binary in memory
    ftp.retrbinary(f"RETR {dfname}.csv", file.write)
    # Get the very first stream position
    file.seek(0)
    df = pd.read_csv(file)
    ftp.quit()

    return df


def fleet_regs():
    ac_list = get_df("ac_util")["A/C"].sort_values(ascending=True).tolist()

    return ac_list
