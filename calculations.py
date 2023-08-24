from datetime import datetime

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta

from dataframes import get_df, get_dr


def get_dr_ytd():
    """
    Function to get the YTD dispatch reliability
    """
    df = get_dr(ytd=True)

    fc = df["TAC acc."].sum()
    dels = df["Delays"].sum()
    ytdDR = ((fc - dels) / fc) * 100

    return ytdDR


def get_cotd_ytd():
    """
    Function to get the YTD contribution of technical delays
    """
    df = get_dr(ytd=True, technical=False)

    cotdYTD = df["Delays"].sum() / df["TAC acc."].sum()

    return round(cotdYTD, 4)


def get_FHFC_tot():
    """
    Function to calculate the total fleet hours (FH) and total fleet cycles (FC). No input parameters is required.
    """
    df = get_dr(ytd=True)
    FH = df["TAH acc."].sum()
    FC = df["TAC acc."].sum()

    return FH, FC


def get_tia(month=datetime.now().month - 1, year=datetime.now().year):
    """
    Function that gets the TIA Rate from db
    """

    FH, FC = get_FHFC_tot()
    delays = get_del()

    tia = (delays / FH) * 100

    return tia


def get_del():
    """
    Function that gets the total number of delays
    """
    df = get_dr(ytd=True, technical=True)
    delays = df["Delays"].sum()

    return delays


def get_status():
    """
    Function that gets the status of each aircraft registration
    """
    status = pd.read_csv("./db/CONFIG_DB.csv")[
        [
            "MSN",
            "REGISTRATION",
            "AIRCRAFT TYPE",
            "CURR_TOTAL_HOURS",
            "CURR_TOTAL_CYCLES",
            "STATUS",
            "WEIGHT VARIANT",
        ]
    ]

    return status
