<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:akn="http://www.akomantoso.org/1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0">
    <xsl:output indent="yes" method="xhtml" encoding="UTF-8"/>

    <xsl:template match="/">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="akn:*">
        <xsl:element name="{node-name(.)}">
            <xsl:for-each select="@*">
                <xsl:attribute name="{name(.)}">
                    <xsl:value-of select="."/>
                </xsl:attribute>
            </xsl:for-each>
            <xsl:apply-templates />
        </xsl:element>
    </xsl:template>

    <xsl:template match="akn:marker">
        <span>
            <xsl:attribute name="class">generic_marker marker</xsl:attribute>
			<xsl:if test="@name">
				<xsl:attribute name="name"><xsl:value-of select="@name" /></xsl:attribute>
			</xsl:if>

            <xsl:apply-templates />
        </span>
    </xsl:template>
    
    <xsl:template match="text()">
        <xsl:value-of select="normalize-space(.)"/>
    </xsl:template> 

</xsl:stylesheet>
