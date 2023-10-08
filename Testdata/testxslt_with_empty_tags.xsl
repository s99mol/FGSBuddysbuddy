<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://xml.ra.se/e-arkiv/FGS-ERMS">
	<xsl:strip-space elements="*"/>
	<xsl:output method="xml" indent="yes" encoding="utf-8"/>
	<xsl:key name="firstkey" match="row" use="ArkivobjektID_Arende"/>
	<xsl:key name="secondkey" match="row" use="concat(ArkivobjektID_Arende, '|', ArkivobjektID_Handling)"/>
	<xsl:key name="thirdkey" match="row" use="concat(ArkivobjektID_Arende, '|', ArkivobjektID_Handling)"/>
	<xsl:template match="/data">
		<Leveransobjekt>
			<ArkivobjektListaArenden>
				<xsl:apply-templates select="row[generate-id() = generate-id(key('firstkey', ArkivobjektID_Arende)[1])]" mode="firstkey"/>
			</ArkivobjektListaArenden>
		</Leveransobjekt>
	</xsl:template>
	<xsl:template match="row" mode="firstkey">
		<ArkivobjektArende>
			<xsl:attribute name="Systemidentifierare">
				<xsl:value-of select="ArkivobjektID_Arende/@Systemidentifierare"/>
			</xsl:attribute>
			<ArkivobjektID>
				<xsl:value-of select="ArkivobjektID_Arende"/>
			</ArkivobjektID>
			<KlassReferens>
				<xsl:value-of select="KlassReferens_Arende"/>
			</KlassReferens>
			<ArendeTyp>
				<xsl:value-of select="ArendeTyp"/>
			</ArendeTyp>
			<Forvaringsplats>
				<xsl:value-of select="Forvaringsplats"/>
			</Forvaringsplats>
			<Agent>
				<Roll>Registrator</Roll>
				<Namn>
					<xsl:value-of select="Namn"/>
				</Namn>
			</Agent>
			<Skapad>
				<xsl:value-of select="Skapad_Arende"/>
			</Skapad>
			<Arendemening>
				<xsl:value-of select="Arendemening"/>
			</Arendemening>
			<xsl:choose>
				<xsl:when test="ArkivobjektID_Handling = ''">
				</xsl:when>
				<xsl:otherwise>
					<ArkivobjektListaHandlingar>
						<xsl:apply-templates select="key('firstkey', ArkivobjektID_Arende)[generate-id() = generate-id(key('secondkey', concat(ArkivobjektID_Arende, '|', ArkivobjektID_Handling))[1])]" mode="secondkey"/>
					</ArkivobjektListaHandlingar>
				</xsl:otherwise>
			</xsl:choose>
		</ArkivobjektArende>
	</xsl:template>
	<xsl:template match="row" mode="secondkey">
		<ArkivobjektHandling>
			<xsl:attribute name="Systemidentifierare">
				<xsl:value-of select="ArkivobjektID_Handling/@Systemidentifierare"/>
			</xsl:attribute>
			<xsl:apply-templates select="key('secondkey', concat(ArkivobjektID_Arende, '|', ArkivobjektID_Handling))[generate-id() = generate-id(key('thirdkey', concat(ArkivobjektID_Arende, '|', ArkivobjektID_Handling))[1])]" mode="thirdkey"/>
		</ArkivobjektHandling>
	</xsl:template>
	<xsl:template match="row" mode="thirdkey">
		<ArkivobjektID>
			<xsl:value-of select="ArkivobjektID_Handling"/>
		</ArkivobjektID>
		<KlassReferens>
			<xsl:value-of select="KlassReferens_Handling"/>
		</KlassReferens>
		<Handlingstyp>
			<xsl:value-of select="Handlingstyp"/>
		</Handlingstyp>
		<Beskrivning>
			<xsl:value-of select="Beskrivning"/>
		</Beskrivning>
		<Rubrik>
			<xsl:value-of select="Rubrik"/>
		</Rubrik>
		<Skapad>
			<xsl:value-of select="substring(Skapad_Handling, 1, 19)"/>
		</Skapad>
		<xsl:apply-templates select="key('secondkey', concat(ArkivobjektID_Arende, '|', ArkivobjektID_Handling))"/>
	</xsl:template>
	<xsl:template match="row">
		<Bilaga>
			<xsl:attribute name="Namn">
				<xsl:value-of select="Lank"/>
			</xsl:attribute>
			<xsl:attribute name="Lank">
				<xsl:value-of select="Lank"/>
			</xsl:attribute>
			<Bevaras>true</Bevaras>
		</Bilaga>
	</xsl:template>
</xsl:stylesheet>