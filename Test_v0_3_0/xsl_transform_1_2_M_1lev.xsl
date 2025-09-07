<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0" xmlns="http://xml.ra.se/e-arkiv/FGS-ERMS">
    <xsl:strip-space elements="*"/>
    <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
    <xsl:key name="mode_1" match="row" use="ArkivobjektID_Handling"/>
    <xsl:template match="/data">
        <Leveransobjekt>
            <ArkivobjektListaHandlingar>
                <xsl:apply-templates select="row[generate-id() = generate-id(key('mode_1', ArkivobjektID_Handling)[1])]" mode='mode_1'/>
            </ArkivobjektListaHandlingar>
        </Leveransobjekt>
    </xsl:template>
    <xsl:template match="row" mode="mode_1">
        <ArkivobjektHandling>
            <ArkivobjektID>
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
            <xsl:apply-templates select="key('mode_1', ArkivobjektID_Handling)" mode="repeat_mode_1"/>
        </ArkivobjektHandling>
    </xsl:template>
    <xsl:template match="row" mode="repeat_mode_1">
        <xsl:if test="string(Lank)">
            <Bilaga>
                <xsl:attribute name="Namn">
                    <xsl:value-of select="Lank"/>
                </xsl:attribute>
                <xsl:attribute name="Lank">
                    <xsl:value-of select="Lank"/>
                </xsl:attribute>
                <Bevaras>
                    <xsl:text>true</xsl:text>
                </Bevaras>
            </Bilaga>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>