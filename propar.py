# -*- coding: utf-8 -*-
#!/usr/bin/env python

import time

import sys
import os
import re
import urllib.request  as urllib2
import glob

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import xlwt
import xlsxwriter
from openpyxl import Workbook

from bs4 import BeautifulSoup

import argparse

#najmanji broj 2556, najveci 1501005


def get_text(soup, key):
    record = soup.find(attrs={"name": key})
    return record.next_element.getText()

def get_amount(soup, text_pattern):
    text_search = re.compile(text_pattern)
    foundtext = soup.find('span', text = text_search)
    text = foundtext.findNext('span').string
    regex = r"(?<=vrijednost:)(.*\d*)(\s+\D*)"
    return re.search(regex, text).group(1).strip()

def get_text_old(soup, text_pattern):
    text_search = re.compile(text_pattern)
    foundtext = soup.find('span', text = text_search)
    # print (foundtext)
    return foundtext.next_sibling

def find_checked_in_table_old_front(soup, text_pattern, attribute):
    text_search = re.compile(text_pattern)
    foundtext = soup.find(attribute, text = text_search)
    if foundtext is None:
        return None
    table = foundtext.findNext('table', border = "0")
    checked = table.find('img', src=re.compile('\Wchecked.gif$'))
    return checked.findNext('td').string


def find_checked_in_table_old_back(soup, text_pattern, border):
    text_search = re.compile(text_pattern)
    foundtext = soup.find('span', text = text_search)

    table = foundtext.findNext('table', border = border)
    checked = table.find('img', src=re.compile('\Wchecked.gif$'))
    return checked.findPrevious('span').string


def get_by_attribute(soup, text_pattern):
    text_search = re.compile(text_pattern)
    foundtext = soup.find('td', text = text_search).string.strip()
    #print (foundtext.encode('utf-8'))
    regex = r"(?<={0})(\W+)(\w+.*$)".format(text_pattern)
    record = re.search(regex, foundtext)
    return record.group(2)

def get_by_attribute_client(soup, text_pattern):
    location = soup.find('span', text = re.compile(".* Ime i adresa"))
    text_search = re.compile(text_pattern)
    foundtext = location.findNext('td', text = text_search).string.strip()
    #print (foundtext.encode('utf-8'))
    regex = r"(?<={0})(\W+)(\w+.*$)".format(text_pattern)
    record = re.search(regex, foundtext)
    return record.group(2)



def write_row(sheet, row, line):
    for column, record in enumerate(line):
        sheet.write(row, column, record)

def find_checked_in_table(soup, text_pattern, function):
    text_search = re.compile(text_pattern)
    foundtext = soup.find('span', text = text_search)
    table = foundtext.findNext('table')
    checkbox = table.find('input', checked = True)
    return function(checkbox['name'])


def activity(x):
    return {
        'Djel_OJN1'         : u'Opće javne usluge',
        'Djel_SGKS1'        : u'Stambeno i komunalno gospodarstvo i usluge',
        'Djel_Obrana1'      : u'Obrana',
        'Djel_SS1'          : u'Socijalna skrb',
        'Djel_SJRS1'        : u'Javni red i sigurnost',
        'Djel_SVKR1'        : u'Rekreacija, kultura i religija',
        'Djel_ZO1'          : u'Okoliš',
        'Djel_Obrazovanje1' : u'Obrazovanje',
        'Djel_GIF1'         : u'Gospodarstvo i financije',
        'Djel_OSTJ1'        : u'Ostalo',
        'Djel_Zdravstvo1'   : u'Zdravstvo',
        #'DjelOstaloJNaziv1' : u'',
    }[x]


def procedure(x):
    return {
        'Postupak_OTV1'           : u'Otvoreni',
        'Postupak_PSaPO1'         : u'Pregovarači s prethodnom objavom',
        'Postupak_OGR1'           : u'Ograničeni',
        'PregSOZur_DA1'           : u'Pregovarači s prethodnom objavom zbog žurnosti',
        'OgrZur_DA1'              : u'Ograničeni zbog žurnosti',
        'Postupak_PBezPO1'        : u'Pregovarački bez prethodne objave',
        'Postupak_ND1'            : u'Natjecateljski dijalog',
        'Postupak_BezOPNN1'       : u'Sklapanje ugovora bez prethodne objave poziva za nadmenta',
    }[x]

def criterion(x):
    return {
        'NajnizaCijena1'           : u'Najniža cijena',
        'EkNajpPon1'               : u'Ekonomski najpovoljnija ponuda',
    }[x]





def open_document(browser, directory):


    browser.find_element_by_css_selector("i.fa.fa-firefox").click()

    #browser.find_element_by_id("uiDokumentPodaci_uiDocumentCtl_uiForClick")

    """
    try:
        element = WebDriverWait(browser, 10).until(
        #EC.presence_of_element_located((By.ID, "uiDokumentPodaci_uiDocumentCtl_uiForClick")))
        EC.visibility_of_element_located((By.ID, "uiDokumentPodaci_uiDocumentCtl_uiForClick")))
    except:
        browser.quit()
        print ("Opasno")

    """
    #browser.find_element_by_css_selector("i.fa.fa-firefox").click()
    #browser.find_element_by_id("uiDokumentPodaci_uiDocumentCtl_uiForClick").click()

    # time.sleep(2)

    # path = r"C:\Users\msikic\Downloads\Obavijest*.html"
    path = directory + r"Obavijest*.Html"

    while (True):
        try:
            filename = glob.glob(path)[0]
            break
        except IndexError:
            print ("Waiting for the file!")
            time.sleep(2)

    with open(filename, encoding="utf-8") as fp:
        # soup = BeautifulSoup(fp, "html5lib")
        soup = BeautifulSoup(fp, "html.parser")
    return soup


def delete_htmls():
    # path = r"C:\Users\msikic\Downloads\*.html"
    path = r"*.Html"
    for filename in glob.glob(path):
        try:
            os.remove(filename)
        except OSError:
            pass

def parse_document(id, announcement_uri, soup):

    record = []

    client_type = soup.find('input', attrs={"name": "VrstaJN_JLS1"})

    if (client_type is None) or (not contractor.has_attr('checked')):
        delete_htmls()
        return None

    record.append(id)
    record.append(announcement_uri)
    record.append(get_text(soup, "DatOdabUg1"))
    record.append(get_text(soup, "BrZapPon1"))
    record.append(get_text(soup, "NazivNadmetanja1"))
    record.append(get_text(soup, "KorisnikNaziv1"))
    record.append("Jedinica lokalne i područne (regionalne) samouprave")
    record.append(find_checked_in_table(soup, ".* Glavna djelatnost", activity))
    record.append(get_text(soup, "UGgStrNaziv1"))
    record.append(get_text(soup, "UGgStrPAdr1"))
    record.append(get_text(soup, "UGgStrMjesto1"))
    record.append("")
    record.append(get_text(soup, "UgGrupePredProc1"))
    record.append(get_text(soup, "UgVrijednost1"))
    record.append(find_checked_in_table(soup, ".* Vrsta postupka", procedure))
    record.append(find_checked_in_table(soup, ".* Kriteriji za ", criterion))

    return record


def parse_old_document (id, announcement_uri, soup):

    record = []

    client_type = find_checked_in_table_old_front(soup, u".* Vrsta javnog", 'span')

    if client_type is None:
        delete_htmls()
        return None

    pattern = re.search(r"samouprave", client_type)

    if pattern is None:
        delete_htmls()
        return None


    record.append(id)
    record.append(announcement_uri)

    record.append(get_text_old(soup, r".* Datum sklapanja"))
    record.append(get_text_old(soup, r".* Broj zaprimljenih"))
    record.append(get_by_attribute(soup, r"Naziv predmeta nabave:"))
    record.append(get_by_attribute(soup, u"Naziv:"))

    record.append(client_type)
    record.append(find_checked_in_table_old_front(soup, u"Ostalo:", "td"))

    record.append(get_by_attribute_client(soup, u"Naziv:"))
    record.append(get_by_attribute_client(soup, u"Poštanska adresa:"))
    record.append(get_by_attribute_client(soup, u"Mjesto:"))
    record.append(get_by_attribute_client(soup, u"OIB:"))

    record.append(get_amount(soup, u"Prvobitno procijenjena"))
    record.append(get_amount(soup, u".* ukupna vrijednost ugovora:"))
    record.append(find_checked_in_table_old_back(soup, u'.* Vrsta postupka', 2))
    record.append(find_checked_in_table_old_back(soup, u'.* Kriteriji odabira', 0))

    return record


def process_case(ws, ids, announcement_id, directory, OS):
    #browser = webdriver.Firefox()
     #browser = webdriver.Chrome(r'/home/msikic/src/chromedriver/chromedriver')

    #browser = webdriver.Chrome(r'C:\Users\msikic\Downloads\chromedriver_win32\chromedriver.exe')

    # url = r'C:\Users\msikic\Downloads\geckodriver-v0.19.1-win64\geckodriver.exe'
    # browser = webdriver.Firefox(executable_path=url)

    # path = r'C:\Users\msikic\Downloads\chromedriver_win32\chromedriver.exe'
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": directory}
    options.add_experimental_option("prefs", prefs)  # Last I checked this was necessary.
    #path = r'/home/msikic/src/chromedriver/chromedriver'
    if OS == "windows":
        path = r'C:\Users\msikic\Downloads\chromedriver_win32\chromedriver.exe'
    elif OS == "linux":
        path = r'/home/msikic/src/chromedriver/chromedriver'

    browser = webdriver.Chrome(path, chrome_options=options)


    print ("Processing ... {0}".format(announcement_id))
    announcement_uri = 'https://eojn.nn.hr/SPIN/application/ipn/DocumentManagement/DokumentPodaciFrm.aspx?id={}'.format(announcement_id)
    browser.get(announcement_uri)


    try:
        browser.find_element_by_id('uiUsernameTbx')
        print("login page!")
        delete_htmls()
        return (ids, ws)
    except NoSuchElementException:
        pass

    text = browser.find_element_by_class_name("HeaderInner").text

    text_search = (u'sklopljenim|sklopljenom')

    if (re.search(text_search, text)):
        pass
    else:
        try:
            element = browser.find_element_by_xpath("//*[contains(text(), 'sklopljen')]")
        except NoSuchElementException:
            delete_htmls()
            return (ids, ws)

        pattern = re.compile('id=(\d+)')
        announcement_id = pattern.search(element.get_attribute('href')).group(1)
        if announcement_id in ids:
            return (ids, ws)
        else :
            ids.add(announcement_id)
            print ("Processing ... {0}".format(announcement_id))
            element.click()
            browser.close()
            new_window = browser.window_handles[0]
            browser.switch_to_window(new_window)


    id = browser.find_element_by_id('uiDokumentPodaci_uiBrojObjave').text

    announcement_uri = browser.current_url

    soup = open_document(browser, directory)

    img_link = soup.find('img')['src']

    if img_link is None:
        procurement = parse_document(id, announcement_uri, soup)
    else :
        procurement = parse_old_document(id, announcement_uri, soup)

    if procurement is not None:
        ws.append(procurement)
        print ("Entering data!")
    delete_htmls()
    browser.quit()
    return (ids, ws)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", help="working directory")
    parser.add_argument("-s", "--start", type=int, help="start purchase")
    parser.add_argument("-e", "--end", type=int, help="end purchase")
    parser.add_argument("--os",help="computer OS")

    args = parser.parse_args()

    OS = args.os
    print (OS)
    directory = args.directory

    if OS == "linux":
        if not directory.endswith('\\'):
            directory = directory + r"\\"
    elif OS == "windows":
        if not directory.endswith('/'):
            directory = directory + r"/"
    else:
        sys.exit("Wrong os!!")

    os.chdir(directory)
    start = args.start
    end = args.end
    start_time = time.time()

    wb = Workbook()
    ws = wb.active

    #wb = xlsxwriter.Workbook('test.xlsx')
    #ws = wb.add_worksheet('test')

    header = [u'ID', 'URL', u'DATUM SKLAPANJA UGOVORA', u'BROJ ZAPRIMLJENIH PONUDA',
              u'PREDMET NABAVE (naziv)', u'NARUČITELJ', u'VRSTA NARUČITELJA',
              u'GLAVNA DJELATNOST', u'PONUDITELJ', u'ADRESA', u'GRAD', u'OIB', u'PROCJENA VRIJEDNOSTI UGOVORA',
              u'VRIJEDNOST UGOVORA', u'VRSTA POSTUPKA', u'KRITERIJ', ]

    # write_row(ws, 0, header)
    ws.append(header)

    #announcement_id = 1413402
    # min 2556 399221

    ids = set()
    problematic = set()
    for announcement_id in range(start, end):
        if announcement_id not in ids:
            try:
                ids.add(announcement_id)
                (ids, ws) = process_case(ws, ids, announcement_id, directory, OS)
            except AttributeError:
                print ("Problem with: {0}".format(announcement_id) )
                problematic.add(announcement_id)
    #wb.close()
    with open('problematicni.txt', 'w') as f:
        for rec in problematic:
            f.write('{0}\n'.format(rec))

    wb.save('results.xlsx')
    print ("velicina seta: {0}".format(len(ids)))
    end_time = time.time()
    print (end_time - start_time)
    #browser.quit()

if __name__== "__main__":
  main()
