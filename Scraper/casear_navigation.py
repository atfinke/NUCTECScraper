import logging

from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

spacer = "   "

def wait(driver, elementID, delay):
    try:
        myElem = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.ID, elementID)))
        return myElem
    except TimeoutException:
        print("Loading took too much time!")

    raise ValueError("Loading took too much time!")

def open_main_page(driver):
    url = "https://caesar.ent.northwestern.edu/"
    driver.get(url)
    wait(driver, 'PTNUI_LAND_WRK_GROUPBOX14$PIMG', 15)

def open_subject_ctecs_from_main_page(driver, logger, career, subject):
    try:
        logger.info("Main Page -> Click Manage Classes")
        main_page_classes_button = wait(
            driver, 'PTNUI_LAND_REC14$0_row_8', 15)
        main_page_classes_button.click()

        logger.info("Manage Classes Page -> Click Search CTECs")
        classes_page_ctec_bar_tab = wait(
            driver, 'PTGP_STEP_DVW_PTGP_STEP_LABEL$7', 15)
        sleep(5)
        classes_page_ctec_bar_tab.click()

        logger.info(spacer + "Waiting for careers to load")
        delay = 15
        try:
            ctec_page_career_selector_dropdown = WebDriverWait(driver, delay).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#NW_CT_PB_SRCH_ACAD_CAREER')))
        except TimeoutException:
            logger.error("Loading took too much time!")

        # TGS or UGRD

        driver.execute_script(
            "document.querySelector('#NW_CT_PB_SRCH_ACAD_CAREER').value = '" + career + "'")
        driver.execute_script(
            "document.querySelector('#NW_CT_PB_SRCH_ACAD_CAREER').onchange();")

        logger.info(spacer + "Waiting for subjects to load")
        sleep(0.25)
        while driver.execute_script("return document.getElementById('processing').offsetParent == null") == False:
            sleep(0.5)

        ctec_page_subject_selector_dropdown = driver.find_element_by_css_selector(
            "#NW_CT_PB_SRCH_SUBJECT")
        options = driver.find_elements_by_tag_name("option")
        is_valid_class = False

        for option in options:
            if (option.get_attribute('value') == subject):
                is_valid_class = True

        if (is_valid_class):
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
        return False

    sleep(1)
    logger.info(spacer + "Waiting for single class results to load")
    driver.execute_script(
        "document.getElementById('NW_CT_PB_SRCH_SRCH_BTN').click();")

    # One off to get past main screen
    try:
        classes_page_ctec_result_row = []
        attempts = 0
        while len(classes_page_ctec_result_row) == 0:
            attempts = attempts + 1
            links = driver.find_elements_by_class_name("psc_rowact")
            for link in links:
                if "NW_CT_PV_DRV$0_row_" in link.get_attribute('id'):
                    classes_page_ctec_result_row.append(link)
                    break
            sleep(0.25)
            if attempts > 60:
                logger.warning(subject + ": No CTEC results, skipping subject")
                return False
    except Exception as e:
        logger.error(
            subject + ": Something unexpected happened when loading inital CTEC results, skipping subject")
        logger.error(subject + ": ERROR INFO - " + str(e) + "\n")
        return False

    logger.info("Manage Classes Page / CTEC Section -> Click CTEC Result")
    driver.find_element_by_id(
        classes_page_ctec_result_row[0].get_attribute('id')).click()
    wait(driver, 'NW_CT_PV4_DRV$0_row_0', 30)
    return True
