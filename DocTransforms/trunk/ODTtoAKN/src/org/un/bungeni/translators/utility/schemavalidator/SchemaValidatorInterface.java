package org.un.bungeni.translators.utility.schemavalidator;


import java.io.IOException;

import javax.xml.transform.stream.StreamSource;

import org.xml.sax.SAXException;

import net.sf.saxon.s9api.SaxonApiException;

/**
 * This is the interface for the Schema Validator object.
 * It is used to perform a validation of a document through a schema
 */
public interface SchemaValidatorInterface 
{
	/**
	 * This method validate a document through a schema
	 * @param aDocumentSource the source of the document to validate
	 * @param aSchemaPath the path of the schema that must be used for the validation 
	 * @throws SaxonApiException 
	 * @throws SAXException 
	 * @throws IOException 
	 */
	public void validate(StreamSource aDocumentSource, String aSchemaPath) throws SaxonApiException, SAXException, IOException;
	
}
