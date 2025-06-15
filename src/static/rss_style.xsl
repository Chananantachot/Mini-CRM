<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:rss="http://purl.org/rss/1.0/"
    xmlns:atom="http://www.w3.org/2005/Atom">

    <!-- Match the root element of the RSS feed -->
    <xsl:template match="/rss">
        <html>
            <head>
                <title><xsl:value-of select="channel/title"/></title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 800px;
                        margin: 20px auto;
                        padding: 0 20px;
                        background-color: #f4f4f4;
                    }
                    h1 {
                        color: #0056b3;
                        border-bottom: 2px solid #0056b3;
                        padding-bottom: 10px;
                    }
                    h2 {
                        color: #0056b3;
                        margin-top: 25px;
                    }
                    .feed-description {
                        font-style: italic;
                        color: #666;
                        margin-bottom: 20px;
                    }
                    .item {
                        background-color: #fff;
                        border: 1px solid #ddd;
                        border-radius: 8px;
                        padding: 15px;
                        margin-bottom: 15px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                        transition: transform 0.2s;
                    }
                    .item:hover {
                        transform: translateY(-3px);
                    }
                    .item-title a {
                        color: #007bff;
                        text-decoration: none;
                        font-size: 1.2em;
                        font-weight: bold;
                    }
                    .item-title a:hover {
                        text-decoration: underline;
                    }
                    .item-description {
                        margin-top: 10px;
                        color: #555;
                    }
                    .item-pubdate {
                        font-size: 0.85em;
                        color: #888;
                        margin-top: 10px;
                    }
                    footer {
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #ccc;
                        font-size: 0.9em;
                        color: #777;
                    }
                </style>
            </head>
            <body>
                <h1><xsl:value-of select="channel/title"/></h1>
                <p class="feed-description"><xsl:value-of select="channel/description"/></p>

                <h2>Latest Products</h2>
                <div class="items-list">
                    <xsl:for-each select="channel/item">
                        <div class="item">
                            <h3 class="item-title">
                                <a href="{link}"><xsl:value-of select="title"/></a>
                            </h3>
                            <div class="item-description">
                                <xsl:value-of select="description"/>
                            </div>
                            <div class="item-pubdate">
                                Published: <xsl:value-of select="pubDate"/>
                            </div>
                        </div>
                    </xsl:for-each>
                </div>

                <footer>
                    <p>Powered by Your Mini CRM</p>
                    <p><a href="{channel/link}">View on Mini CRM</a></p>
                </footer>
            </body>
        </html>
    </xsl:template>

</xsl:stylesheet>