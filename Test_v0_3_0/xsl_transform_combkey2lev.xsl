<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0" xmlns="http://xml.ra.se/e-arkiv/FGS-ERMS">
    <xsl:strip-space elements="*"/>
    <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
    <xsl:key name="mode_1" match="row" use="ArkivobjektID_Arende"/>
    <xsl:key name="mode_2" match="row" use="concat(ArkivobjektID_Arende, '|', ArkivobjektID_Handling)"/>
    <xsl:template match="/data">
        <Leveransobjekt>
            <ArkivobjektListaArenden>
                <xsl:apply-templates select="row[generate-id() = generate-id(key('mode_1', ArkivobjektID_Arende)[1])]" mode='mode_1'/>
            </ArkivobjektListaArenden>
        </Leveransobjekt>
    </xsl:template>
    <xsl:template match="row" mode="mode_1">
        <ArkivobjektArende>
            <ArkivobjektID>
                <xsl:value-of select="ArkivobjektID_Arende"/>
            </ArkivobjektID>
            <xsl:if test="string(KlassReferens_Arende)">
                <KlassReferens>
                    <xsl:value-of select="KlassReferens_Arende"/>
                </KlassReferens>
            </xsl:if>
            <xsl:if test="string(ArendeTyp)">
                <ArendeTyp>
                    <xsl:value-of select="ArendeTyp"/>
                </ArendeTyp>
            </xsl:if>
            <xsl:if test="string(Forvaringsplats)">
                <Forvaringsplats>
                    <xsl:value-of select="Forvaringsplats"/>
                </Forvaringsplats>
            </xsl:if>
            <xsl:if test="string(Namn)">
                <Agent>
                    <Roll>
                        <xsl:text>Registrator</xsl:text>
                    </Roll>
                    <Namn>
                        <xsl:value-of select="Namn"/>
                    </Namn>
                </Agent>
            </xsl:if>
            <xsl:if test="string(Skapad_Arende)">
                <Skapad>
                    <xsl:value-of select="Skapad_Arende"/>
                </Skapad>
            </xsl:if>
            <xsl:if test="string(Arendemening)">
                <Arendemening>
                    <xsl:value-of select="Arendemening"/>
                </Arendemening>
            </xsl:if>
            <xsl:if test="string(ArkivobjektID_Handling)">
                <ArkivobjektListaHandlingar>
                    <xsl:apply-templates mode="mode_2" select="key('mode_1', ArkivobjektID_Arende)[generate-id() = generate-id(key('mode_2', concat(ArkivobjektID_Arende, '|', ArkivobjektID_Handling))[1])]"/>
                </ArkivobjektListaHandlingar>
            </xsl:if>
        </ArkivobjektArende>
    </xsl:template>
    <xsl:template match="row" mode="mode_2">
        <ArkivobjektHandling>
            <ArkivobjektID>
                <xsl:value-of select="ArkivobjektID_Arende"/>
                <xsl:text>/</xsl:text>
                <xsl:value-of select="ArkivobjektID_Handling"/>
            </ArkivobjektID>
            <xsl:if test="string(KlassReferens_Handling)">
                <KlassReferens>
                    <xsl:value-of select="KlassReferens_Handling"/>
                </KlassReferens>
            </xsl:if>
            <xsl:if test="string(Handlingstyp)">
                <Handlingstyp>
                    <xsl:value-of select="Handlingstyp"/>
                </Handlingstyp>
            </xsl:if>
            <xsl:if test="string(Beskrivning)">
                <Beskrivning>
                    <xsl:value-of select="Beskrivning"/>
                </Beskrivning>
            </xsl:if>
            <xsl:if test="string(Rubrik)">
                <Rubrik>
                    <xsl:value-of select="Rubrik"/>
                </Rubrik>
            </xsl:if>
            <xsl:if test="string(Skapad_Handling)">
                <Skapad>
                    <xsl:value-of select="Skapad_Handling"/>
                </Skapad>
            </xsl:if>
        </ArkivobjektHandling>
    </xsl:template>
</xsl:stylesheet>