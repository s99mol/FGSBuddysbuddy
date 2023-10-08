<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://xml.ra.se/e-arkiv/FGS-ERMS" version="1.0">
	<xsl:strip-space elements="*"/>
	<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes" />
	<!-- keys used to match unique "ArkivobjektID_Arende" and ArkivobjektID_Handling for each ArkivobjektID_Arende and output 'Bilaga' for 1:* ArkivobjektID_Handling. In this example 'thirdkey' is the same as 'secondkey' but can be expanded to use more elements. -->
	<xsl:key name="firstkey" match="row" use="ArkivobjektID_Arende"/>
	<xsl:key name="secondkey" match="row" use="concat(ArkivobjektID_Arende, '|', ArkivobjektID_Handling)"/>
	<xsl:key name="thirdkey" match="row" use="concat(ArkivobjektID_Arende, '|', ArkivobjektID_Handling)"/>
	<xsl:template match="/data">
		<!-- Output the Leveransobjekt -->
		<Leveransobjekt>
			<ArkivobjektListaArenden>
				<xsl:apply-templates select="row[generate-id() = generate-id(key('firstkey', ArkivobjektID_Arende)[1])]" mode="firstkey"/>
			</ArkivobjektListaArenden>
		</Leveransobjekt>
	</xsl:template>
	<!-- Output the <ArkivobjektArende in <ArkivobjektListaArenden> as firstkey -->
	<xsl:template match="row" mode="firstkey">
		<ArkivobjektArende>
			<xsl:attribute name="Systemidentifierare">
				<xsl:value-of select="ArkivobjektID_Arende/@Systemidentifierare"/>
			</xsl:attribute>
			<ArkivobjektID>
				<xsl:value-of select="ArkivobjektID_Arende"/>
			</ArkivobjektID>
			<!-- Output only when tag is not empty -->
			<xsl:choose>
				<xsl:when test="KlassReferens_Arende != ''">
					<KlassReferens>
						<xsl:value-of select="KlassReferens_Arende"/>
					</KlassReferens>
				</xsl:when>
			</xsl:choose>
			<xsl:choose>
				<xsl:when test="ArendeTyp != ''">
					<ArendeTyp>
						<xsl:value-of select="ArendeTyp"/>
					</ArendeTyp>
				</xsl:when>
			</xsl:choose>
			<xsl:choose>
				<xsl:when test="Forvaringsplats != ''">
					<Forvaringsplats>
						<xsl:value-of select="Forvaringsplats"/>
					</Forvaringsplats>
				</xsl:when>
			</xsl:choose>
			<xsl:choose>
				<xsl:when test="Namn != ''">
					<Agent>
						<Roll>Registrator</Roll>
						<Namn>
							<xsl:value-of select="Namn"/>
						</Namn>
					</Agent>
				</xsl:when>
			</xsl:choose>
			<xsl:choose>
				<xsl:when test="Skapad_Arende != ''">
					<Skapad>
						<xsl:value-of select="Skapad_Arende"/>
					</Skapad>
				</xsl:when>
			</xsl:choose>
			<xsl:choose>
				<xsl:when test="Arendemening != ''">
					<Arendemening>
						<xsl:value-of select="Arendemening"/>
					</Arendemening>
				</xsl:when>
			</xsl:choose>
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
	<!-- Output the <ArkivobjektHandling in ArkivobjektListaHandlingar, as secondkey-->
	<xsl:template match="row" mode="secondkey">
		<ArkivobjektHandling>
			<xsl:attribute name="Systemidentifierare">
				<xsl:value-of select="ArkivobjektID_Handling/@Systemidentifierare"/>
			</xsl:attribute>
			<xsl:apply-templates select="key('secondkey', concat(ArkivobjektID_Arende, '|', ArkivobjektID_Handling))[generate-id() = generate-id(key('thirdkey', concat(ArkivobjektID_Arende, '|', ArkivobjektID_Handling))[1])]" mode="thirdkey"/>
		</ArkivobjektHandling>
	</xsl:template>
	<!-- thirdkey used to output elements in <ArkivobjektHandling> -->
	<xsl:template match="row" mode="thirdkey">
		<ArkivobjektID>
			<xsl:value-of select="ArkivobjektID_Arende"/>
			<xsl:text>/</xsl:text>
			<xsl:value-of select="ArkivobjektID_Handling"/>
		</ArkivobjektID>
		<xsl:choose>
			<xsl:when test="KlassReferens_Handling != ''">
				<KlassReferens>
					<xsl:value-of select="KlassReferens_Handling"/>
				</KlassReferens>
			</xsl:when>
		</xsl:choose>
		<xsl:choose>
			<xsl:when test="Handlingstyp != ''">
				<Handlingstyp>
					<xsl:value-of select="Handlingstyp"/>
				</Handlingstyp>
			</xsl:when>
		</xsl:choose>
		<xsl:choose>
			<xsl:when test="Beskrivning != ''">
				<Beskrivning>
					<xsl:value-of select="Beskrivning"/>
				</Beskrivning>
			</xsl:when>
		</xsl:choose>
		<xsl:choose>
			<xsl:when test="Rubrik != ''">
				<Rubrik>
					<xsl:value-of select="Rubrik"/>
				</Rubrik>
			</xsl:when>
		</xsl:choose>
		<xsl:choose>
			<xsl:when test="Skapad_Handling != ''">
				<Skapad>
					<xsl:value-of select="substring(Skapad_Handling, 1, 19)"/>
				</Skapad>
			</xsl:when>
		</xsl:choose>
		<!-- The return of secondkey, to match each Lank as Bilaga (one to many) -->
		<xsl:apply-templates select="key('secondkey', concat(ArkivobjektID_Arende, '|', ArkivobjektID_Handling))"/>
	</xsl:template>
	<xsl:template match="row">
		<xsl:choose>
			<xsl:when test="Lank = ''">
			</xsl:when>
			<xsl:otherwise>
				<Bilaga>
					<xsl:attribute name="Namn">
						<xsl:value-of select="Lank"/>
					</xsl:attribute>
					<xsl:attribute name="Lank">
						<xsl:value-of select="Lank"/>
					</xsl:attribute>
					<Bevaras>true</Bevaras>
				</Bilaga>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
</xsl:stylesheet>
