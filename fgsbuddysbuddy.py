import os
import time
import PySimpleGUI as sg
import json
import webbrowser
from io import StringIO
import lxml.etree as et
from lxml import etree
import xmlschema
import pandas as pd
import shutil
#import fnmatch
#import glob,fnmatch
#import glob

#cwd = os.getcwd()

# Funktion för att rensa alla input-fält
def clearinput():
    saveinput = ['folderinput', 'outputfolderinput']
    # Går igenom key_dict och kontrollerar vad det är för sg objekt
    for k, v in window.key_dict.items():
        # Om fältet är ett inputfält och keyn inte finns med i listan över värden som inte ska ändras --> Rensa 
        if isinstance(v, sg.Input) and k not in saveinput:
            v.update('')
        # Sätter alla combofält till defaultvärdet
        elif isinstance(v, sg.Combo):
            v.update(v.DefaultValue)
        # Ändrar till defaultvärdet i radioknapparna kring om paketet ska innehålla "undermappar"
        elif isinstance(v, sg.Radio) and k == 'subfoldersfalse':
            v.update(True)
        else:
            continue
    window.refresh()

# Funktion för att skapa popup-fönstret "Om FGS-Buddysbuddysbuddy"
def buddywindow():
    # Hämtar alla releasenotes från txt-fil och lägger i variabeln releasenotes
    with open('releasenotes.txt', encoding='utf-8') as releasenotesdoc:
        releasenotes = releasenotesdoc.read()

    # Layout för fönstret
    aboutlayout = [
        [sg.Text('FGS-Buddysbuddy', font='Arial 12 bold', size=30)],
        [sg.Text(f'Version: {version}\nSkapad av: Martin Olsson\nLicens: Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)', font='Consolas 10')],
        [sg.Text('Baserad på: Viktor Lundbergs FGS-Buddy v. 1.1.0', font='Consolas 10')],
        [sg.Text('FGS-Buddy på github', font='Consolas 10 underline', text_color='blue', enable_events=True, key='githublink')],
        [sg.Text('', font='Arial 12 bold', size=30)],
        [sg.Text('Release notes', font='Arial 10 bold', size=30)],
        [sg.Text(releasenotes, font='Consolas 8')],
        [sg.Button('Ok', key='Exit', size=7)]
    ]

    # Skapar nya fönstret
    about = sg.Window('Om FGS-Buddy', aboutlayout, icon="Buddy.ico")
    
    # Programloop för "Om FGS-Buddy"-fönstret.
    while True:
        event, values = about.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            about.close()
            releasenotesdoc.close()
            break
        if event == 'githublink':
            webbrowser.open('https://github.com/Viktor-Lundberg/FGSBuddy')

# Funktion för att validera med xsd-schema
def validate(xml_path: str, xsd_path: str) -> bool:
    xmlschema_doc = etree.parse(xsd_path)
    xmlschema = etree.XMLSchema(xmlschema_doc)

    xml_doc = etree.parse(xml_path)
    result = xmlschema.validate(xml_doc)
    #xmlschema.assertValid(xml_doc)
    #try:
        #xmlschema.assertValid(xml_doc)
    #except Exception as e:
        #return False,str(e)
    #return True,''
    return result

# Nuvarande version
version = '0.0.1'
# Current working directory
cwd = os.getcwd()

# Sätter färgtema
sg.theme('greenMono') #LightGreen2 DarkBlue3 #reddit greenMono



innehall = [  
    [sg.Text('Skapa och validera metadatafil (xml) från xml eller semikolonseparerad csv med rubriker', font='Arial 12 bold', size=70)],
    [sg.Text('Med denna metadataomat, ett komplement till FGS Buddy (länk i Hjälp-menyn) kan du skapa en metadatafil som valideras mot ett xsd-schema.')],
    [sg.Text('Utgå antingen från en semikolonseparerad csv-fil med rubriker eller en xml-fil.')],
    [sg.Text('Mappningen från input till metadatafil sker i den xslt-fil som ingår och som du kan kopiera och modiera efter behov.')],
    [sg.Text('')],
    [sg.Text('Sökväg till inputfil:*')],
    [sg.Input(tooltip="Välj inputfil", key='inputfile'), sg.FileBrowse('Välj fil', key="inputfileB", initial_folder=os.path.join(cwd) ), sg.Text ('Csv- eller xml-fil med metadatat du vill transformera.')],
    [sg.Text('Sökväg till xsltfil:*')],
    [sg.Input(tooltip="Välj xslt", key='xsltfile'), sg.FileBrowse('Välj fil', key="xsltfileB", initial_folder=os.path.join(cwd) ), sg.Text ('För att transformera din input.')],
    [sg.Text('Sökväg till schemafil:')],
    [sg.Input(tooltip="Välj schemafil", key='schemafile'), sg.FileBrowse('Välj fil', key="schemafileB", initial_folder=os.path.join(cwd) ), sg.Text ('Använd om du vill validera den skapade metadatafilen.')],
    [sg.Text('Döp din outputfil:*', tooltip='Välj filnamn på outputfilen')],
    [sg.Input(key='filename',size=45, tooltip='Välj filnamn på outputfilen', default_text='metadata'), sg.Combo(['.xml'], default_value='.xml', key='filesuffix'), sg.Text ('Använd default eller välj ett eget namn. Filsuffix läggs till per automagi.\nFilnamnet får inte finnas redan i outputkatalogen.')],

    ]

space = [
    [sg.Text('', font='Arial 8 bold', size=30)],
    ]
    
# Menyraden
meny = [
    ['FGS-dokumentation', ['FGS-Paketstruktur v 1.2','FGS-Paketstruktur v 1.2 - tillägg','Schema v 1.2']],['Hjälp', ['Om FGS-Buddysbuddy']]
     ]
    
# GUI layout
layout = [
    # OBS! Pysimplegui har problem med custom menubar (om det används syns inte applikationen i verktygsfältet, använd classic tills fix...)
    #[sg.Titlebar('FGS-Buddysbuddy v 0.0.1 - Martin Olsson', font='Consolas 10', background_color='Black')],
    #[sg.MenubarCustom(meny, bar_background_color='Pink', bar_text_color='Black')],
    
    [sg.MenuBar(meny, background_color='Pink')],
    [sg.Column(space)],
    [sg.Column(innehall, vertical_alignment='top')],
    [sg.Text('')],
    [sg.Output(size=(165,5), key='output', pad=5, background_color=	'pink', echo_stdout_stderr=True)],
    [sg.Text('Outputkatalog'),sg.Input(default_text=cwd, tooltip="Välj katalog", size=65, key='outputfolderinput'), sg.FolderBrowse('Välj katalog',key='outputfolder', initial_folder=os.path.join(cwd)),sg.Submit('Skapa fil', key='create_metadatafile', size=15,button_color='black on pink'), sg.Button('Rensa', key='clear', size=15)],
    
    ]

# Skapar "huvudfönstret"
window = sg.Window(f'FGS-Buddysbuddy v {version}',layout, font='Consolas 10', icon="Buddy.ico", resizable=True, titlebar_background_color='green')

# Variabler för att kontrollera obligatoriska värden samt trigger för att visa/dölja alla element i layouten.
forcedvaluesdict = {}
allvalues = False


# Program-Loop
while True:
    event, values = window.read()
    match event:
        case sg.WIN_CLOSED:
            break

        # Startar processen för att skapa FGS-paket om användaren trycker på "skapa paket"-knappen
        case 'create_metadatafile':
            window.find_element('output').Update('')
            window.refresh()
            inputfile = values['inputfileB']
            xsltfile = values['xsltfileB']
            schemafile = values['schemafileB']
            outputfolder = values['outputfolder']
            filename = values['filename']
            filesuffix = values['filesuffix']
            xmlfile = filename+filesuffix

            # Kontrollerar att inputfil och xsltfil finns och om schemafil är tom skapa metadatafil utan att validera.    
            if values['inputfile'] == '':
                print(f'Du måste välja en inputfil!')
            elif values['xsltfile'] == '':
                print(f'Du måste välja en xsltfil!')
             
            # Hantering av xmlfil som input.
            elif values['inputfile'].endswith('.xml') and values['schemafile'] == '':
                doc = et.parse(inputfile)
                xsl = et.parse(xsltfile)
                transform = et.XSLT(xsl)
                result = transform(doc)
                result.write_output(xmlfile)
                
                try:
                    shutil.move(xmlfile, outputfolder)
                    print(f'Metadatafil skapad i outputkatalog. Bra jobbat!')
                except: print(f'Men finns redan en fil i outputfolder med samma namn. Radera/flytta den innan du skapar en ny.')
            
            elif values['inputfile'].endswith('.xml') and values['schemafile'] != '':
                doc = et.parse(inputfile)
                xsl = et.parse(xsltfile)
                transform = et.XSLT(xsl)
                result = transform(doc)
                result.write_output(xmlfile)
                if validate(xmlfile, schemafile):
                    print(f'Valid!')
                    try:
                        shutil.move(xmlfile, outputfolder)
                        print(f'Metadatafil skapad i outputkatalog, och validerad mot {schemafile}. Bra jobbat!')
                    except: print(f'Men finns redan en fil i outputfolder med samma namn. Radera/flytta den innan du skapar en ny.')
                else:
                    print(f'Not/ej valid!')
                    try:
                        shutil.move(xmlfile, outputfolder)
                        print(f'Metadatafil skapad i outputkatalog men den validerar inte mot {schemafile}.')
                    except: print(f'Men finns redan en fil i outputfolder med samma namn. Radera/flytta den innan du skapar en ny.')
                    
            elif values['schemafile'] == '' and values['inputfile'] != '' and values['xsltfile'] != '':
                print(f'Det går bra att inte välja en schemafil men då blir det ingen validering!')
                print(f'Skapar metadatafil...')
                window.refresh()
                time.sleep(0.3)
                window.find_element('output').update('')
                window.refresh()
                #print(fgsPackage.output)
                df=pd.read_csv(inputfile, sep = ';')
                df = df.convert_dtypes()
                df.to_xml(xmlfile)
                doc = et.parse(xmlfile)
                xsl = et.parse(xsltfile)
                transform = et.XSLT(xsl)
                result = transform(doc)
                result.write_output(xmlfile)
                #print("The Current working directory is :", cwd)
                #print(event, values[xsltfile], values[xsltfileB], values[outputfolder]) 
                #outputfolder = r'C:\Users\marols\pythonskript\FGSBuddysbuddy\out'
                
                try:
                    shutil.move(xmlfile, outputfolder)
                    print(f'Metadatafil skapad i outputkatalog. Bra jobbat!')
                except: print(f'Men finns redan en fil i outputfolder med samma namn. Radera/flytta den innan du skapar en ny.')

            #if values['submissionagreement'] == '' or values['system'] == '' or values['arkivbildare'] == '' or values['IDkod'] == '' or values['levererandeorganisation'] == '':
                # Lägger till värden i dicten för att kunna visa användaren vilka värden som saknas
                #forcedvaluesdict['System'] = values['system']
                #forcedvaluesdict['Leveransöverenskommelse'] = values['submissionagreement']
                #forcedvaluesdict['Arkivbildare'] = values['arkivbildare']
                #forcedvaluesdict['Identitetskod'] = values['IDkod']
                #forcedvaluesdict['Levererande organisation'] = values['levererandeorganisation']
                # Loopar igenom dicten
                #for k, v in forcedvaluesdict.items():
                    # Returnerar de värden som saknas till användaren.
                    #if v == '':
                        #print(f'Fältet "{k}" saknar värde.')
                
            # Om inputfil, xsltfil och schemafil är valda skapas och valideras metadatafil.
            else:
                print(f'Skapar metadatafil...')
                window.refresh()
                #fgsPackage = FGSfunc.FgsMaker(values)
                #if values['folder'] == '':
                    #folder = os.path.join(cwd)
                #else:
                    #folder = os.path.join(values['folder'])
                #if values['outputfolder'] == '':
                    #outputfolder = os.path.join(cwd)
                #else:
                    #outputfolder = os.path.join(values['outputfolder'])
                #if values['subfolderstrue']:
                    #subfolders = True
                if values['inputfile'] != '':
                    inputfile = values['inputfile']
                if values['xsltfile'] != '':
                    xsltfile = values['xsltfile']
                if values['schemafile'] != '':
                    schemafile = values['schemafile']
                time.sleep(0.3)
                window.find_element('output').update('')
                window.refresh()
                df=pd.read_csv(inputfile, sep = ';')
                df = df.convert_dtypes()
                df.to_xml(xmlfile)
                doc = et.parse(xmlfile)
                xsl = et.parse(xsltfile)
                transform = et.XSLT(xsl)
                result = transform(doc)
                result.write_output(xmlfile)
                #lösningen tillåter inte att man skriver över fil
                if validate(xmlfile, schemafile):
                    print(f'Valid!')
                    try:
                        shutil.move(xmlfile, outputfolder)
                        print(f'Metadatafil skapad i outputkatalog, och validerad mot {schemafile}. Bra jobbat!')
                    except: print(f'Men finns redan en fil i outputfolder med samma namn. Radera/flytta den innan du skapar en ny.')
                else:
                    print(f'Not/ej valid!')
                    try:
                        shutil.move(xmlfile, outputfolder)
                        print(f'Metadatafil skapad i outputkatalog men den validerar inte mot {schemafile}.')
                    except: print(f'Men finns redan en fil i outputfolder med samma namn. Radera/flytta den innan du skapar en ny.')
                    
        
        case 'clear':
            clearinput()
        
        # Meny - FGS-dokumentation
        case 'FGS-Paketstruktur v 1.2':
            webbrowser.open('https://riksarkivet.se/Media/pdf-filer/doi-t/FGS_Paketstruktur_RAFGS1V1_2.pdf')
        case 'FGS-Paketstruktur v 1.2 - tillägg':
            webbrowser.open('https://riksarkivet.se/Media/pdf-filer/doi-t/FGS_Paketstruktur_Tillagg_RAFGS1V1_2A20171025.pdf')
        case 'Schema v 1.2':
            webbrowser.open('http://xml.ra.se/e-arkiv/METS/CSPackageMETS.xsd')
        
        # Meny - Hjälp
        case 'Om FGS-Buddysbuddy':
            sg.Window.disappear(window)
            buddywindow()
            sg.Window.reappear(window)