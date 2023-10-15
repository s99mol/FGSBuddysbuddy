<?xml version="1.0"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
<ns uri="http://xml.ra.se/e-arkiv/FGS-ERMS" prefix="fgs"/>
  <pattern>
    <rule context="fgs:Leveransobjekt/fgs:ArkivobjektListaArenden/fgs:ArkivobjektArende/fgs:Agent">
      <assert test="fgs:Roll='Registrator' or fgs:Roll='Handläggare'">
      Rollen är varken Handläggare eller Registrator!
      </assert>
    </rule>
  </pattern>
  <pattern>
    <rule context="fgs:Leveransobjekt/fgs:ArkivobjektListaArenden/fgs:ArkivobjektArende/fgs:ArkivobjektListaHandlingar/fgs:ArkivobjektHandling">
      <report test="fgs:KlassReferens='0'">
      Klassreferens är 0 men får inte vara det!
      </report>
    </rule>
  </pattern>
</schema>
