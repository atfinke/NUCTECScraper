import math

import logging
import os
import argparse

from datetime import datetime
from queue import Queue
from time import sleep
from threading import Thread

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.firefox.options import Options

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import model
import casear_navigation
from caesar_authentication import authenticate
from bluera_ctec_scraper import scrape_loaded_ctec_page
from caesar_scraper import scrape_subject_ctecs

q = Queue(maxsize=0)
num_drivers = 3

career = "UGRD"

def notify(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))

def mp_worker(delay):
    sleep(int(delay))

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

    # Driver
    options = Options()
    # options.set_headless(True)

    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('permissions.default.image', 2)

    driver = webdriver.Firefox(options=options,firefox_profile=firefox_profile, executable_path="/usr/local/bin/geckodriver")
    driver.set_window_size(1000, 1000)

    # Authenticate
    authenticate(driver, logger, args.NetID, args.Password)

    while True:
        subject = q.get()
        logger.info("Starting " + subject)

        attempts = 0
        while attempts < 4:
            attempts += 1

            try:
                casear_navigation.open_main_page(driver)
            except Exception as e:
                logger.error("Failed to open main page")
                logger.error("ERROR INFO - " + str(e) + "\n")
                sleep(5)
                continue
            # try to overcome peoplesoft timeout
            ActionChains(driver).move_by_offset(50, 50).perform()


            try:
                scrapped_ctecs = scrape_subject_ctecs(driver, logger, career, subject)
            except Exception as e:
                logger.error("Failed to scrape subject ctecs")
                logger.error("ERROR INFO - " + str(e) + "\n")
                sleep(5)
                continue

            if scrapped_ctecs:
                save_ctecs_to_db(scrapped_ctecs, logger, subject)
                break
            sleep(5)
        if attempts == 4:
            logger.error("Skipping " + subject)
        q.task_done()

    driver.quit()
    logger.info("Driver Done")

def save_ctecs_to_db(ctecs, logger, subject):
    saved_count = 0
    for ctec in ctecs:
        try:
            obj = model.CTEC(ctec)
            logger.info("saving to db: " + str(obj.report_caesar_title))
            try:
                session.add(obj)
                session.commit()
                saved_count += 1
            except Exception as e:
                error = str(e)
                if "UNIQUE constraint failed" in error:
                    logger.info("already in db")
                else:
                    logger.error("Failed to add CTEC to db")
                    logger.error("ERROR INFO - " + error + "\n")
                    notify("NUCTECScraper", "Failed to add CTEC object: " + str(obj.report_caesar_title))
                session.rollback()
        except Exception as e:
            logger.error("Failed to create CTEC object")
            logger.error("ERROR INFO - " + error + "\n")
            notify("NUCTECScraper", "Failed to create CTEC object: " + str(ctec))

    notify("NUCTECScraper", "Saved " + str(saved_count) + " " + subject + " CTECs to DB")
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

    engine = create_engine('sqlite:///' + "output/CTEC.db")
    model.Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

# Undergraduate
    subject_string = "ANTHRO,ARABIC,ART,ART_HIST,ASIAN_AM,ASIAN_LC,ASIAN_ST,ASTRON,BIOL_SCI,BMD_ENG,BUS_INST,CAT,CFS,CHEM,CHEM_ENG,CHINESE"
    subject_string += ",CHRCH_MU,CIV_ENG,CIV_ENV,CLASSICS,CMN,COG_SCI,COMM_SCI,COMM_ST,COMP_LIT,COMP_SCI,CONDUCT,COOP,CRDV,CSD,DANCE,DSGN,EARTH"
    subject_string += ",ECE,ECON,EDIT,EECS,ENGLISH,ENTREP,ENVR_POL,ENVR_SCI,ES_APPM,EUR_ST,EUR_TH,FRENCH,GBL_HLTH,GEN_CMN,GEN_ENG,GEN_LA,GEN_MUS,GEN_SPCH"
    subject_string += ",GEOG,GEOL_SCI,GERMAN,GNDR_ST,GREEK,HDPS,HEBREW,HINDI,HIND_URD,HISTORY,HUM,IDEA,IEMS,IMC,INTG_ART,INTG_SCI,INTL_ST,ISEN,ITALIAN,JAPANESE"
    subject_string += ",JAZZ_ST,JOUR,JWSH_ST,KELLG_FE,KELLG_MA,KOREAN,LATIN,LATINO,LATIN_AM,LDRSHP,LEGAL_ST,LING,LOC,LRN_DIS,MATH,MAT_SCI,MECH_ENG,MENA,MFG_ENG,MMSS"
    subject_string += ",MUSIC,MUSICOL,MUSIC_ED,MUS_COMP,MUS_TECH,MUS_THRY,NEUROSCI,PERF_ST,PERSIAN,PHIL,PHYSICS,PIANO,POLI_SCI,PORT,PRDV,PSYCH,RELIGION,RTVF,SESP"
    subject_string += ",SHC,SLAVIC,SOCIOL,SOC_POL,SPANISH,STAT,STRINGS,SWAHILI,TEACH_ED,THEATRE,TRANS,TURKISH,URBAN_ST,VOICE,WIND_PER,WM_ST,WRITING,YIDDISH"


# Graduate
    # subject_string = "AAL,ACCT,AFST,AF_AM_ST,ANIM_ART,ANTHRO,ART,ART_HIST,ASIAN_LC,ASTRON,AUD,BIOETHIC,BIOL_SCI,BMD_ENG,CFS,CHEM,CHEM_ENG,CHSS,CIS,CIV_ENG,CIV_ENV,CLASSICS,CMN,COG_SCI,COMM_SCI,COMM_ST,COMP_LIT,COMP_SCI,CONDUCT,COUN,COUN_PSY,CRD,CRDV,CSD,CSD_INTR,DANCE,DATA_SCI,DECS,DSGN,EARTH,ECE,ECON,EECS"
    # subject_string = "ENGLISH,ENTR,ENTREP,ENVR_POL,EPI_BIO,ES_APPM,FINC,FRENCH,GAMS,GBL_HLTH,GEN_ENG,GEOG,GEOL_SCI,GERMAN,GNDR_ST,GREEK,HDPS,HDSP,HISTORY,HQS,HSIP,HSR,HUM,IBIS,IDEA,IEMS,IGP,INTL,IPLS,ISEN,ITALIAN,LATIN,LATINO,LATIN_AM,LING,LIT,LOC,LRN_DIS,LRN_SCI,MATH,MAT_SCI,MCW,MDVL_ST,MECH_ENG,MECN,MECS,MEM"
    # subject_string = "MENA,MGMT,MHB,MKTG,MORS,MPPA,MSC,MSCI,MSTP,MS_ED,MS_FT,MTS,MUSICOL,MUSIC_ED,MUS_COMP,MUS_GRD,MUS_TECH,MUS_THRY,NEUROBIO,NEUROSCI,NUIN,OPNS,PBC,PERF_ST,PHIL,PHYSICS,POLI_SCI,PORT,PROJ_MGT,PSYCH,PUB_HLTH,RELIGION,REPR_SCI,RTVF,SEEK,SESP,SLAVIC,SOCIOL,SOC_POL,SPANISH,SPANPORT,SPCH_LNG,STAT,STRINGS,TEACH_ED,TGS,TH&DRAMA,THEATRE,VOICE,WIND_PER,WM_ST,WRITING"

    # subject_string = "ASTRON,IEMS,DSGN,EECS"

    for x in subject_string.split(','):
        q.put(x)

    for i in range(num_drivers):
        worker = Thread(target=mp_worker, args=(i * 14,))
        worker.setDaemon(True)
        worker.start()

    q.join()
