# FGS Buddy :sunglasses:


<div style="text-align: center;">

![Buddyn](Buddy.ico)<br>



En apparat som förvandlar csv eller xml till xml enligt ett givet xml-schema. Den kan även validera schemat, antingen när xmlfilen skapas eller separat. På experimentstadiet finns även en funktion som konverterar xml till csv.
</div>

## Features :star:
* Huvudarbetsprocess:
  *   Välj antingen csv-fil med rubriker (encoding utf-8, defaultseparator är semikolon) eller en xml-fil med flat strutur.
  *   Välj matchande xslt-fil där rubrikerna i csv-filen eller taggar i xml-filen mappar mot värden i xslt-filen.
  *   Väljs xml-schemafil (.xsd) om du vill validera filen i samband med skapandet.
  *   Namnge xml-outputfilen (om du vill ändra default).
  *   Välj outputkatalog (om du vill ändra default).
  *   Skapa filen!
  *   Gå till FGS Buddy med filen och infoga i FGS-paketet.
---


![](screenv1_1.PNG)


## Ideas :star:
* Analys av csv/xml
* Editering av xslt
* schematron or that kind of xslt in editing-GUI
* Utveckla xml till csv
* Mer exceptionhantering
* Ta fram .exe-fil för Windows
* Ta fram .dmg-fil för Mac
* Language-files


---

## Struktur :package:

Exempel på strukturen: <br>



---

## Kom igång :rocket:

1. [Ladda ner den senaste releasen av FGS-Buddysbuddy.](https://github.com/s99mol/FGSBuddysbuddy)
  

---

## Kända problem :warning:

* Applikationen kan ta lång tid att starta om den körs från en nätverksdisk. Rekommendationen är att alltid installera FGS-buddy på en lokal disk (exempelvis c:).
* Tooltips på flera rader laddas inte alltid. - workaround flytta muspekaren från fältet och försök igen.
* Xml till csv-funktionen är som sagt på experimentstadiet. Går inte att använda till något vettigt, än.
* Det återstår att lägga in mer exception-hantering.
* Huvudmenyn fungerar inte på Mac, åtminstone inte M1.
* Återstår att städa upp i koden.



---

## Credits :trophy:

* Viktor Lundberg - Har bidragit med FGS Buddy, som FGS Buddysbuddy utgått ifrån och använt som mall.
* Glasögon till ikonen hämtade från - http://clipart-library.com/  

---
<br>
<a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/">Creative Commons Attribution-NonCommercial 4.0 International License</a>.

