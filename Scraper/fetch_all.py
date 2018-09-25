from time import sleep
import math

import logging
import os
import argparse

from selenium import webdriver
from selenium.webdriver import ActionChains

from authcaesar import authenticate
from main import wait
from main import fetchSubjectCTECs
from dicttocsv import saveDictionariesToCSV

from extendedscrapbluectec import scrapLoadedCTECPage
from datetime import datetime

from Queue import Queue
from threading import Thread

q = Queue(maxsize=0)
num_drivers = 5

def mp_worker(delay):
    sleep(int(delay))

    # Driver
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('permissions.default.image', 2)
    firefox_profile.set_preference(
        'dom.ipc.plugins.enabled.libflashplayer.so', 'false')

    # driver = webdriver.Firefox(firefox_profile=firefox_profile, executable_path="/usr/local/bin/geckodriver")
    driver = webdriver.Firefox(executable_path="/usr/local/bin/geckodriver")

    driver.set_window_size(1000, 1000)

    # Authenticate
    authenticate(driver, args.NetID, args.Password)

    name = "Driver-" + str(datetime.now().strftime('%H_%M_%S'))
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # create a file handler
    handler = logging.FileHandler("output/logs/" + name + '.log', mode='w')
    handler.setLevel(logging.INFO)
    # create a logging format
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)8s] --- %(message)s", "%H:%M:%S")
    handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)

    while True:
        subject = q.get()

        attempts = 0
        while attempts < 4:
            attempts += 1
            url = "https://caesar.ent.northwestern.edu/"
            driver.get(url)
            wait(driver, 'PTNUI_LAND_WRK_GROUPBOX14$PIMG', 15)

            # try to overcome peoplesoft timeout
            ActionChains(driver).move_by_offset(50, 50).perform()

            scrappedCTECs = fetchSubjectCTECs(driver, logger, subject)
            if scrappedCTECs:
                saveDictionariesToCSV(scrappedCTECs, subject + "-CTECs")
                break
            sleep(5)
        if attempts == 4:
            logger.error("Skipping " + subject)
        q.task_done()

    driver.quit()
    print("Driver Done")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser._action_groups.pop()

    required = parser.add_argument_group('required arguments')
    required.add_argument("-n", "--NetID", type=str)
    required.add_argument("-p", "--Password", type=str)

    args = parser.parse_args()

    if args.NetID is None:
        raise ValueError("NetID requried.")
    elif args.Password is None:
        raise ValueError("Password requried.")

    if not os.path.exists("output"):
        os.makedirs("output")

    if not os.path.exists("output/logs"):
        os.makedirs("output/logs")

    subject_string = "ANTHRO,ARABIC,ART,ART_HIST,ASIAN_AM,ASIAN_LC,ASIAN_ST,ASTRON,BIOL_SCI,BMD_ENG,BUS_INST,CAT,CFS,CHEM,CHEM_ENG,CHINESE"
    subject_string += ",CHRCH_MU,CIV_ENG,CIV_ENV,CLASSICS,CMN,COG_SCI,COMM_SCI,COMM_ST,COMP_LIT,COMP_SCI,CONDUCT,COOP,CRDV,CSD,DANCE,DSGN,EARTH"
    subject_string += ",ECE,ECON,EDIT,EECS,ENGLISH,ENTREP,ENVR_POL,ENVR_SCI,ES_APPM,EUR_ST,EUR_TH,FRENCH,GBL_HLTH,GEN_CMN,GEN_ENG,GEN_LA,GEN_MUS,GEN_SPCH"

    subject_string += ",GEOG,GEOL_SCI,GERMAN,GNDR_ST,GREEK,HDPS,HEBREW,HINDI,HIND_URD,HISTORY,HUM,IDEA,IEMS,IMC,INTG_ART,INTG_SCI,INTL_ST,ISEN,ITALIAN,JAPANESE"
    subject_string += ",JAZZ_ST,JOUR,JWSH_ST,KELLG_FE,KELLG_MA,KOREAN,LATIN,LATINO,LATIN_AM,LDRSHP,LEGAL_ST,LING,LOC,LRN_DIS,MATH,MAT_SCI,MECH_ENG,MENA,MFG_ENG,MMSS"
    subject_string += ",MUSIC,MUSICOL,MUSIC_ED,MUS_COMP,MUS_TECH,MUS_THRY,NEUROSCI,PERF_ST,PERSIAN,PHIL,PHYSICS,PIANO,POLI_SCI,PORT,PRDV,PSYCH,RELIGION,RTVF,SESP"
    subject_string += ",SHC,SLAVIC,SOCIOL,SOC_POL,SPANISH,SPCH,STAT,STRINGS,SWAHILI,TEACH_ED,THEATRE,TRANS,TURKISH,URBAN_ST,VOICE,WIND_PER,WM_ST,WRITING,YIDDISH"

    # subject_string = "AAL,ACCT,AFST,AF_AM_ST,ANIM_ART,ANTHRO,ART,ART_HIST,ASIAN_LC,ASTRON,AUD,BIOETHIC,BIOL_SCI,BMD_ENG,CFS,CHEM,CHEM_ENG,CHSS,CIS,CIV_ENG,CIV_ENV,CLASSICS,CMN,COG_SCI,COMM_SCI,COMM_ST,COMP_LIT,COMP_SCI,CONDUCT,COUN,COUN_PSY,CRD,CRDV,CSD,CSD_INTR,DANCE,DATA_SCI,DECS,DSGN,EARTH,ECE,ECON,EECS"
    # subject_string = "ENGLISH,ENTR,ENTREP,ENVR_POL,EPI_BIO,ES_APPM,FINC,FRENCH,GAMS,GBL_HLTH,GEN_ENG,GEOG,GEOL_SCI,GERMAN,GNDR_ST,GREEK,HDPS,HDSP,HISTORY,HQS,HSIP,HSR,HUM,IBIS,IDEA,IEMS,IGP,INTL,IPLS,ISEN,ITALIAN,LATIN,LATINO,LATIN_AM,LING,LIT,LOC,LRN_DIS,LRN_SCI,MATH,MAT_SCI,MCW,MDVL_ST,MECH_ENG,MECN,MECS,MEM"
    # subject_string = "MENA,MGMT,MHB,MKTG,MORS,MPPA,MSC,MSCI,MSTP,MS_ED,MS_FT,MTS,MUSICOL,MUSIC_ED,MUS_COMP,MUS_GRD,MUS_TECH,MUS_THRY,NEUROBIO,NEUROSCI,NUIN,OPNS,PBC,PERF_ST,PHIL,PHYSICS,POLI_SCI,PORT,PROJ_MGT,PSYCH,PUB_HLTH,RELIGION,REPR_SCI,RTVF,SEEK,SESP,SLAVIC,SOCIOL,SOC_POL,SPANISH,SPANPORT,SPCH_LNG,STAT,STRINGS,TEACH_ED,TGS,TH&DRAMA,THEATRE,VOICE,WIND_PER,WM_ST,WRITING"

    for x in subject_string.split(','):
        q.put(x)

    for i in range(num_drivers):
        worker = Thread(target=mp_worker, args=(i * 7,))
        worker.setDaemon(True)
        worker.start()

    q.join()
