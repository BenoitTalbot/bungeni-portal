package org.un.bungeni.translators.odttoakn.configurations;
import java.util.HashMap;

import javax.xml.xpath.XPathExpressionException;
import org.un.bungeni.translators.odttoakn.steps.XSLTStep;
import org.un.bungeni.translators.odttoakn.steps.ReplaceStep;

/**
 * This is the interface for the configuration object of the ODTtoAKN translator. A configuration
 * stores all the steps needed to perform a specific translation.
 */
public interface ConfigurationInterface 
{	
	/**
	 * Used to get an HashMap containing all the INPUT XSLT Steps of the configuration with their position 
	 * as key. The input step are applied to the document before the resolution of its names according to the map 
	 * @return the HashMap containing all the Steps of the configuration
	 * @throws XPathExpressionException 
	 */
	public HashMap<Integer,XSLTStep> getInputSteps() throws XPathExpressionException;

	/**
	 * Used to get an HashMap containing all the OUTPUT XSLT Steps of the configuration with their position 
	 * as key. The output step are applied to the document after the resolution of its names according to the map 
	 * @return the HashMap containing all the Steps of the configuration
	 * @throws XPathExpressionException 
	 */
	public HashMap<Integer, XSLTStep> getOutputSteps() throws XPathExpressionException; 

	/**
	 * Used to get an HashMap containing all the Replace Steps of the configuration with their position 
	 * as key 
	 * @return the HashMap containing all the Replace Steps of the configuration
	 * @throws XPathExpressionException 
	 */
	public HashMap<Integer,ReplaceStep> getReplaceSteps() throws XPathExpressionException;
}
