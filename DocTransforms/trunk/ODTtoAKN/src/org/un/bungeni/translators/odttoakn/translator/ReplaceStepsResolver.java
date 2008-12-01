package org.un.bungeni.translators.odttoakn.translator;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashMap;
import java.util.Iterator;

import javax.xml.transform.TransformerException;
import javax.xml.transform.stream.StreamSource;
import javax.xml.xpath.XPathExpressionException;

import org.un.bungeni.translators.odttoakn.configurations.Configuration;
import org.un.bungeni.translators.odttoakn.steps.ReplaceStep;
import org.un.bungeni.translators.utility.streams.StreamSourceUtility;

/**
 * Used to resolve the REPLACE STEPS of a configuration file
 */
public final class ReplaceStepsResolver 
{
	/**
	 * Return the StreamSource obtained after all the result steps of the given 
	 * configuration Document are applied to the given Stream source of the document
	 * @param aDocument a Stream Source of an ODF DOM document
	 * @param aConfiguration the configuration file that contains the MAP STEPS
	 * @return a new StreamSource obtained applying all the steps of the configuration to the 
	 * 			given StreamSource
	 * @throws XPathExpressionException 
	 * @throws TransformerException 
	 * @throws IOException 
	 */
	protected static StreamSource resolve(StreamSource anODFDocument, Configuration aConfiguration) throws XPathExpressionException, TransformerException, IOException
	{
		//get the replacement step from the configuration
		HashMap<Integer,ReplaceStep> replaceSteps = aConfiguration.getReplaceSteps();
		
		//create an iterator on the hash map
		Iterator<ReplaceStep> replaceIterator = replaceSteps.values().iterator();

		//get the Document String
		String iteratedStringDocument = StreamSourceUtility.getInstance().writeToString(anODFDocument);
		
		//while the Iterator has replacement steps apply the replacement
		while(replaceIterator.hasNext())
		{
			//get the next step
			ReplaceStep nextStep = (ReplaceStep)replaceIterator.next();

			//get the pattern of the replace
			String pattern = nextStep.getPattern();
			
			//get the replacement of the step 
			String replacement = nextStep.getReplacement();
			
			//apply the replacement
			iteratedStringDocument = iteratedStringDocument.replaceAll(pattern, replacement);
		}

		//create a file for the result  
		File tempFile = File.createTempFile("temp", ".xml");
		
		//delete the temp file on exit
		tempFile.deleteOnExit();

		//write the result on the temporary file
		BufferedWriter out = new BufferedWriter(new FileWriter(tempFile));
	    out.write(iteratedStringDocument);
	    out.close();
	    
		//create a new StremSource
		StreamSource tempStreamSource = new StreamSource(tempFile);

		//return the string of the new created document
		return tempStreamSource;
	}
}
