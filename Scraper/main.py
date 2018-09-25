import urllib2
import argparse

import logging
import os

from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains


from authcaesar import authenticate
from extendedscrapbluectec import scrapLoadedCTECPage
from dicttocsv import saveDictionariesToCSV

spacer = "   "


def wait(driver, elementID, delay):
    try:
        myElem = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.ID, elementID)))
        return myElem
    except TimeoutException:
        print "Loading took too much time!"


def fetchSubjectCTECs(driver, logger, subject):
    logger.info("=============")

    try:
        sleep(1)
        logger.info("Main Page -> Click Manage Classes")
        mainPageManageClassesButton = wait(
            driver, 'PTNUI_LAND_REC14$0_row_8', 15)
        mainPageManageClassesButton.click()

        logger.info("Manage Classes Page -> Click Search CTECs")
        classesPageCTECRow = wait(
            driver, 'PTGP_STEP_DVW_PTGP_STEP_LABEL$7', 15)
        sleep(5)
        classesPageCTECRow.click()

        logger.info(spacer + "Waiting for careers to load")
        delay = 15
        try:
            careerSelectorDropdown = WebDriverWait(driver, delay).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#NW_CT_PB_SRCH_ACAD_CAREER')))
        except TimeoutException:
            logger.error("Loading took too much time!")

        # TGS or UGRD

        driver.execute_script(
            "document.querySelector('#NW_CT_PB_SRCH_ACAD_CAREER').value = 'UGRD'")
        driver.execute_script(
            "document.querySelector('#NW_CT_PB_SRCH_ACAD_CAREER').onchange();")

        logger.info(spacer + "Waiting for subjects to load")
        sleep(0.25)
        while driver.execute_script("return document.getElementById('processing').offsetParent == null") == False:
            sleep(0.5)

        subjectSelectorDropdown = driver.find_element_by_css_selector(
            "#NW_CT_PB_SRCH_SUBJECT")
        options = driver.find_elements_by_tag_name("option")
        validClass = False

        for option in options:
            if (option.get_attribute('value') == subject):
                validClass = True

        if (validClass):
            logger.info(spacer + "Found correct class subject")
            driver.execute_script(
                "document.querySelector('#NW_CT_PB_SRCH_SUBJECT').value = '" + subject + "'")
            driver.execute_script(
                "document.querySelector('#NW_CT_PB_SRCH_SUBJECT').onchange();")
        else:
            raise ValueError("Couldn't find subject")
    except Exception as e:
        logger.error(
            subject + ": Something unexpected happened when loading manage classes page, skipping subject")
        logger.error(subject + ": ERROR INFO - " + str(e) + "\n")
        return None

    sleep(1)
    logger.info(spacer + "Waiting for single class results to load")
    driver.execute_script(
        "document.getElementById('NW_CT_PB_SRCH_SRCH_BTN').click();")

    # One off to get past main screen
    try:
        classesPageCTECResultRow = []
        checkCount = 0
        while len(classesPageCTECResultRow) == 0:
            checkCount = checkCount + 1
            links = driver.find_elements_by_class_name("psc_rowact")
            for link in links:
                if "NW_CT_PV_DRV$0_row_" in link.get_attribute('id'):
                    classesPageCTECResultRow.append(link)
                    break
            sleep(0.25)
            if checkCount > 60:
                logger.warning(subject + ": No CTEC results, skipping subject")
                return None
    except Exception as e:
        logger.error(
            subject + ": Something unexpected happened when loading inital CTEC results, skipping subject")
        logger.error(subject + ": ERROR INFO - " + str(e) + "\n")
        return None

    logger.info("Manage Classes Page / CTEC Section -> Click CTEC Result")
    driver.find_element_by_id(
        classesPageCTECResultRow[0].get_attribute('id')).click()
    wait(driver, 'NW_CT_PV4_DRV$0_row_0', 30)

    # Now viewing full ctec view (classes on left, section reviews table on right)
    fullCTECPageClassList = []
    while len(fullCTECPageClassList) == 0:
        links = driver.find_elements_by_class_name("psc_rowact")
        for link in links:
            if "NW_CT_PV_DRV$0_row_" in link.get_attribute('id'):
                fullCTECPageClassList.append(link.get_attribute('id'))
        sleep(0.25)

    logger.info("-------------")
    logger.info(subject + ": Found " +
                str(len(fullCTECPageClassList)) + " classes in sidebar")

    main_window = driver.current_window_handle
    scrappedCTECs = []

    scrappedClasses = 0
    last_class_inner_html = "N/A"

    for class_row_id in fullCTECPageClassList:

        scrappedClasses += 1
        sleep(5)

        attempts = 0
        while attempts < 5:
            attempts += 1

            try:
                # Click on the class on the left sidebar

                class_row_element = driver.find_element_by_id(class_row_id)
                class_row_element.click()
                classNumber = class_row_element.get_attribute(
                    'innerText').split('-')[0]

                logger.info(spacer + subject + " " +
                            str(classNumber) + ": Starting")

                try:
                    ctecs, resultsRowsText = fetchClassCTECs(
                        driver, logger, main_window, subject, classNumber, last_class_inner_html)
                    scrappedCTECs = scrappedCTECs + ctecs

                    if resultsRowsText != "":
                        last_class_inner_html = resultsRowsText

                    break

                except Exception as e:
                    logger.error(spacer + subject + ": Trying class again\n")
                    continue
            except Exception as e:
                logger.error(
                    spacer + subject + ": Something unexpected happened when loading all class CTEC results, skipping class")
                logger.error(spacer + subject +
                             ": ERROR INFO - " + str(e) + "\n")
                continue

        saveDictionariesToCSV(scrappedCTECs, "_TEMP-" + subject + "-CTECs")

        logger.info(spacer + "Subject Progress: " + str(scrappedClasses) +
                    "/" + str(len(fullCTECPageClassList)) + "\n")

    try:
        os.remove("output/_TEMP-" + subject + "-CTECs")
    except:
        pass

    return scrappedCTECs


def fetchClassCTECs(driver, logger, main_window, subject, classNumber, last_class_inner_html):
    sleep(5)

    class_inner_html = ""

    try:
        updatedResults = False
        updatedCheckCount = 0

        logger.info(spacer + spacer + "Waiting 3 seconds to load")
        sleep(3)

        while (updatedResults == False and updatedCheckCount < 10):
            updatedCheckCount += 1

            classCTECResultRow = []
            class_inner_html = ""
            links = driver.find_elements_by_class_name("psc_rowact")
            class_inner_html = driver.find_element_by_id("NW_CT_PUB_RSLT_FL").get_attribute('innerHTML')

            for link in links:
                if "NW_CT_PV4_DRV$0_row_" in link.get_attribute('id'):
                    classCTECResultRow.append(link)

            if class_inner_html != last_class_inner_html and class_inner_html != "":
                updatedResults = True

            else:
                sleep(1)

        if updatedResults == False:
            logger.warning(spacer + spacer +
                           "No CTEC result rows loaded, (same inner html) skipping class" + "\n")
            logger.warning(class_inner_html)

            raise ValueError("no rows found")
        elif updatedCheckCount == 10:
            logger.warning(spacer + spacer +
                           "No CTEC result rows loaded, (timeout) skipping class" + "\n")
            raise ValueError("no rows found")

    except Exception as e:
        logger.error(spacer + spacer +
                     "Something unexpected happened when reading CTEC result rows, skipping class")
        logger.error(spacer + spacer + "ERROR INFO - " + str(e) + "\n")
        raise e

    scrappedRows = 0
    onlyOldResultsLeft = False
    sleep(1)

    new_subject_CTECs = []

    for resultRow in classCTECResultRow:
        if onlyOldResultsLeft:
            break

        try:
            scrappedRows += 1

            name = driver.find_element_by_id(
                "MYDESCR$" + str(scrappedRows - 1)).get_attribute("innerText")

            instructor = driver.find_element_by_id(
                "CTEC_INSTRUCTOR$" + str(scrappedRows - 1)).get_attribute("innerText")

            driver.execute_script(
                "document.getElementById('" + resultRow.get_attribute('id') + "').click();")
            WebDriverWait(driver, 10).until(
                lambda d: len(d.window_handles) == 2)
        except Exception as e:
            logger.error(
                spacer + spacer + "Something unexpected happened when clicking a CTEC result row, skipping row")
            logger.error(spacer + spacer + "ERROR INFO - " + str(e) + "\n")
            sleep(2)
            continue

        onCTECTab = False
        validBluePage = False

        while onCTECTab == False:
            for handle in driver.window_handles:
                driver.switch_to.window(handle)
                sleep(0.5)
                if "Northwestern - " in driver.title:
                    onCTECTab = True
                    validBluePage = True
                    break
                elif "NU:" in driver.title:
                    onCTECTab = True
                    validBluePage = False
                    break
                elif "NU CTEC Published Reports" in driver.title:
                    if handle != main_window:
                        onCTECTab = True
                        validBluePage = False
                        onlyOldResultsLeft = True
                        break

        if validBluePage:
            delay = 30
            try:
                myElem = WebDriverWait(driver, delay).until(
                    EC.presence_of_element_located((By.ID, 'reportView')))
            except TimeoutException:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                logger.error("Loading took too much time!")
                continue

            scrap = scrapLoadedCTECPage(driver)
            if len(scrap) > 1:
                scrap["report_caesar_title"] = name.replace(",", "|")
                scrap["report_caesar_instructor"] = instructor
                scrap["report_caesar_subject"] = subject

                # The Graduate School or Undergraduate
                scrap["report_caesar_career"] = "Undergraduate"
                scrap["report_caesar_class_number"] = classNumber
                new_subject_CTECs.append(scrap)
            else:
                logger.warning(spacer + spacer +
                               spacer + "CTEC page empty")

            logger.info(spacer + spacer + "Class Progress: " +
                        str(scrappedRows) + "/" + str(len(classCTECResultRow)))
        elif onlyOldResultsLeft:
            logger.info(spacer + spacer +
                        "Only old CTECs left, skipping the rest")
        else:
            logger.warning(spacer + spacer +
                           "Invalid CTEC Page (Probably the bluera homepage)")
            logger.info(spacer + spacer + "Class Progress: " +
                        str(scrappedRows) + "/" + str(len(classCTECResultRow)))

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    if len(new_subject_CTECs) == 0:
        raise ValueError("no ctecs found")

    return new_subject_CTECs, class_inner_html


if __name__ == "__main__":

    # Arg Parse
    parser = argparse.ArgumentParser()
    parser._action_groups.pop()

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument("-s", '--Subjects', type=str,
                          help='Subjects in Caesar. Case-sensitive, comma seperated (i.e. "MATH,CHEM")')

    required.add_argument("-n", "--NetID", type=str)
    required.add_argument("-p", "--Password", type=str)

    args = parser.parse_args()

    if args.NetID is None:
        raise ValueError("NetID requried.")
    elif args.Password is None:
        raise ValueError("Password requried.")

    subjects = []
    if args.Subjects is not None:
        if args.Subjects == "ALL":
            subjects = "ANTHRO,ARABIC,ART,ART_HIST,ASIAN_AM,ASIAN_LC,ASIAN_ST,ASTRON,BIOL_SCI,BMD_ENG,BUS_INST,CAT,CFS,CHEM,CHEM_ENG,CHINESE,CHRCH_MU,CIV_ENG,CIV_ENV,CLASSICS,CMN,COG_SCI,COMM_SCI,COMM_ST,COMP_LIT,COMP_SCI,CONDUCT,COOP,CRDV,CSD,DANCE,DSGN,EARTH,ECE,ECON,EDIT,EECS,ENGLISH,ENTREP,ENVR_POL,ENVR_SCI,ES_APPM,EUR_ST,EUR_TH,FRENCH,GBL_HLTH,GEN_CMN,GEN_ENG,GEN_LA,GEN_MUS,GEN_SPCH,GEOG,GEOL_SCI,GERMAN,GNDR_ST,GREEK,HDPS,HEBREW,HINDI,HIND_URD,HISTORY,HUM,IDEA,IEMS,IMC,INTG_ART,INTG_SCI,INTL_ST,ISEN,ITALIAN,JAPANESE,JAZZ_ST,JOUR,JWSH_ST,KELLG_FE,KELLG_MA,KOREAN,LATIN,LATINO,LATIN_AM,LDRSHP,LEGAL_ST,LING,LOC,LRN_DIS,MATH,MAT_SCI,MECH_ENG,MENA,MFG_ENG,MMSS,MUSIC,MUSICOL,MUSIC_ED,MUS_COMP,MUS_TECH,MUS_THRY,NEUROSCI,PERF_ST,PERSIAN,PHIL,PHYSICS,PIANO,POLI_SCI,PORT,PRDV,PSYCH,RELIGION,RTVF,SESP,SHC,SLAVIC,SOCIOL,SOC_POL,SPANISH,SPCH,STAT,STRINGS,SWAHILI,TEACH_ED,THEATRE,TRANS,TURKISH,URBAN_ST,VOICE,WIND_PER,WM_ST,WRITING,YIDDISH".split(
                ',')
        else:
            subjects = args.Subjects.split(',')
    else:
        raise ValueError("Must specify -s in Subject Fetch")

    # Driver
    driver = webdriver.Firefox(executable_path="/usr/local/bin/geckodriver")
    driver.set_window_size(1000, 1000)

    # Authenticate
    authenticate(driver, args.NetID, args.Password)

    for subject in subjects:
        url = "https://caesar.ent.northwestern.edu/"
        driver.get(url)
        wait(driver, 'PTNUI_LAND_WRK_GROUPBOX14$PIMG', 15)

        # try to overcome peoplesoft timeout
        ActionChains(driver).move_by_offset(50, 50).perform()

        scrappedCTECs = fetchSubjectCTECs(driver, subject)
        if not scrappedCTECs:
            # try once more if it fails
            sleep(5)
            url = "https://caesar.ent.northwestern.edu/"
            driver.get(url)
            wait(driver, 'PTNUI_LAND_WRK_GROUPBOX14$PIMG', 15)
            fetchSubjectCTECs(driver, subject)
        else:
            saveDictionariesToCSV(scrappedCTECs, subject + "-CTECs")

    driver.quit()
