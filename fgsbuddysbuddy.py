import os
import time
import PySimpleGUI as sg
#import json
import webbrowser
from io import StringIO
from lxml import etree
import pandas as pd
import uuid
import shutil
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

# hemfoldern (ska övergå till Pathlib helt)
home = Path.home()

# Sätter färgtema
sg.theme('greenMono') #LightGreen2 DarkBlue3 #reddit greenMono


innehall = [  
    [sg.Text('Skapa och validera metadatafil (xml) från xml eller semikolonseparerad csv med rubriker', font='Arial 12 bold', size=75)],
    [sg.Text('Med denna metadataomat, ett komplement till FGS Buddy (länk i Hjälp-menyn) kan du skapa en metadatafil som valideras mot ett xsd-schema.')],
    [sg.Text('Utgå antingen från en semikolonseparerad csv-fil med rubriker eller en xml-fil.')],
    [sg.Text('Mappningen från input till metadatafil sker i den xslt-fil som ingår och som du kan kopiera och modiera efter behov.')],
    [sg.Text('')],
    [sg.Text('Sökväg till inputfil (metadatat att utgå ifrån, .csv el. .xml):*', size=52), sg.Text('Csv-separator:'), sg.Text('Funktionsval:')],
    [sg.Input(tooltip="Välj inputfil", key='inputfileB'), sg.FileBrowse('Välj fil', key="-INPUTFILE-", initial_folder=os.path.join(cwd) ), sg.Combo([';', ',', ':', '.', '|', '\t', ' '], default_value=';', size=8, key='-CSVSEPARATOR-'), sg.Combo(['Skapa xml-metadatafil', 'Enbart xml-validering', 'Csv-inputstatistik'], default_value='Skapa metadatafil', key='-FUNCTION_CHOOSER-')],
    [sg.Text('Sökväg till xsltfil:')],
    [sg.Input(tooltip="Välj xslt", key='xsltfile'), sg.FileBrowse('Välj fil', key="-XSLTFILE-", initial_folder=os.path.join(cwd) ), sg.Text ('För att transformera din input.')],
    [sg.Text('Sökväg till schemafil:')],
    [sg.Input(tooltip="Välj schemafil", key='schemafileB'), sg.FileBrowse('Välj fil', key="-SCHEMAFILE-", initial_folder=os.path.join(cwd) ), sg.Text ('Använd om du vill validera den skapade metadatafilen.')],
    [sg.Text('Döp din outputfil:', tooltip='Välj filnamn på outputfilen')],
    [sg.Input(key='-FILENAME-',size=45, tooltip='Välj filnamn på outputfilen', default_text='metadata'), sg.Combo(['.xml', '.csv'], default_value='.xml', key='-FILESUFFIX-'), sg.Text ('Använd default eller välj ett eget namn. Filsuffix läggs till per automagi.\nERROR-hantering om filnamnet redan finns i berörda kataloger.')],
#sg.Radio('Ja', 'validationready', default=False, key='-READY_FOR_VALIDATION-'), sg.Radio('Nej', 'validationready', default=True, key='-NOT_READY_FOR_VALIDATION-'
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
    [sg.Output(size=(165,20), key='output', pad=5, background_color=	'pink', echo_stdout_stderr=True)],
    [sg.Text('Outputkatalog'),sg.Input(default_text=home, tooltip="Välj katalog", size=65, key='-OUTPUTFOLDER-'), sg.FolderBrowse('Välj katalog', key='initialoutputfolder', initial_folder=Path.home()), sg.Submit('Skapa/validera fil', key='create_metadatafile', size=15,button_color='black on pink'), sg.Button('Rensa', key='clear', size=15)],
    
    ]

# Skapar "huvudfönstret"
window = sg.Window(f'FGS-Buddysbuddy v {version}',layout, font='Consolas 10', icon="Buddy.ico", resizable=True, titlebar_background_color='green')

# Variabler för att kontrollera obligatoriska värden samt trigger för att visa/dölja alla element i layouten.
#forcedvaluesdict = {}
#allvalues = False

# Funktion för att flytta den skapade filen från cwd till vald outputkatalog om annan katalog än cwd är vald som outputkatalog.
def move():

    #if os.path.exists(os.path.join(os.getcwd(), xmlfile)) == True:
        #print(f'ERROR: Det finns en fil med samma namn som det du döpt din fil till i programmets katalog {cwd}. Ta bort den eller döp om din outputfil.')
    #else:
        #print (f'Fil med samma namn finns inte i {cwd} och kan därför skapas...')
        
        #result.write_output(xmlfile)

    if (os.path.normpath(outputfolder)) == cwd:
        print(f'Grattis! Metadatafil skapad i outputkatalog {cwd}.')
    
    else:
        print (f'Flyttar till outputkatalogen...')
        try:
            shutil.move(xmlfile, outputfolder)
            print(f'Metadatafil skapad i outputkatalog {outputfolder}. Bra jobbat!')
        except:
            print(f'ERROR: Det finns redan en fil med samma namn i outputkatalogen {outputfolder}. Flytta eller radera den eller döp om din outputfil, och försök igen.')

# Funktion för att transformera inputfilen till xmlfil enligt schemafilen.
def xslttransform():
    try:
        if inputfile.endswith('.xml'):
            doc = etree.parse(inputfile)
        else:
            doc = etree.parse(csvtoxmlfile)
    except Exception as e:
        sg.popup_error_with_traceback(f'Error! Sannolikt har du valt fel csv-separator. Fil kan kanske ändå skapas, men rådet är att välja rätt separator. Info:', e)

    #Hårdkodat... lägga till uuid
    root = doc.getroot()
    for ArkivobjektID_Arenden in root.iter('ArkivobjektID_Arende'):
        ArkivobjektID_Arenden.set('Systemidentifierare', uuid.uuid4().hex)
    for ArkivobjektID_Handlingar in root.iter('ArkivobjektID_Handling'):
        ArkivobjektID_Handlingar.set('Systemidentifierare', uuid.uuid4().hex)
    
    xsl = etree.parse(xsltfile)
    transform = etree.XSLT(xsl)
    result = transform(doc)

    if os.path.exists(os.path.join(os.getcwd(), xmlfile)) == False:
            print (f'Fil med samma namn finns inte i {cwd} och kan därför skapas...')
            result.write_output(xmlfile)
            
            if schemafile != '':
                print(f'Har du valt en schemafil så valideras xmlfilen.')
                xmlschemavalidation()
            move()
    else:
        print(f'ERROR: Det finns en fil med samma namn som det du döpt din fil till i programmets katalog {cwd}. Ta bort den eller döp om din outputfil.')   

# Funktion för att konvertera csv-inputfil till xml-fil som mellanfil inför transformeringen.
def csvtoxml():
    
    try:
        df=pd.read_csv(inputfile, sep = csvseparator)

    except Exception as e:
        sg.popup_error_with_traceback(f'Error! Sannolikt har du valt fel csv-separator. Fil kan kanske ändå skapas, men rådet är att välja rätt separator. Info:', e)

    df = df.convert_dtypes()
    try:
        df.to_xml(csvtoxmlfile)
    except Exception as e:
        sg.popup_error_with_traceback(f'Error! Sannolikt har du valt fel csv-separator. Fil kan kanske ändå skapas, men rådet är att välja rätt separator. Info:', e)

# Funktion för att validera den skapade xmlfilen.
def xmlschemavalidation():
    try:
        xmlfile = filename+filesuffix
        xmlschemadoc=etree.parse(schemafile)
        xmlschema=etree.XMLSchema(xmlschemadoc)
        xmldoc=etree.parse(xmlfile)
        xmlschema.assertValid(xmldoc)
        print(f'Valid mot {schemafile}. Bra jobbat!')
    except Exception as e: print(e)

# Program-Loop
while True:
    event, values = window.read()
    match event:
        case sg.WIN_CLOSED:
            break     
        
        # Startar processen för att skapa metadatafil och/el validera om användaren trycker på "Skapa fil/validera"-knappen
        case 'create_metadatafile':
            window.find_element('output').Update('')
            window.refresh()
            inputfile = values['-INPUTFILE-']
            filename = values['-FILENAME-']
            filesuffix = values['-FILESUFFIX-']
            xmlfile = filename+filesuffix
            #csvfile = filename+filesuffix
            csvtoxmlfile = 'temp.xml'
            csvseparator = values['-CSVSEPARATOR-']
            xsltfile = values['-XSLTFILE-']
            schemafile = values['-SCHEMAFILE-']
            outputfolder = values['-OUTPUTFOLDER-']

            # Kontrollerar att inputfil och xsltfil finns och om schemafil är tom skapa metadatafil utan att validera. Denna är ännu 'standalone' till def:arna ovan.
            
            # or not inputfile.endswith('.xml') or not inputfile.endswith('.csv')
            if inputfile == '':
                print(f'Du måste välja en inputfil som har filändelse .xml eller .csv (små bokstäver)!')
            
            # Hantering när funktionsväljaren är vald till enbart validera.
            elif inputfile != '' and values['-FUNCTION_CHOOSER-'] == 'Enbart xml-validering':
                if schemafile.endswith('.xsd'):
                    print(f'Validerar inputfil {inputfile}... den flyttar inte på sig eller byter namn utan ligger kvar där du lade den, i sitt ursprungliga skick.')
                else:
                    print(f'Du måste välja en schemafil med ändelsen .xsd.')
                try:
                    xmlschemadoc=etree.parse(schemafile)
                    xmlschema=etree.XMLSchema(xmlschemadoc)
                    xmldoc=etree.parse(inputfile)
                    xmlschema.assertValid(xmldoc)
                    print(f'Valid mot {schemafile}. Bra jobbat!')
                except Exception as e: print(e)
                
            # Hantering när funktionsväljaren är vald till csv till xml-konvertering. Standalone från def:arna. Återstår fixa export av allt, knyta till outputfolder, välja separator, populera defaultvärden, tillåta namespace. Hittills endast experiment.
            elif inputfile.endswith('.csv') and values['-FUNCTION_CHOOSER-'] == 'Csv-inputstatistik':
                df = pd.read_csv(inputfile, sep=';')
                print(f'Nedan följer en sammanfattning. Se även statistics.csv i {cwd}.')
                # Antal unika per kolumn mm (alt. df.count() )
                #inputfile.info()
                df.count()
                # Antal unika värden per kolumn
                df.nunique()
                # Group data by columns 'A' and 'C', and count unique values in column 'B'
                unique_count = df.groupby(['ArkivobjektID_Arende', 'ArkivobjektID_Handling']).agg({'Lank': 'nunique'})
                # Print the result
                print(f'unique_count')
                # Alla antal unika värden per kolumn sorterat på Ärende.
                df.groupby(['ArkivobjektID_Arende']).nunique()
                num_unique_rows = df.groupby(['ArkivobjektID_Arende']).count()
                df2 = num_unique_rows
                df2.to_csv('statistics.csv')
                # Kolla dubletter
                duplicate_rows = df.duplicated()
                print('fduplicate_rows')
                num_duplicate_rows = df.duplicated().sum()
                print(f' "Number of duplicate rows: ", num_duplicate_rows')
                print(f'{num_unique_rows}')
                #try:
                    #df = pd.read_xml(inputfile, xpath='.//ArkivobjektArende')
                    #outputfile = 'outputfile.csv'
                    #df.to_csv(outputfile, sep=';')
                    #print(f'Filen {outputfile} ligger i programmets katalog {cwd}. Det som exporterades var ArkivobjektArende. Detta är bara på experimentstadiet hittills.')
                #except Exception as e: print(e)
            
            elif xsltfile == '':
                print(f'Du måste välja en xsltfil med filändelse .xsl eller .xslt (eller en schemafil om det är så att du bara vill validera xml, fixar separat exception senare)!')
             
            # Hantering av xmlfil som input
            elif inputfile.endswith('.xml') and xsltfile != '':
                xslttransform()

            # Hantering av csv som input
            else:
                if inputfile.endswith('.csv') and xsltfile != '':
                    print(f'Skapar metadatafil...')
                window.refresh()
                time.sleep(0.3)
                window.find_element('output').update('')
                window.refresh()
                csvtoxml()
                xslttransform()

            if os.path.exists(csvtoxmlfile):
                os.remove(csvtoxmlfile)
                print(f'Tempfilen raderad.') 
            else:
                print(f'Slut i rutan!') 
        
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