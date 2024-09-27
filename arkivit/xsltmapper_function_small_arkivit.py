from xml.etree.ElementTree import QName
from lxml import etree
import os
import shutil
# could not compile select expression 'Ad acta.' = funkar ej med mellanrum verkar det som
# the content type is 'element-only' eller need attribute = fixas om tomma inte kommer med.
# <Bilaga><Bevaras>true</Bevaras></Bilaga> kommer med även när det inte finns bilaga.

cwd = os.getcwd()

class XsltMaker:
    def __init__(self, values):
        self.filedict = {}
        self.GUIvalues = dict(values)

    
    def createXslt(self, outputfolder):
        
        # Variabler för att skapa concat- och generateid-funktionerna i xslt-kodens keys
        var1 = 'concat('
        # Exception då dessa kan vara raderade
        try:
            var2 = self.GUIvalues['-ERRAND_INFILE-']
        except Exception as e:
            sg.popup_error_with_traceback(f'Error! Radera inte översta (den prepopulerade) raden i varje kategori. Info:', e)
        var3 = ", '|',"
        try:
            var4 = self.GUIvalues['-RECORD_INFILE-']
        except Exception as e:
            sg.popup_error_with_traceback(f'Error! Radera inte översta (den prepopulerade) raden i varje kategori. Info:', e)
        var5 = ')'

        #print("{}{}{} {}{}".format(var1, var2, var3, var4, var5))
 
        secondkey = "{}{}{} {}".format(var1, var2, var3, var4)
        secondkey_var5 = "{}{}".format(secondkey, var5)
        
        # Thirdkey råkar vara samma som second, behöver inte vara det
        thirdkey = "{}{}{} {}".format(var1, var2, var3, var4)
        thirdkey_var5 = "{}{}".format(thirdkey, var5)

        var6 = "key('firstkey',"
        var7 = ")[generate-id() = generate-id(key('secondkey',"
        var8 = ')[1])]'
        var9 = "row[generate-id() = generate-id(key('firstkey',"
        var10 = "key('secondkey',"
        var11 = "))[generate-id() = generate-id(key('thirdkey',"
        var12 = '))[1])]'
        var13 = '/@Systemidentifierare'
        
        genidkey1 = "{} {}{}".format(var9, var2, var8)
        genidkey2 = "{} {}{} {}{}".format(var6, var2, var7, secondkey, var12)

        concatgenidkey = "{} {}{}{}{}".format(var10, secondkey, var11, secondkey, var12)

        concatsecondkey = "{} {}{}".format(var10, secondkey_var5, var5)

        systemid_arende = "{}{}".format(var2, var13)
        systemid_handling = "{}{}".format(var4, var13)
        
        # Variabler för element i dicten
        root = self.GUIvalues['-ROOT-']
        container_1 = self.GUIvalues['-CONTAINER_1-']
        container_2 = self.GUIvalues['-CONTAINER_2-']
        container_3 = self.GUIvalues['-CONTAINER_3-']
        container_4 = self.GUIvalues['-CONTAINER_4-']
        attachment = self.GUIvalues['-ATTACHMENT-']
        
        # Variabler för attribut i dicten
        Systemidentifierare = "-ATTRIBUTID-"
        empty = "= ''"
        notempty = "!= ''"
        
        # Raderar key-value-par som inte ska ingå.
        del self.GUIvalues['outputfolderinput']
        del self.GUIvalues['outputfolder']
        
        arende_1 = self.GUIvalues['-ERRAND_INFILE-']
        arende_1_ne = "{} {}".format(arende_1, notempty)
        
        handling_1 = self.GUIvalues['-RECORD_INFILE-']
        handling_1_ne = "{} {}".format(handling_1, notempty)
        handling_1_e = "{} {}".format(handling_1, empty)
        
        
        filedict = self.filedict
        #print(filedict)
        ns = {'xsl' : "http://www.w3.org/1999/XSL/Transform",
        'xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'xs': "http://www.w3.org/2001/XMLSchema",

        }
        
        schemaLocation = str(QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation"))

        # Skapar rotelementet 'stylesheet'
        
        rotelement = etree.Element(str(QName(ns.get('xsl'),'stylesheet')), nsmap=ns)
        xslFile = etree.ElementTree(rotelement)
        rotelement.set('version', '1.0')
        rotelement.set('xmlns', 'http://xml.ra.se/e-arkiv/FGS-ERMS')
        
        # Skapar strip-space och output
        stripspace = etree.SubElement(rotelement, str(QName(ns.get('xsl'),'strip-space')))
        stripspace.set('elements', '*')
        
        output = etree.SubElement(rotelement, str(QName(ns.get('xsl'),'output')))
        output.set('method', 'xml')
        output.set('indent', 'yes')
        output.set('encoding', 'UTF-8')
        
        # Skapar keys
        
        key = etree.SubElement(rotelement, str(QName(ns.get('xsl'),'key')))
        key.set('name', 'firstkey')
        key.set('match', 'row')
        key.set('use', self.GUIvalues['-ERRAND_INFILE-'])
        
        key = etree.SubElement(rotelement, str(QName(ns.get('xsl'),'key')))
        key.set('name', 'secondkey')
        key.set('match', 'row')
        key.set('use', secondkey_var5)
        
        key = etree.SubElement(rotelement, str(QName(ns.get('xsl'),'key')))
        key.set('name', 'thirdkey')
        key.set('match', 'row')
        key.set('use', thirdkey_var5)
        
        # Skapar template leveransobjekt
        
        template = etree.SubElement(rotelement, str(QName(ns.get('xsl'),'template')))
        template.set('match', '/data')
        
        Root = etree.SubElement(template, str(root))
        ErrandList = etree.SubElement(Root, str(container_1))
        
        applytemplates = etree.SubElement(ErrandList, str(QName(ns.get('xsl'),'apply-templates')))
        applytemplates.set('select', genidkey1)
        applytemplates.set('mode', 'firstkey')

        # Skapar template Errand/Ärende
        template_arende = etree.SubElement(rotelement, str(QName(ns.get('xsl'),'template')))
        template_arende.set('match', 'row')
        template_arende.set('mode', 'firstkey')

        Errand = etree.SubElement(template_arende, str(container_2))
        
        Sysidattribute = etree.SubElement(Errand, str(QName(ns.get('xsl'),'attribute')))
        Sysidattribute.set('name', 'Systemidentifierare')
        valueof2 = etree.SubElement(Sysidattribute, str(QName(ns.get('xsl'),'value-of')))
        valueof2.set('select', systemid_arende)
        
        
        # itererar så att den stoppar in värden för key enl key-ordning. 3: ta bara de med ifylld INFILE
        for (k,v) in self.GUIvalues.items():
            if v == '':
                continue
                
            if k.startswith('-ERRAND_INFILE') and v != '':
                infile = v
                infile_notempty = "{} {}".format(infile, notempty)
                choose = etree.SubElement(Errand, str(QName(ns.get('xsl'),'choose')))
                when = etree.SubElement(choose, str(QName(ns.get('xsl'),'when')))
                when.set('test', infile_notempty)
                
            if k.startswith('-ERRAND_SCHEMA'):
                schema = v
                ArkivobjektID_arende = etree.SubElement(when, schema)
                valueof3 = etree.SubElement(ArkivobjektID_arende, str(QName(ns.get('xsl'),'value-of')))
                valueof3.set('select', infile)
                
        # Skapar RecordList
        choose = etree.SubElement(Errand, str(QName(ns.get('xsl'),'choose')))
        when = etree.SubElement(choose, str(QName(ns.get('xsl'),'when')))
        when.set('test', handling_1_e)
        otherwise = etree.SubElement(choose, str(QName(ns.get('xsl'),'otherwise')))
        RecordList = etree.SubElement(otherwise, str(container_3))
        applytemplates_handlingar = etree.SubElement(RecordList, str(QName(ns.get('xsl'),'apply-templates')))
        applytemplates_handlingar.set('select', genidkey2)
        applytemplates_handlingar.set('mode', 'secondkey')
                
        # Skapar template för Record/handling
        template_record = etree.SubElement(rotelement, str(QName(ns.get('xsl'),'template')))
        template_record.set('match', 'row')
        template_record.set('mode', 'secondkey')
        
        Record = etree.SubElement(template_record, str(container_4))

        Sysidattribute2 = etree.SubElement(Record, str(QName(ns.get('xsl'),'attribute')))
        Sysidattribute2.set('name', 'Systemidentifierare')
        valueof2 = etree.SubElement(Sysidattribute2, str(QName(ns.get('xsl'),'value-of')))
        valueof2.set('select', systemid_handling)
        
        applytemplates3 = etree.SubElement(Record, str(QName(ns.get('xsl'),'apply-templates')))
        applytemplates3.set('select', concatgenidkey)
        applytemplates3.set('mode', 'thirdkey')

        # Skapar template Arkivobjekt handlingsmetadata
        template_recordmetadata = etree.SubElement(rotelement, str(QName(ns.get('xsl'),'template')))
        template_recordmetadata.set('match', 'row')
        template_recordmetadata.set('mode', 'thirdkey')
        
        for (k,v) in self.GUIvalues.items():
            
            if k.startswith('-RECORD_INFILE'):
                infile = v
                infile_notempty = "{} {}".format(infile, notempty)
                choose = etree.SubElement(template_recordmetadata, str(QName(ns.get('xsl'),'choose')))
                when = etree.SubElement(choose, str(QName(ns.get('xsl'),'when')))
                when.set('test', infile_notempty)
            if k.startswith('-RECORD_SCHEMA'):
                schema = v
                record = etree.SubElement(when, schema)
                valueof11 = etree.SubElement(record, str(QName(ns.get('xsl'),'value-of')))
                valueof11.set('select', infile)

        applytemplates4 = etree.SubElement(template_recordmetadata, str(QName(ns.get('xsl'),'apply-templates')))
        applytemplates4.set('select', concatsecondkey)

        # Skapar template bilaga IN MED CHOICE HÄR?
        template_attachment = etree.SubElement(rotelement, str(QName(ns.get('xsl'),'template')))
        template_attachment.set('match', 'row')
        
        choose = etree.SubElement(template_attachment, str(QName(ns.get('xsl'),'choose')))
        when = etree.SubElement(choose, str(QName(ns.get('xsl'),'when')))
        
        #Attachment = etree.SubElement(template_attachment, str(attachment))
        Attachment = etree.SubElement(when, str(attachment))
        
        for (k,v) in self.GUIvalues.items():
            
            
            if k.startswith('-ATTACHMENT_INFILE'):
        
                infile = v
                infile_notempty = "{} {}".format(infile, notempty)
            
                when.set('test', infile_notempty)

            if k.startswith('-ATTACHMENT_SCHEMA'):
                schema = v
                attribute_bilaganamn = etree.SubElement(Attachment, str(QName(ns.get('xsl'),'attribute')))
                attribute_bilaganamn.set('name', schema)
                valueof17 = etree.SubElement(attribute_bilaganamn, str(QName(ns.get('xsl'),'value-of')))
                valueof17.set('select', infile)

        Bevaras = etree.SubElement(Attachment, str('Bevaras')).text = 'true'

        # Skapar mappningsfilen
        
        xslFile.write(f'mappningsfil.xsl', xml_declaration=True, encoding='utf-8', pretty_print=True)
        
        #shutil.move('mappningsfil.xsl', outputfolder)
        
        if (os.path.normpath(outputfolder)) == cwd:
            print(f'Grattis! Mappningsfil skapad i outputkatalog {cwd}.')
    
        else:
            mappningsfil = 'mappningsfil.xsl'
            print (f'Flyttar till outputkatalogen...')
            try:
                shutil.move(mappningsfil, outputfolder)
                print(f'Mappningsfil skapad i outputkatalog {outputfolder}. Bra jobbat!')
            except:
                print(f'ERROR: Det finns redan en fil med samma namn i outputkatalogen {outputfolder}. Flytta eller radera den eller döp om din outputfil, och försök igen.')

