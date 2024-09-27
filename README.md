# FGS Buddysbuddy :sunglasses:

 <img align="left" src="Buddysbuddy.ico" alt="Buddysbuddy-logotyp"> En GUI-försedd metadataomat inom Buddy-projektet. Buddy-projektet vänder sig till arkivarier och sådana som håller på med strukturerad metadata inom arkivdomänen, och alla andra.
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>

---

## Features :star:
* Huvudflöde:
  *   Välj antingen csv-fil med rubriker (encoding UTF-8, defaultseparator är semikolon) eller en xml-fil med flat strutur.
  *   Välj matchande xslt-fil där rubrikerna i csv-filen eller taggar i xml-filen mappar mot värden i xslt-filen.
  *   Välj xml-schemafil (.xsd) om du vill validera filen i samband med skapandet.
  *   Namnge xml-outputfilen (om du vill ändra default).
  *   Välj outputkatalog (om du vill ändra default).
  *   Skapa filen!
  *   Välj filen som metadatafil i [FGS Buddy](https://github.com/Viktor-Lundberg/FGSBuddy) och skapa FGS-paket.
* Samt:
	* Validera färdig xml-fil separat
	* Plocka ut statistik från csv-inputfil
	* Schematron-validering genom att välja schematronfil som schemafile (v.0.2.0).
	
	Se även systemtestcasen redovisade i releasenotes. I mappen Testdata finns testfiler som kan användas för att bekanta sig med Buddysbuddy.
	
	[![Screenshot1](Screenshots/fgsbuddysbuddy_screen1.png "Liten skärmdump 1, klicka för större")](Screenshots/fgsbuddysbuddy_screen1_big.png "Stor skärmdump 1")[![Screenshot2](Screenshots/fgsbuddysbuddy_screen2.png "Liten skärmdump 2, klicka för större")](Screenshots/fgsbuddysbuddy_screen2_big.png "Stor skärmdump 2")

---

# FAQ :question:

* Vilka egenskaper bör min csv-inputfil ha? Varför fungerar det inte med min csv-fil?<br/>
  Svar:
  * Encoding: UTF-8
  * Rubriker utan blanksteg och "konstiga tecken" som '/' (å, ä, ö går bra, även '_' och '-').
  * Defaultseparator är semikolon (';') men kan ändras.
  * Får du inte någon output från sista raden, kolla att det finns radavslutningstecken, vilket skapas om sista raden är en blankrad.
  * Ett vanligt fel är att antalet separatorer inte stämmer med rubrikraden. Exempelvis kan ett semikolon i en sträng tolkas som separator.
* Varför måste min csv-fil ha rubriker? <br/>
  Svar: Det måste finnas en första rad med rubriker därför att det är dessa som i xslt-filen mappas in i xml-taggarna. Exempel:
  
  
  	```
   <Skapad> (xml-element som skrivs till xml-outputfilen)
		<xsl:value-of select="Skapad_Arende"/> ('Skapad_Arende' kommer ursprungligen från csv-filens rubrikrad.)
   </Skapad>
	``` 

---

## Ideas :star:

- [x] Funktion för uuid-tilldelning (v.0.2.0)
- [ ] Jämföra inputdata med outputdata i syfte att säkerställa processuell kvalitet
- [ ] Editering av xslt och ev schematron
- [ ] Xml till csv-konvertering
- [ ] Ta fram .exe-fil för Windows
- [ ] Ta fram .dmg-fil för Mac
- [ ] Language-files
- [ ] Anpassa testdatat till FGS 2.0
- [ ] Extrahera metadata från filer


---

## Kom igång :rocket:

1. [Ladda ner den senaste releasen och packa upp på lämplig plats.](https://github.com/s99mol/FGSBuddysbuddy/releases)
2. Kör py-filen med Python 3 (eller be Buddy-projektet att snabba på med .exe-versionen).
3. Arbeta enligt Feautures ovan.
  
---

## Kända problem/fix :warning:

* :exclamation: Rekommendation: Installera FGS-buddysbuddy på en lokal disk (exempelvis c:). Applikationen kan ta lång tid att starta om den körs från en nätverksdisk. 
* :exclamation: Rekommendation: Kör skriptet och de framtida programfilerna från katalog du som användare har skrivbehörighet till. Fil skrivs till current working directory i de flesta funktionerna.
* :question: Möjligen: Tooltips på flera rader laddas inte alltid. - workaround flytta muspekaren från fältet och försök igen.
- [ ] Det går säkert att lägga in mer exception-hantering.
- [x] Uuid-tilldelningen finns endast för specifik mappning (v.0.2.0).
- [x] Group-funktion i statistikfunktionen kräver en rubrik 'Lank' (v.0.2.0).
- [ ] Huvudmenyn fungerar inte på Mac, åtminstone inte M1.
- [ ] Allmän koduppstädning och bättre lösningar.
- [ ] Missvisande felmeddelande när man försöker skapa statistik från en xml-fil.
- [ ] På Mac får kolumnerna i statistikoutputen i det stora fönstret inte rak vänsterjustering.
- [ ] Om man först angett schemafil och sedan vill köra utan kan det vara nödvändigt att starta om programmet.
- [ ] Vid sällsynta tillfällen ges felet "Start tag expected, '<' not found, line 1, column 1" fast det är en csv-fil som inputfil. Workaround: Starta om och försök igen.
- [x] Fixa i testmappens testxslt.xsl så att tomma taggar utesluts och lägg in kommentarer (v.0.2.0).
- [x] Det ska vara FGS Buddysbuddy och inte FGS-Buddysbuddy (v.0.2.0).

---

## Credits :trophy:

* Viktor Lundberg - Har bidragit med [FGS Buddy](https://github.com/Viktor-Lundberg/FGSBuddy), som FGS Buddysbuddy utgått från och använt som mall, samt agerat bollplank.
* The following Python-libraries are used, thank you all!
	* The Python Standard Library
	* lxml
	* pandas
	* FreeSimpleGUI
* Glasögon till ikonen hämtade från - [http://clipart-library.com/](http://clipart-library.com/)
