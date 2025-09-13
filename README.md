# TEXT BELOW IS NOT UP TO DATA BUT WILL SOON BE. PLEASE SEE THE releasenotes :sunglasses:
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
* Tabs:
  *	Input Analyser: Preview data viewer as table and by selected hierarchy keys. Pass selected keys to XSLT Mapper.
  *	XSLT Mapper: Map input file headers to schema (xsd) and genereate xslt mapping file. Option to generate, transform and validate in one go.
  *	Transformer: Transform with optional xsd validation
  *	Validator: Validate against xsd or Schematron (sch).
  *	Package Creater: A reference to FGS Buddy
	
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

- [ ] New tab Output Analyser
- [ ] XSD Analyser
- [ ] Extract metadata from files


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
- [ ] Not possible to name the xml file when using "Generate, Transform and Validate in one go".
- [ ] If you use more than one screen, the pop-up windows might turn up on another screen than expected.
- [ ] There are cases where you need to restart Buddysbuddy to generate xslt, since there are no delete buttons. It's not always possible to delete values manually.
- [ ] When configuring XSLT hierarchy with objects without a mapping, all input data is dumped into the xsl since there is no template. This should be fixed by creating empty templates.

---

## Credits :trophy:

* Viktor Lundberg - Har bidragit med [FGS Buddy](https://github.com/Viktor-Lundberg/FGSBuddy), som FGS Buddysbuddy utgått från och använt som mall, samt agerat bollplank.
* The following Python-libraries are used, thank you all!
	* The Python Standard Library
	* lxml
	* pandas
	* FreeSimpleGUI
* Glasögon till ikonen hämtade från - [http://clipart-library.com/](http://clipart-library.com/)
