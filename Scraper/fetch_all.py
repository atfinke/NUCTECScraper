import multiprocessing
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


def mp_worker((subjects, delay)):
    sleep(int(delay))

    # Driver
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('permissions.default.image', 2)
    firefox_profile.set_preference(
        'dom.ipc.plugins.enabled.libflashplayer.so', 'false')

    driver = webdriver.Firefox(
        firefox_profile=firefox_profile, executable_path="/usr/local/bin/geckodriver")
    driver.set_window_size(1000, 1000)

    # Authenticate
    authenticate(driver, args.NetID, args.Password)

    name = "Driver-" + str(delay)
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
    logger.info(subjects)

    for subject in subjects:

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
            print("Skipping " + subject)

    driver.quit()


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


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

    subjects = "ANTHRO,ARABIC,ART,ART_HIST,ASIAN_AM,ASIAN_LC,ASIAN_ST,ASTRON,BIOL_SCI,BMD_ENG,BUS_INST,CAT,CFS,CHEM,CHEM_ENG,CHINESE,CHRCH_MU,CIV_ENG,CIV_ENV,CLASSICS,CMN,COG_SCI,COMM_SCI,COMM_ST,COMP_LIT,COMP_SCI,CONDUCT,COOP,CRDV,CSD,DANCE,DSGN,EARTH,ECE,ECON,EDIT,EECS,ENGLISH,ENTREP,ENVR_POL,ENVR_SCI,ES_APPM,EUR_ST,EUR_TH,FRENCH,GBL_HLTH,GEN_CMN,GEN_ENG,GEN_LA,GEN_MUS,GEN_SPCH,GEOG,GEOL_SCI,GERMAN,GNDR_ST,GREEK,HDPS,HEBREW,HINDI,HIND_URD,HISTORY,HUM,IDEA,IEMS,IMC,INTG_ART,INTG_SCI,INTL_ST,ISEN,ITALIAN,JAPANESE,JAZZ_ST,JOUR,JWSH_ST,KELLG_FE,KELLG_MA,KOREAN,LATIN,LATINO,LATIN_AM,LDRSHP,LEGAL_ST,LING,LOC,LRN_DIS,MATH,MAT_SCI,MECH_ENG,MENA,MFG_ENG,MMSS,MUSIC,MUSICOL,MUSIC_ED,MUS_COMP,MUS_TECH,MUS_THRY,NEUROSCI,PERF_ST,PERSIAN,PHIL,PHYSICS,PIANO,POLI_SCI,PORT,PRDV,PSYCH,RELIGION,RTVF,SESP,SHC,SLAVIC,SOCIOL,SOC_POL,SPANISH,SPCH,STAT,STRINGS,SWAHILI,TEACH_ED,THEATRE,TRANS,TURKISH,URBAN_ST,VOICE,WIND_PER,WM_ST,WRITING,YIDDISH".split(
        ',')

    driver_count = 1
    chunk_size = int(math.ceil(float(len(subjects)) / float(driver_count)))
    split_subjects = [subjects[i:i + chunk_size]
                      for i in xrange(0, len(subjects), chunk_size)]

    data = []
    delay = 5
    for subject_split in split_subjects:
        subject_data = [subject_split, delay]
        delay += 5
        data.append(subject_data)

    p = multiprocessing.Pool(driver_count)
    p.map(mp_worker, data)
