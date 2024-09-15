import os
import PySimpleGUI as sg
import webbrowser
from io import StringIO
from lxml import etree
from lxml import isoschematron
import pandas as pd
import uuid
import shutil
from pathlib import Path
import time
import xsltmapper_function_small_arkivit as Xsltfunc
#import json

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

# Funktion för att skapa popup-fönstret "Om FGS Buddysbuddysbuddy"
def buddywindow():
    # Hämtar alla releasenotes från txt-fil och lägger i variabeln releasenotes
    with open('releasenotes.txt', encoding='utf-8') as releasenotesdoc:
        releasenotes = releasenotesdoc.read()

    # Layout för fönstret
    aboutlayout = [
        [sg.Text('FGS Buddysbuddy', font='Arial 12 bold', size=30)],
        [sg.Text(f'Version: {version}\nSkapad av: Martin Olsson\nLicens: Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)', font='Consolas 10')],
        [sg.Text('Baserad på: Viktor Lundbergs FGS-Buddy v. 1.1.0', font='Consolas 10')],
        [sg.Text('FGS Buddysbuddy på github', font='Consolas 10 underline', text_color='blue', enable_events=True, key='githublink')],
        [sg.Text('FGS-Buddy på github', font='Consolas 10 underline', text_color='blue', enable_events=True, key='githublink2')],
        [sg.Text('', font='Arial 12 bold', size=30)],
        [sg.Text('Release notes', font='Arial 10 bold', size=30)],
        [sg.Text(releasenotes, font='Consolas 8')],
        [sg.Button('Ok', key='Exit', size=7)]
    ]

    # Skapar nya fönstret
    about = sg.Window('Om FGS Buddysbuddy', aboutlayout, icon="Buddysbuddy.ico")
    
    # Programloop för "Om FGS Buddysbuddy"-fönstret.
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
version = 'arkivit'

# Current working directory
cwd = os.getcwd()
#cwd = Path.home()

# hemfoldern (ska övergå till Pathlib helt)
home = Path.home()

# Sätter färgtema
sg.theme('greenMono')

innehall = [  
    [sg.Text('Metadataomaten FGS Buddysbuddy', font='Arial 12 bold', size=75)],
    [sg.Text('Komplement till FGS Buddy (länk i Hjälp-menyn). Skapa metadatafil, validera mot xmlschema/schematron, statistik från csv-fil.')],
    [sg.Text('Mappningen från input till metadatafil görs i en xslt-fil. Det finns en i testdatat som du kan modifiera efter behov.')],
    [sg.Text('')],
    [sg.Text('Sökväg till inputfil med metadatat:*', size=52), sg.Text('Csv-separator:'), sg.Text('Välj vad du vill göra med inputfilen:')],
    [sg.Input(tooltip="Välj inputfil (.xml, .csv)", key='inputfileB'), sg.FileBrowse('Välj fil', tooltip=".xml eller .csv, utf-8", key="-INPUTFILE-", initial_folder=os.path.join(cwd) ), sg.Combo([';', ',', ':', '.', '|', '\t'], default_value=';', size=8, tooltip='Den tomma är tab.', key='-CSVSEPARATOR-'), sg.Combo(['Skapa xml-metadatafil', 'Mappa (skapa xslt)', 'Enbart xml-validering', 'Csv-inputstatistik', 'Schematron (experimental)'], default_value='Skapa metadatafil', key='-FUNCTION_CHOOSER-')],
    [sg.Text('Sökväg till xsltfilen som transformerar din input:')],
    [sg.Input(tooltip="Välj xslt (.xsl, .xslt)", key='xsltfile'), sg.FileBrowse('Välj fil', tooltip=".xsl eller .xslt", key="-XSLTFILE-", initial_folder=os.path.join(cwd) )],
    [sg.Text('Sökväg till schemafil som validerar xmlfilen:')],
    [sg.Input(tooltip="Välj schemafil (.xsd)", key='schemafileB'), sg.FileBrowse('Välj fil', tooltip=".xsd", key="-SCHEMAFILE-", initial_folder=os.path.join(cwd) )],
    [sg.Text('Döp din outputfil:', tooltip='Välj filnamn på outputfilen')],
    [sg.Input(key='-FILENAME-',size=45, tooltip='Välj filnamn på outputfilen. Använd default eller välj ett eget namn. Filsuffix läggs till per automagi.\nERROR-hantering om filnamnet redan finns i berörda kataloger.', default_text='metadata'), sg.Combo(['.xml', '.csv'], default_value='.xml', key='-FILESUFFIX-')],
    ]

space = [
    [sg.Text('', font='Arial 8 bold', size=30)],
    ]
    
# Menyraden
meny = [
    ['FGS-dokumentation', ['Om FGS-scheman','FGS-scheman']],['Hjälp', ['Om FGS Buddysbuddy']]
     ]
    
# GUI layout
layout = [
    [sg.MenuBar(meny, background_color='Pink')],
    [sg.Column(space)],
    [sg.Column(innehall, vertical_alignment='top')],
    [sg.Text('')],
    [sg.Output(size=(165,20), key='output', pad=5, background_color= 'pink', echo_stdout_stderr=True)],
    [sg.Text('Outputkatalog'),sg.Input(default_text=home, tooltip="Välj katalog om du vill ha annan än den förinställda.", size=65, key='-OUTPUTFOLDER-'), sg.FolderBrowse('Välj katalog', key='initialoutputfolder', initial_folder=Path.home()), sg.Submit('Utför!', tooltip="Vad som utförs beror på dina inställningar: Skapa fil, validera, csv-statistik.", key='create', size=15,button_color='black on pink'), sg.Button('Rensa', key='clear', size=15)],   
    ]

# Skapar "huvudfönstret"
window = sg.Window(f'FGS Buddysbuddy v {version}',layout, font='Consolas 10', icon="Buddysbuddy.ico", resizable=True, titlebar_background_color='green')

# Funktion för att plocka ut statistik från csv-inputfil. MER ATT JOBBA PÅ
def statistics():
    print(f'Nedan följer en sammanfattning. Se all statistik i mappen csv_statistics i {cwd}.')
    # Antal unika per kolumn mm (alt. df.count() )
    #df.info()
    # Antal unika värden per kolumn
    s1 = df.count()
    s2 = df.nunique()
    df1 = pd.concat([s1, s2], axis=1)
    df1.rename(columns = {0:'Antal', 1:'Antal unika'}, inplace = True)
    print(df1)
    # Gruppera på kolumner
    unique_count = df.groupby([values['-COLUMN_CHOOSER_1-'], values['-COLUMN_CHOOSER_2-'], values['-COLUMN_CHOOSER_3-']]).nunique()
    print(unique_count)
    # Alla antal unika värden per kolumn sorterat på användarens val.
    df.groupby([values['-COLUMN_CHOOSER_1-']]).nunique()
    num_unique_rows = df.groupby([values['-COLUMN_CHOOSER_1-']]).count()
    df2 = num_unique_rows
    # Kolla dubletter
    duplicate_rows = df.duplicated()
    print(duplicate_rows)
    num_duplicate_rows = df.duplicated().sum()
    print("Number of duplicate rows: ", num_duplicate_rows)
    print(num_unique_rows)
    csvstatisticsfolder = './csv_statistics'
    path = os.path.join('csv_statistics_' + str(uuid.uuid4().hex))
    
    if os.path.exists(os.path.join(os.getcwd(), csvstatisticsfolder)) == True:
        path = os.path.join('csv_statistics_' + str(uuid.uuid4().hex))
        os.mkdir(path)
        os.chdir(path)
        df1.to_csv('totals_and_unique.csv')
        df2.to_csv('unique_rows.csv')
        unique_count.to_csv('unique_count.csv')
        duplicate_rows.to_csv('duplicate_rows.csv')
        #num_duplicate_rows.to_csv('')
        num_unique_rows.to_csv('num_unique_rows.csv')
        os.chdir(cwd)
    else:
        csvstatisticsfolder = './csv_statistics'
        path = csvstatisticsfolder
        os.mkdir(path)
        df1.to_csv('./csv_statistics/totals_and_unique.csv')
        df2.to_csv('./csv_statistics/unique_rows.csv')
        unique_count.to_csv('./csv_statistics/unique_count.csv')
        duplicate_rows.to_csv('./csv_statistics/duplicate_rows.csv')
        #num_duplicate_rows.to_csv('')
        num_unique_rows.to_csv('./csv_statistics/num_unique_rows.csv')
        
# Funktion för att validera xml-fil med schematron-regler i vald schematronfil (.sch)
def schematron():

    # Parse schema
    sct_doc = etree.parse(schematronfile)
    schematron = isoschematron.Schematron(sct_doc, store_report = True)
       
    notValid = inputfile
    
    # Parse xml
    doc = etree.parse(notValid)

    # Validera mot schema
    validationResult = schematron.validate(doc)

    # Valideringsrapport
    report = schematron.validation_report

    print("is valid: " + str(validationResult))
    print(type(report))
    print(report)
    report.write('Schematronreport.xml', encoding='UTF-8')
    print(f'Schematronreport.xml sparad i {cwd}.')
    

# Funktion för att konvertera csv-inputfil till xml-fil som mellanfil inför transformeringen.
def csvtoxml():
    try:
        df=pd.read_csv(inputfile, sep = csvseparator, engine='python')
    except Exception as e:
        sg.popup_error_with_traceback(f'Error! Sannolikt har du valt fel csv-separator. Fil kan kanske ändå skapas, men rådet är att välja rätt separator. Info:', e)
    df = df.convert_dtypes()
    try:
        df.to_xml(csvtoxmlfile)
    except Exception as e:
        sg.popup_error_with_traceback(f'Error! Sannolikt har du valt fel csv-separator. Fil kan kanske ändå skapas, men rådet är att välja rätt separator. Info:', e)

# Funktion för att transformera inputfilen till xmlfil enligt schemafilen.
def xslttransform():
    try:
        if inputfile.endswith('.xml'):
            doc = etree.parse(inputfile)
        else:
            doc = etree.parse(csvtoxmlfile)
    except Exception as e:
        sg.popup_error_with_traceback(f'Error! Sannolikt har du valt fel csv-separator. Fil kan kanske ändå skapas, men rådet är att välja rätt separator. Info:', e)

    elemList = []
    
    for elem in doc.iter():
        elemList.append(elem.tag)
    
    # Tar bort (ev) dubletter, skriver ut listan (ej  nödvändigt)
    elemList = list(set(elemList))
    print(elemList)
        
    layoutelementchooser = [
        [sg.Text('Sätt uuid till Systemidentifierare (attr.):', tooltip='Du måste ha Systemidentifierare som attribut i din xslt-fil för det valda elementet.'), sg.Combo(elemList, key='-ELEMENT_CHOOSER_1-')],
        [sg.Text('Sätt uuid till Systemidentifierare (attr.):', tooltip='Du måste ha Systemidentifierare som attribut i din xslt-fil för det valda elementet.'), sg.Combo(elemList, key='-ELEMENT_CHOOSER_2-')],
        [sg.Button('Skapa', size=15, button_color='black on pink'), sg.Button('Stäng')] 
        ]

    # Skapar elementväljarfönster för uuid. MER ATT JOBBA PÅ. Gör det valbart vilket attribut peka på, 0:* element.
    elementchooserwindow = sg.Window(f'FGS Buddysbuddy v {version}',layoutelementchooser, font='Consolas 10', icon="Buddysbuddy.ico", resizable=True, titlebar_background_color='green')

    while True:
        event, values = elementchooserwindow.read()
        print(event, values)
        if event == sg.WIN_CLOSED or event == 'Stäng':
            break
        if event == 'Skapa':
            if values['-ELEMENT_CHOOSER_1-'] in elemList and values['-ELEMENT_CHOOSER_2-'] in elemList:
                root = doc.getroot()
                for values['-ELEMENT_CHOOSER_1-'] in root.iter(values['-ELEMENT_CHOOSER_1-']):
                    values['-ELEMENT_CHOOSER_1-'].set('Systemidentifierare', uuid.uuid4().hex)
                for values['-ELEMENT_CHOOSER_2-'] in root.iter(values['-ELEMENT_CHOOSER_2-']):
                    values['-ELEMENT_CHOOSER_2-'].set('Systemidentifierare', uuid.uuid4().hex)
                break
                
            elif values['-ELEMENT_CHOOSER_1-'] in elemList:
                root = doc.getroot()
                for values['-ELEMENT_CHOOSER_1-'] in root.iter(values['-ELEMENT_CHOOSER_1-']):
                    values['-ELEMENT_CHOOSER_1-'].set('Systemidentifierare', uuid.uuid4().hex)
                break
                
            elif values['-ELEMENT_CHOOSER_2-'] in elemList:
                root = doc.getroot()
                for values['-ELEMENT_CHOOSER_2-'] in root.iter(values['-ELEMENT_CHOOSER_2-']):
                    values['-ELEMENT_CHOOSER_2-'].set('Systemidentifierare', uuid.uuid4().hex)
                break
            
            else:
                print('Välj minst en eller klicka Stäng för att gå vidare utan att skapa uuid till Systemidentifierare!')
    
    elementchooserwindow.close()

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

# Funktion för att flytta den skapade filen från cwd till vald outputkatalog om annan katalog än cwd är vald som outputkatalog.
def move():
    if (os.path.normpath(outputfolder)) == cwd:
        print(f'Grattis! Metadatafil skapad i outputkatalog {cwd}.')
    
    else:
        print (f'Flyttar till outputkatalogen...')
        try:
            shutil.move(xmlfile, outputfolder)
            print(f'Metadatafil skapad i outputkatalog {outputfolder}. Bra jobbat!')
        except:
            print(f'ERROR: Det finns redan en fil med samma namn i outputkatalogen {outputfolder}. Flytta eller radera den eller döp om din outputfil, och försök igen.')    

# Funktion för mappningsfönstret
def mapping():
    if inputfile.endswith('.csv'):
        csvtoxml()
        doc = etree.parse(csvtoxmlfile)
    else:
        try:
            if inputfile.endswith('.xml'):
                doc = etree.parse(inputfile)
            else:
                doc = etree.parse(csvtoxmlfile)
        except Exception as e:
            sg.popup_error_with_traceback(f'Error! Sannolikt har du valt fel csv-separator. Fil kan kanske ändå skapas, men rådet är att välja rätt separator. Info:', e)
    
    elemList = []
    
    for elem in doc.iter():
        elemList.append(elem.tag)
    
    # Tar bort (ev) dubletter, skriver ut listan (ej nödvändigt)
    elemList = list(set(elemList))
    #print(elemList)
    elemList.sort()
    xsddoc = 'arendehantering.xsd'
    tree = etree.parse(xsddoc)
    #attrListxsd = tree.xpath(".//@ref")
    attrListxsd_arende = tree.xpath("xs:complexType[@name='ArkivobjektArendeTyp']/xs:sequence/xs:element/@ref", namespaces={'xs':'http://www.w3.org/2001/XMLSchema'})
    attrListxsd_handling = tree.xpath("xs:complexType[@name='ArkivobjektHandlingTyp']/xs:sequence/xs:element/@ref", namespaces={'xs':'http://www.w3.org/2001/XMLSchema'})
    attrListxsd_bilaga = tree.xpath("xs:complexType[@name='BilagaTyp']/xs:attribute/@name", namespaces={'xs':'http://www.w3.org/2001/XMLSchema'})
    attrListxsd_bilagatyp = tree.xpath("xs:element[@name='Bilaga']/@name", namespaces={'xs':'http://www.w3.org/2001/XMLSchema'})

    attrListxsd_levobjekt = tree.xpath("xs:complexType[@name='LeveransobjektTyp']/xs:sequence/xs:element/@ref", namespaces={'xs':'http://www.w3.org/2001/XMLSchema'})
    attrListxsd_abstruktur = tree.xpath("xs:complexType[@name='ArkivbildarStrukturTyp']/xs:attribute/@name", namespaces={'xs':'http://www.w3.org/2001/XMLSchema'})
    attrListxsd_arkivbildare = tree.xpath("xs:complexType[@name='ArkivbildareTyp']/xs:sequence/xs:element/@name", namespaces={'xs':'http://www.w3.org/2001/XMLSchema'})
    attrListxsd_vir = tree.xpath("xs:complexType[@name='VerksamhetsbaseradArkivredovisningTyp']/xs:sequence/xs:element/@name", namespaces={'xs':'http://www.w3.org/2001/XMLSchema'})
    attrListxsd_arendelista = tree.xpath("xs:element[@name='ArkivobjektListaArenden']/@name", namespaces={'xs':'http://www.w3.org/2001/XMLSchema'})
    attrListxsd_arendetyp = tree.xpath("xs:complexType[@name='ArkivobjektListaArendenTyp']/xs:sequence/xs:element/@name", namespaces={'xs':'http://www.w3.org/2001/XMLSchema'})
    attrListxsd_handlingtyp = tree.xpath("xs:complexType[@name='ArkivobjektListaHandlingarTyp']/xs:sequence/xs:element/@name", namespaces={'xs':'http://www.w3.org/2001/XMLSchema'})
    attrListxsd_handlinglista = tree.xpath("xs:element[@name='ArkivobjektListaHandlingar']/@name", namespaces={'xs':'http://www.w3.org/2001/XMLSchema'})
    attrListxsd_rot = tree.xpath("xs:element[@name='Leveransobjekt']/@name", namespaces={'xs':'http://www.w3.org/2001/XMLSchema'})

    attrListxsd_arkivbildaretyp = tree.xpath("xs:complexType[@name='ArkivbildarStrukturTyp']/xs:sequence/xs:element/@name", namespaces={'xs':'http://www.w3.org/2001/XMLSchema'})

    attrListxsd_restriktiontyp = tree.xpath("xs:element[@name='Restriktion']/@name", namespaces={'xs':'http://www.w3.org/2001/XMLSchema'})
    # fixa attribute
    attrListxsd_restriktion = tree.xpath("xs:complexType[@name='RestriktionsTyp']/xs:sequence/xs:element/@name", namespaces={'xs':'http://www.w3.org/2001/XMLSchema'})


    root = [

        [sg.Input(attr, size=23, key='-ROOT-', tooltip='Metadatatagg'),
            ] for attr in attrListxsd_rot
        ]


    arendetyp = [

        [sg.Input(attr, size=23, key='-CONTAINER_2-', tooltip='Metadatatagg'), sg.Text('i'),
            ] for attr in attrListxsd_arendetyp

        ]
    
    arendelista = [
    
        [sg.Input(attr, size=23, key='-CONTAINER_1-', tooltip='Metadatatagg'), sg.Text(':'),
            ] for attr in attrListxsd_arendelista
        
        ]

    handlingtyp = [

        [sg.Input(attr, size=23, key='-CONTAINER_4-', tooltip='Metadatatagg'), sg.Text('i'),
            ] for attr in attrListxsd_handlingtyp

        ]
    
    handlinglista = [
    
        [sg.Input(attr, size=23, key='-CONTAINER_3-', tooltip='Metadatatagg'), sg.Text(':'),
            ] for attr in attrListxsd_handlinglista
        
        ]
    
    bilagatyp = [
    
        [sg.Input(attr, size=23, key='-ATTACHMENT-', tooltip='Metadatatagg'), sg.Text(':'),
            ] for attr in attrListxsd_bilagatyp
        
        ]


    def create_row(row_counter, row_number_view):
        row =  [sg.pin(
            sg.Col([[
                #sg.Text('Mappa Arende'),
                sg.Combo(elemList, key=('-ERRAND_INFILE-'), default_value='Mappa_från...'),
                sg.Combo(attrListxsd_arende, key=('-ERRAND_SCHEMA-'), default_value='Mappa_till...'),
                sg.Button("X", border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), key=('-DEL-', row_counter), tooltip='Ta bort raden'),
                ]],
            key=('-ROW-', row_counter)
            ))]
        return row

    def create_row2(row_counter, row_number_view):
        row2 =  [sg.pin(
            sg.Col([[
                #sg.Text('Mappa Handling'),
                sg.Combo(elemList, key=('-RECORD_INFILE-'), default_value='Mappa_från...'),
                sg.Combo(attrListxsd_handling, key=('-RECORD_SCHEMA-'), default_value='Mappa_till...'),
                sg.Button("X", border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), key=('-DEL2-', row_counter), tooltip='Ta bort raden'),
                ]],
            key=('-ROW2-', row_counter)
            ))]
        return row2

    def create_row3(row_counter, row_number_view):
        row3 =  [sg.pin(
            sg.Col([[
                #sg.Text('Mappa Bilaga'),
                sg.Combo(elemList, key=('-ATTACHMENT_INFILE-'), default_value='Mappa_från...'),
                sg.Combo(attrListxsd_bilaga, key=('-ATTACHMENT_SCHEMA-'), default_value='Mappa_till...'),
                #sg.Text('+', enable_events=True, k='-ADD_ITEM3-', tooltip='Lägg till en rad'),
                sg.Button("X", border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), key=('-DEL3-', row_counter), tooltip='Ta bort raden'),
                ]],
            key=('-ROW3-', row_counter)
            ))]
        return row3



    layout = [  [sg.Text('Mappa inputrubriker till valt schemam med root'), sg.Column(root), sg.Text('OBS: TA INTE BORT DEN ÖVERSTA RADEN I ÄRENDE OCH HANDLING.', font='15')],
                #[sg.Column(root)],
                [sg.Column(arendetyp), sg.Column(arendelista)],
                [sg.Column([create_row(0, 1)], k='-ROW_PANEL-')],
                [sg.Text('+Rad', enable_events=True, k='-ADD_ITEM-', tooltip='Lägg till en ärenderad')],
                [sg.Column(handlingtyp), sg.Column(handlinglista)],
                [sg.Column([create_row2(0, 1)], k='-ROW_PANEL2-')],
                [sg.Text('+Rad', enable_events=True, k='-ADD_ITEM2-', tooltip='Lägg till en handlingsrad')],
                [sg.Column(bilagatyp)],
                [sg.Column([create_row3(0, 1)], k='-ROW_PANEL3-')],
                [sg.Text('+Rad', enable_events=True, k='-ADD_ITEM3-', tooltip='Lägg till en bilagerad')],
            
                [sg.Submit('Skapa mappning', key='createXslt', size=15, button_color='black on pink'), sg.Text('', size=15),
                sg.Button("Stäng", enable_events=True, key='-EXIT-', tooltip='Stäng fönstret'),
                ],
                [sg.Output(size=(80,5), key='output', pad=5, background_color=	'pink', echo_stdout_stderr=True)],
                [sg.Text('Outputkatalog'),sg.Input(default_text=cwd, tooltip="Välj katalog", size=65, key='outputfolderinput'), sg.FolderBrowse('Välj katalog', key="outputfolder", initial_folder=os.path.join(cwd))],
            
                ]

    window = sg.Window('Buddys Mappomat', 
        layout,  use_default_focus=False, font='Consolas 10')

    # Skapar "huvudfönstret"

    row_counter = 0
    row_number_view = 1
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == '-EXIT-':
            break
        elif event == '-ADD_ITEM-':
            row_counter += 1
            row_number_view += 1
            window.extend_layout(window['-ROW_PANEL-'], [create_row(row_counter, row_number_view)])
        elif event == '-ADD_ITEM2-':
            row_counter += 1
            row_number_view += 1
            window.extend_layout(window['-ROW_PANEL2-'], [create_row2(row_counter, row_number_view)])
        elif event == '-ADD_ITEM3-':
            row_counter += 1
            row_number_view += 1
            window.extend_layout(window['-ROW_PANEL3-'], [create_row3(row_counter, row_number_view)])
        elif event[0] == '-DEL-':
            row_number_view -= 1
            window[('-ROW-', event[1])].update(visible=False)
            window[('-ROW-', event[1])].Widget.pack_forget()
            window[('-ROW-', event[1])].Widget.destroy()
        elif event[0] == '-DEL2-':
            row_number_view -= 1
            window[('-ROW2-', event[1])].update(visible=False)
            window[('-ROW2-', event[1])].Widget.pack_forget()
            window[('-ROW2-', event[1])].Widget.destroy()
        elif event[0] == '-DEL3-':
            row_number_view -= 1
            window[('-ROW3-', event[1])].update(visible=False)
            window[('-ROW3-', event[1])].Widget.pack_forget()
            window[('-ROW3-', event[1])].Widget.destroy()
        
        
        else:
            print(values)
            values = {k:v for k,v in values.items() if v != ''}
            values = {k:v for k,v in values.items() if v != '*Exception occurred*'}
            event == 'createXslt'
            window.find_element('output').Update('')
            window.refresh()

            print(f'Skapar mappningsfilen...')
            window.refresh()
            xsltmapper = Xsltfunc.XsltMaker(values)
            if values['outputfolder'] == '':
                outputfolder = os.path.join(cwd)
            else:
                outputfolder = os.path.join(values['outputfolder'])
                xsltmapper.createXslt(outputfolder)
                #xsltmapper.outputXslt(cwd, outputfolder)
                time.sleep(0.3)
            
                window.find_element('output').update('')
                window.refresh() 
                print(values)
            print(f'Grattis! Mappningsfilen skapad i outputkatalog {outputfolder}.')
    
    window.close()
    
    
# Program-Loop
while True:
    event, values = window.read()
    match event:
        case sg.WIN_CLOSED:
            break     
        
        # Startar processen för att skapa metadatafil och/el validera om användaren trycker på "Skapa fil/validera"-knappen
        case 'create':
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

            # Kontrollerar att inputfil är vald.
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
                
            # Plocka ut statistik från csv-inputfil
            elif inputfile.endswith('.csv') and values['-FUNCTION_CHOOSER-'] == 'Csv-inputstatistik':
                df = pd.read_csv(inputfile, sep = csvseparator, engine='python')
                df = df.convert_dtypes()
                columnchoices = df.columns.tolist()
                
                 # Layoyt för val av kolumner för csv-statistik.
                layoutcolchooser = [
                    [sg.Text('Gruppering nivå 1:'), sg.Combo(columnchoices, key='-COLUMN_CHOOSER_1-')],
                    [sg.Text('Gruppering nivå 2:'), sg.Combo(columnchoices, key='-COLUMN_CHOOSER_2-')],
                    [sg.Text('Gruppering nivå 3:'), sg.Combo(columnchoices, key='-COLUMN_CHOOSER_3-')],
                    [sg.Button('Skapa', size=15, button_color='black on pink'), sg.Button('Stäng')] 
                    ]

                # Skapar kolumnväljarfönster för csv-statistik.
                colchooserwindow = sg.Window(f'FGS Buddysbuddy v {version}',layoutcolchooser, font='Consolas 10', icon="Buddysbuddy.ico", resizable=True, titlebar_background_color='green')

                while True:
                    event, values = colchooserwindow.read()
                    print(event, values)
                    if event == sg.WIN_CLOSED or event == 'Stäng':
                        break
                    if event == 'Skapa':
                        if values['-COLUMN_CHOOSER_1-'] in columnchoices and values['-COLUMN_CHOOSER_2-'] in columnchoices and values['-COLUMN_CHOOSER_3-'] in columnchoices:
                            statistics()
                        else:
                            print('Alla måste fyllas i!')
                
                colchooserwindow.close()
                        
                # Hantering när funktionsväljaren är vald till csv till xml-konvertering. Standalone från def:arna. Återstår fixa export av allt, knyta till outputfolder, välja separator, populera defaultvärden, tillåta namespace. Hittills endast experiment.

            # Hantering vid schematron-experiment. Plan att schematronvalidering ska ingå i huvudflödet.
            elif values['-FUNCTION_CHOOSER-'] == 'Schematron (experimental)':
                if schemafile.endswith('.sch'):
                    schematronfile = values['-SCHEMAFILE-']
                    schematron()
                else:
                    print(f'Du måste välja en schematronfil med ändelsen .sch i fältet för schemafil för att kunna validera din inputfil.')
            
            # Hantering vid mappning av inputfil till xslt-fil (via dict)
            elif values['-FUNCTION_CHOOSER-'] == 'Mappa (skapa xslt)':
                mapping()
            
            # Hantering när ingen xslt-fil är vald.
            elif xsltfile == '':
                print(f'Du måste välja en xsltfil med filändelse .xsl eller .xslt!')

            # Hantering när ingen input finns i 'Döp din outputfil' (default raderas med rensaknappen).
            elif filename == '':
                print(f'Du måste skriva in ett värde i Döp din outputfil så att din metadatafil får ett filnamn!')
                
            # Hantering när ingen input finns i outputkatalog (default raderas med rensaknappen).
            elif outputfolder == '':
                print(f'Du måste välja en outputkatalog så att du vet var din metadatafil hamnar!')
             
            # Hantering av xmlfil som input
            elif inputfile.endswith('.xml') and xsltfile != '':
                xslttransform()

            # Hantering av csv som input
            else:
                if inputfile.endswith('.csv') and xsltfile != '':
                    print(f'Skapar metadatafil...')
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
        case 'Om FGS-scheman':
            webbrowser.open('https://riksarkivet.se/faststallda-kommande-fgser')
        case 'FGS-scheman':
            webbrowser.open('http://xml.ra.se/e-arkiv/')
        
        # Meny - Hjälp
        case 'Om FGS Buddysbuddy':
            sg.Window.disappear(window)
            buddywindow()
            sg.Window.reappear(window)