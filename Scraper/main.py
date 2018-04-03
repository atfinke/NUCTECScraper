import urllib2
import argparse

from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains


from authcaesar import authenticate
from scrapbluectec import scrapLoadedCTECPage
from dicttocsv import saveDictionariesToCSV

spacer = "   "


def wait(driver, elementID, delay):
    try:
        myElem = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.ID, elementID)))
        return myElem
    except TimeoutException:
        print "Loading took too much time!"


def fetchSubjectCTECs(driver, subject):
    print("=============")

    try:
        sleep(1)
        print("Main Page -> Click Manage Classes")
        mainPageManageClassesButton = wait(
            driver, 'win0divPTNUI_LAND_REC_GROUPLET$6', 15)
        mainPageManageClassesButton.click()

        print("Manage Classes Page -> Click Search CTECs")
        classesPageCTECRow = wait(
            driver, 'PTGP_STEP_DVW_PTGP_STEP_LABEL$7', 15)
        sleep(5)
        classesPageCTECRow.click()

        print(spacer + "Waiting for careers to load")
        delay = 15
        try:
            careerSelectorDropdown = WebDriverWait(driver, delay).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#NW_CT_PB_SRCH_ACAD_CAREER')))
        except TimeoutException:
            print "Loading took too much time!"

        driver.execute_script(
            "document.querySelector('#NW_CT_PB_SRCH_ACAD_CAREER').value = 'UGRD'")
        driver.execute_script(
            "document.querySelector('#NW_CT_PB_SRCH_ACAD_CAREER').onchange();")

        print(spacer + "Waiting for subjects to load")
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
            print(spacer + "Found correct class subject")
            driver.execute_script(
                "document.querySelector('#NW_CT_PB_SRCH_SUBJECT').value = '" + subject + "'")
            driver.execute_script(
                "document.querySelector('#NW_CT_PB_SRCH_SUBJECT').onchange();")
        else:
            raise ValueError("Couldn't find subject")
    except Exception as e:
        print(subject + ": Something unexpected happened when loading manage classes page, skipping subject")
        print(subject + ": ERROR INFO - " + str(e) + "\n")
        return False

    sleep(1)
    print(spacer + "Waiting for single class results to load")
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
                print(subject + ": No CTEC results, skipping subject")
                return
    except Exception as e:
        print(subject + ": Something unexpected happened when loading inital CTEC results, skipping subject")
        print(subject + ": ERROR INFO - " + str(e) + "\n")
        return False

    print("Manage Classes Page / CTEC Section -> Click CTEC Result")
    driver.find_element_by_id(
        classesPageCTECResultRow[0].get_attribute('id')).click()
    wait(driver, 'NW_CT_PV4_DRV$0_row_0', 30)

    # Now viewing full ctec view (classes on left, section reviews table on right)
    fullCTECPageClassList = []
    while len(fullCTECPageClassList) == 0:
        links = driver.find_elements_by_class_name("psc_rowact")
        for link in links:
            if "NW_CT_PV_DRV$0_row_" in link.get_attribute('id'):
                fullCTECPageClassList.append(link)
        sleep(0.25)

    print("-------------")
    print(subject + ": Found " +
          str(len(fullCTECPageClassList)) + " classes in sidebar")

    main_window = driver.current_window_handle
    scrappedCTECs = []

    scrappedClasses = 0
    lastClassCTECResultsRowsText = "N/A"

    for classRow in fullCTECPageClassList:

        scrappedClasses += 1
        sleep(5)

        try:
            # Click on the class on the left sidebar
            driver.execute_script(
                "document.getElementById('" + classRow.get_attribute('id') + "').click();")
            classNumber = classRow.get_attribute('innerText').split('-')[0]
        except Exception as e:
            print(spacer + subject + " " + str(classNumber) +
                  ": Something unexpected happened when loading all class CTEC results, skipping class")
            print(spacer + subject + " " + str(classNumber) +
                  ": ERROR INFO - " + str(e) + "\n")
            continue

        print(spacer + subject + " " + str(classNumber) + ": Starting")

        try:
            updatedResults = False
            updatedCheckCount = 0

            print(spacer + spacer + "Waiting 2 seconds to load")
            sleep(2)

            while (updatedResults == False and updatedCheckCount < 30):
                updatedCheckCount += 1

                classCTECResultRow = []
                classCTECResultsRowsText = ""
                links = driver.find_elements_by_class_name("psc_rowact")

                for link in links:
                    if "NW_CT_PV4_DRV$0_row_" in link.get_attribute('id'):
                        classCTECResultRow.append(link)
                        classCTECResultsRowsText += link.get_attribute(
                            'innerText')

                if classCTECResultsRowsText != lastClassCTECResultsRowsText and classCTECResultsRowsText != "":
                    lastClassCTECResultsRowsText = classCTECResultsRowsText
                    updatedResults = True

                else:
                    sleep(1)

            if updatedResults == False or updatedCheckCount == 30:
                print(spacer + spacer +
                      "No CTEC result rows loaded, skipping class" + "\n")
                continue

        except Exception as e:
            print(spacer + spacer +
                  "Something unexpected happened when reading CTEC result rows, skipping class")
            print(spacer + spacer + "ERROR INFO - " + str(e) + "\n")
            continue

        scrappedRows = 0
        onlyOldResultsLeft = False
        sleep(1)

        for resultRow in classCTECResultRow:
            if onlyOldResultsLeft:
                break

            try:
                scrappedRows += 1

                name = driver.find_element_by_id(
                    "MYDESCR$" + str(scrappedRows - 1)).get_attribute("innerText")

                driver.execute_script(
                    "document.getElementById('" + resultRow.get_attribute('id') + "').click();")
                WebDriverWait(driver, 10).until(
                    lambda d: len(d.window_handles) == 2)
            except Exception as e:
                print(
                    spacer + spacer + "Something unexpected happened when clicking a CTEC result row, skipping row")
                print(spacer + spacer + "ERROR INFO - " + str(e) + "\n")
                sleep(2)
                continue

            onCTECTab = False
            validBluePage = False

            while onCTECTab == False:
                for handle in driver.window_handles:
                    driver.switch_to.window(handle)
                    sleep(0.1)
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
                    print "Loading took too much time!"
                    continue

                scrap = scrapLoadedCTECPage(driver)
                if len(scrap) > 0:
                    scrap["shortName"] = name.replace(",", "|")
                    scrappedCTECs.append(scrap)
                else:
                    print(spacer + spacer + spacer + "CTEC page empty")

                print(spacer + spacer + "Class Progress: " +
                      str(scrappedRows) + "/" + str(len(classCTECResultRow)))
            elif onlyOldResultsLeft:
                print(spacer + spacer + "Only old CTECs left, skipping the rest")
            else:
                print(spacer + spacer +
                      "Invalid CTEC Page (Probably the bluera homepage)")
                print(spacer + spacer + "Class Progress: " +
                      str(scrappedRows) + "/" + str(len(classCTECResultRow)))

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        print(spacer + "Subject Progress: " + str(scrappedClasses) +
              "/" + str(len(fullCTECPageClassList)) + "\n")

    saveDictionariesToCSV(scrappedCTECs, subject + "-CTECs")
    return True


if __name__ == "__main__":

    # Arg Parse
    parser = argparse.ArgumentParser()
    parser._action_groups.pop()

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    # required.add_argument("-m", "--Mode", type=str, help='Script Mode. "Class" = Class Fetch, "Subject" = Subject Fetch.');
    required.add_argument("-s", '--Subjects', type=str,
                          help='Subjects in Caesar. Case-sensitive, comma seperated (i.e. "MATH,CHEM")')

    required.add_argument("-n", "--NetID", type=str)
    required.add_argument("-p", "--Password", type=str)

    # optional.add_argument("-t", "--Term", type=str, help='Class term. Only valid for class fetch mode. Case-sensitive (i.e. Fall 2017)');
    # optional.add_argument("-i", "--ClassID", type=str, help='Class ID term. Only valid for class fetch mode (i.e. 230)');

    args = parser.parse_args()

    if args.NetID is None:
        raise ValueError("NetID requried.")
    elif args.Password is None:
        raise ValueError("Password requried.")
    # if args.Mode is None:
    #     raise ValueError("Script mode requried.")
    # elif args.Mode != "Class" and args.Mode != "Subject":
    #     raise ValueError("Invalid mode.")
    # elif args.NetID is None:
    #     raise ValueError("NetID requried.")
    # elif args.Password is None:
    #     raise ValueError("Password requried.")
    # elif args.Mode == "Class":
    #     if args.Term is None:
    #         raise ValueError("Term requried.")
    #     elif args.ClassID is None:
    #         raise ValueError("Class ID requried.")

    # if args.Mode == "C":
    #     print("Class fetch is currently broken (Built for old Caesar)")
    #     # fetchClassData(driver, args.Term, args.Subject, args.ClassID)
    # else:

    # AAL,AFST,AF_AM_ST,ALT_CERT,AMER_ST,AMES,ANIM_ART,ANTHRO,ARABIC,ART,ART_HIST,ASIAN_AM,ASIAN_LC,ASIAN_ST,ASTRON,BIOL_SCI,BMD_ENG,BUS_INST,CAT,CFS,CHEM,CHEM_ENG,CHINESE,CHRCH_MU,CIV_ENG,CIV_ENV,CLASSICS,CMN,COG_SCI,COMM_SCI,COMM_ST,COMP_LIT,COMP_SCI,CONDUCT,COOP,CRDV,CSD,DANCE,DSGN,EARTH,ECE,ECON,EDIT,EECS,ENGLISH,ENTREP,ENVR_POL,ENVR_SCI,ES_APPM,EUR_ST,EUR_TH,FRENCH,GBL_HLTH,GEN_CMN,GEN_ENG,GEN_LA,GEN_MUS,GEN_SPCH,GEOG,GEOL_SCI,GERMAN,GNDR_ST,GREEK,HDPS,HEBREW,HINDI,HIND_URD,HISTORY,HUM,IDEA,IEMS,IMC,INTG_ART,INTG_SCI,INTL_ST,ISEN,ITALIAN,JAPANESE,JAZZ_ST,JOUR,JWSH_ST,KELLG_FE,KELLG_MA,KOREAN,LATIN,LATINO,LATIN_AM,LDRSHP,LEGAL_ST,LING,LOC,LRN_DIS,MATH,MAT_SCI,MECH_ENG,MENA,MFG_ENG,MMSS,MUSIC,MUSICOL,MUSIC_ED,MUS_COMP,MUS_TECH,MUS_THRY,NEUROSCI,PERF_ST,PERSIAN,PHIL,PHYSICS,PIANO,POLI_SCI,PORT,PRDV,PSYCH,RELIGION,RTVF,SESP,SHC,SLAVIC,SOCIOL,SOC_POL,SPANISH,SPCH,STAT,STRINGS,SWAHILI,TEACH_ED,THEATRE,TRANS,TURKISH,URBAN_ST,VOICE,WIND_PER,WM_ST,WRITING,YIDDISH

    subjects = []
    if args.Subjects is not None:
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

        if not fetchSubjectCTECs(driver, subject):
            # try once more if it fails
            sleep(5)
            url = "https://caesar.ent.northwestern.edu/"
            driver.get(url)
            wait(driver, 'PTNUI_LAND_WRK_GROUPBOX14$PIMG', 15)
            fetchSubjectCTECs(driver, subject)

    driver.quit()
