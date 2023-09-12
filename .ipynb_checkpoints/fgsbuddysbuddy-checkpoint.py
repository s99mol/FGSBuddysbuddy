import os
import time
import PySimpleGUI as sg
import json
import webbrowser
from io import StringIO
import lxml.etree as et
from lxml import etree
import pandas as pd
import shutil
#import os.path
from pathlib import Path

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
        [sg.Text('FGS-Buddysbuddy på github', font='Consolas 10 underline', text_color='blue', enable_events=True, key='githublink')],
        [sg.Text('FGS-Buddy på github', font='Consolas 10 underline', text_color='blue', enable_events=True, key='githublink2')],
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
        elif event == 'githublink':
            webbrowser.open('https://github.com/s99mol/FGSBuddysbuddy')
        elif event == 'githublink2':
            webbrowser.open('https://github.com/Viktor-Lundberg/FGSBuddy')

# Nuvarande version
version = '0.0.1'

# Current working directory
cwd = os.getcwd()

# hemfoldern
home = Path.home()

# Sätter färgtema
sg.theme('greenMono') #LightGreen2 DarkBlue3 #reddit greenMono


innehall = [  
    [sg.Text('Skapa och validera metadatafil (xml) från xml eller semikolonseparerad csv med rubriker', font='Arial 12 bold', size=70)],
    [sg.Text('Med denna metadataomat, ett komplement till FGS Buddy (länk i Hjälp-menyn) kan du skapa en metadatafil som valideras mot ett xsd-schema.')],
    [sg.Text('Utgå antingen från en semikolonseparerad csv-fil med rubriker eller en xml-fil.')],
    [sg.Text('Mappningen från input till metadatafil sker i den xslt-fil som ingår och som du kan kopiera och modiera efter behov.')],
    [sg.Text('')],
    [sg.Text('Sökväg till inputfil:*')],
    [sg.Input(tooltip="Välj inputfil", key='inputfile'), sg.FileBrowse('Välj fil', key="inputfileB", initial_folder=os.path.join(cwd) ), sg.Combo([';', ',', ':', '.', '|', 'tab', 'space'], default_value=';', key='csvseparator'), sg.Text ('Csv- eller xml-fil med metadatat du vill transformera.\nVälj filens separator om annan än semikolon (;)')],
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
    [sg.Text('Outputkatalog'),sg.Input(default_text=home, tooltip="Välj katalog", size=65, key='outputfolder'), sg.FolderBrowse('Välj katalog', key='initialoutputfolder', initial_folder=Path.home()), sg.Submit('Skapa fil', key='create_metadatafile', size=15,button_color='black on pink'), sg.Button('Rensa', key='clear', size=15)],
    
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

        # Startar processen för att skapa metadatafil om användaren trycker på "Skapa fil"-knappen
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
             
            # Hantering av xmlfil som input, utan xmlschema
            elif values['inputfile'].endswith('.xml') and values['schemafile'] == '':
                doc = et.parse(inputfile)
                xsl = et.parse(xsltfile)
                transform = et.XSLT(xsl)
                result = transform(doc)
                result.write_output(xmlfile)

                #testet visar att det inte finns ngn fil där, fast shutil är ändå inte nöjd, ger exception
                #path = r''
                #check_file = os.path.isfile(path)
                #print(check_file)
                #print(cwd)
                
                try:
                    shutil.move(xmlfile, outputfolder)
                    print(f'Metadatafil skapad i outputkatalog. Bra jobbat!')
                #except Exception as e:
                    sg.popup_error_with_traceback(f'Error! Info:', e)
                except: print(f'Det finns redan en fil i outputfolder med samma namn. Radera/flytta den innan du skapar en ny. Om outputkatalog är samma som programmets katalog beror detta meddelande på att det inte går att flytta en fil till en plats den redan befinner sig på.')
                #except:
                    #felbeteende: när jag kör med default homepath får jag medd "no such file or directory" och filen flyttas inte. När jag aktivt anger home funkar det. Fråga: Hur anger man korrekt home?
                    #misslyckat försök att hantera problemet att det blir except-meddelande när outputfolder = cwd
                    #current_directory = os.getcwd()
                    #final_directory = os.path.join(current_directory, r'new_folder')
                    #if not os.path.exists(final_directory):
                        #os.makedirs(final_directory)
                    #shutil.move(xmlfile, final_directory)
                    #shutil.move(xmlfile, os.path.join(cwd))

            # Hantering av xmlfil som input, med xmlschema
            elif values['inputfile'].endswith('.xml') and values['schemafile'] != '':
                doc = et.parse(inputfile)
                xsl = et.parse(xsltfile)
                transform = et.XSLT(xsl)
                result = transform(doc)
                result.write_output(xmlfile)

                #lösningen tillåter inte att man skriver över fil
                try:
                    xmlschemadoc=etree.parse(schemafile)
                    xmlschema=etree.XMLSchema(xmlschemadoc)
                    xmldoc=etree.parse(xmlfile)
                    xmlschema.assertValid(xmldoc)
                    print(f'Valid mot {schemafile}. Bra jobbat!')
                except Exception as e: print(e)
                
                try:
                    shutil.move(xmlfile, outputfolder)
                    print(f'Metadatafil skapad i outputkatalog oavsett valid eller inte. Om filen inte är valid visas ett felmeddelande ovan.')
                except: print(f'Det finns redan en fil i outputfolder med samma namn. Radera/flytta den innan du skapar en ny. Om outputkatalog är samma som programmets katalog beror detta meddelande på att det inte går att flytta en fil till en plats den redan befinner sig på.')

            # Hantering av csv som input, utan xmlschema
            elif values['schemafile'] == '' and values['inputfile'] != '' and values['xsltfile'] != '':
                print(f'Det går bra att inte välja en schemafil men då blir det ingen validering!')
                print(f'Skapar metadatafil...')
                window.refresh()
                time.sleep(0.3)
                window.find_element('output').update('')
                window.refresh()
                try:
                    df=pd.read_csv(inputfile, sep = values['csvseparator'])

                except Exception as e:
                    sg.popup_error_with_traceback(f'Error! Sannolikt har du valt fel csv-separator. Fil kan kanske ändå skapas, men rådet är att välja rätt separator. Info:', e)

                df = df.convert_dtypes()
                try:
                    df.to_xml(xmlfile)
                except Exception as e:
                    sg.popup_error_with_traceback(f'Error! Sannolikt har du valt fel csv-separator. Fil kan kanske ändå skapas, men rådet är att välja rätt separator. Info:', e)
                try:
                    doc = et.parse(xmlfile)
                except Exception as e:
                    sg.popup_error_with_traceback(f'Error! Sannolikt har du valt fel csv-separator. Fil kan kanske ändå skapas, men rådet är att välja rätt separator. Info:', e)
                xsl = et.parse(xsltfile)
                transform = et.XSLT(xsl)
                result = transform(doc)
                result.write_output(xmlfile)
                
                try:
                    shutil.move(xmlfile, outputfolder)
                    print(f'Metadatafil skapad i outputkatalog. Bra jobbat!')
                except: print(f'Det finns redan en fil i outputfolder med samma namn. Radera eller flytta den innan du skapar en ny.')
                
            # Hantering av csv som input, med xmlschema
            else:
                print(f'Skapar metadatafil...')
                window.refresh()
                if values['inputfile'] != '':
                    inputfile = values['inputfile']
                if values['xsltfile'] != '':
                    xsltfile = values['xsltfile']
                if values['schemafile'] != '':
                    schemafile = values['schemafile']
                time.sleep(0.3)
                window.find_element('output').update('')
                window.refresh()

                try:
                    df=pd.read_csv(inputfile, sep = values['csvseparator'])

                except Exception as e:
                    sg.popup_error_with_traceback(f'Error! Sannolikt har du valt fel csv-separator. Fil kan kanske ändå skapas, men rådet är att välja rätt separator. Info:', e)

                df = df.convert_dtypes()
                try:
                    df.to_xml(xmlfile)
                except Exception as e:
                    sg.popup_error_with_traceback(f'Error! Sannolikt har du valt fel csv-separator. Fil kan kanske ändå skapas, men rådet är att välja rätt separator. Info:', e)
                try:
                    doc = et.parse(xmlfile)
                except Exception as e:
                    sg.popup_error_with_traceback(f'Error! Sannolikt har du valt fel csv-separator. Fil kan kanske ändå skapas, men rådet är att välja rätt separator. Info:', e)
                xsl = et.parse(xsltfile)
                transform = et.XSLT(xsl)
                result = transform(doc)
                result.write_output(xmlfile)
                
                #lösningen tillåter inte att man skriver över fil
                try:
                    xmlschemadoc=etree.parse(schemafile)
                    xmlschema=etree.XMLSchema(xmlschemadoc)
                    xmldoc=etree.parse(xmlfile)
                    xmlschema.assertValid(xmldoc)
                    print(f'Valid mot {schemafile}. Bra jobbat!')
                except Exception as e: print(e)
                
                try:
                    shutil.move(xmlfile, outputfolder)
                    print(f'Metadatafil skapad i outputkatalog oavsett valid eller inte. Om filen inte är valid visas ett felmeddelande ovan.')
                except: print(f'Det finns redan en fil i outputfolder med samma namn. Radera/flytta den innan du skapar en ny. Om outputkatalog är samma som programmets katalog beror detta meddelande på att det inte går att flytta en fil till en plats den redan befinner sig på.')
                
        
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