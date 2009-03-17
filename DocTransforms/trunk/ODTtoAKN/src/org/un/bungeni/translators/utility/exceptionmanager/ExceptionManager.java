package org.un.bungeni.translators.utility.exceptionmanager;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.InvalidPropertiesFormatException;
import java.util.Properties;
import java.util.ResourceBundle;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.un.bungeni.translators.globalconfigurations.GlobalConfigurations;
import org.xml.sax.ErrorHandler;
import org.xml.sax.SAXParseException;

/**
 * This object parse a SAXEception understand what type of exception is and throws an 
 * user readable error
 */
public class ExceptionManager implements ErrorHandler
{
	/* The instance of this FileUtility object*/
	private static ExceptionManager instance = null;
		
	/* The resource bundle for the messages */
	private ResourceBundle resourceBundle;
	
	/**
	 * Private constructor used to create the ExceptionManager instance
	 * @throws IOException 
	 * @throws InvalidPropertiesFormatException 
	*/
	private ExceptionManager() throws InvalidPropertiesFormatException, IOException 
	{
		//create the Properties object
		Properties properties = new Properties();
	
		//read the properties file
		InputStream propertiesInputStream = new FileInputStream(GlobalConfigurations.getApplicationPathPrefix() + GlobalConfigurations.getConfigurationFilePath());
			
		//load the properties
		properties.loadFromXML(propertiesInputStream);
		
		//create the resource bundle
		this.resourceBundle = ResourceBundle.getBundle(properties.getProperty("resourceBundlePath"));		
	}
		
	/**
	 * Get the current instance of the ExceptionManager class 
	 * @return the ExceptionManager instance
	*/
	public static ExceptionManager getInstance()
	{
		//if the instance is null create a new instance
		if (instance == null)
		{
			//create the instance
			try 
			{
				instance = new ExceptionManager();
			} 
			catch (Exception e) 
			{
				e.printStackTrace();
			} 
		}
		//otherwise return the instance
		return instance;
	}
	
	
    /**
     * Report a non-fatal error
     * @param ex the error condition
     */
    public void error(SAXParseException ex) 
    {

		//the message of the exception
		String exceptionMessage = ex.getMessage();
		
		//check what type of text the exception launch
		if(exceptionMessage.matches("(.*)Attribute '(.*)' must appear on element '(.*)'.")) 
		{
			//compile the regex
			Pattern p = Pattern.compile("(.*)Attribute '(.*)' must appear on element '(.*)'");
        	//set the input
			Matcher m = p.matcher(exceptionMessage);
        	//the attribute name
			String attribute = ""; 
			//the elemet name
			String element = ""; 
        	while (m.find())
        	{
        	    //get the attribute name
        		attribute = m.group(2).toString();
        		//get element name
        	    element = m.group(3).toString();
        	}
        	//create the text of the exception
    		String message = resourceBundle.getString("MISSING_ATTRIBUTE_LEFT_TEXT") +
	  		                 attribute +
	  		                 resourceBundle.getString("MISSING_ATTRIBUTE_CENTER_TEXT") +
	  		                 element +
	  		                 resourceBundle.getString("MISSING_ATTRIBUTE_RIGHT_TEXT");
        	
            System.err.println("At line " + ex.getLineNumber()  + " of " + ex.getSystemId() + ':');
            System.err.println(message);
           // System.exit(0);
		}
    }

    /**
     * Report a fatal error
     * @param ex the error condition
     */

    public void fatalError(SAXParseException ex) 
    {
		//the message of the exception
		String exceptionMessage = ex.getMessage();
		
		//check what type of text the exception launch
		if(exceptionMessage.matches("(.*)Attribute '(.*)' must appear on element '(.*)'.")) 
		{
			//compile the regex
			Pattern p = Pattern.compile("(.*)Attribute '(.*)' must appear on element '(.*)'");
        	//set the input
			Matcher m = p.matcher(exceptionMessage);
        	//the attribute name
			String attribute = ""; 
			//the elemet name
			String element = ""; 
        	while (m.find())
        	{
        	    //get the attribute name
        		attribute = m.group(2).toString();
        		//get element name
        	    element = m.group(3).toString();
        	}
        	//create the text of the exception
    		String message = resourceBundle.getString("MISSING_ATTRIBUTE_LEFT_TEXT") +
	  		                 attribute +
	  		                 resourceBundle.getString("MISSING_ATTRIBUTE_CENTER_TEXT") +
	  		                 element +
	  		                 resourceBundle.getString("MISSING_ATTRIBUTE_RIGHT_TEXT");
        	
            System.err.println("At line " + ex.getLineNumber()  + " of " + ex.getSystemId() + ':');
            System.err.println(message);
            //System.exit(0);
    	}
    }

    /**
     * Report a warning
     * @param ex the warning condition
     */
    public void warning(org.xml.sax.SAXParseException ex) 
    {
		//the message of the exception
		String exceptionMessage = ex.getMessage();
		
		//check what type of text the exception launch
		if(exceptionMessage.matches("(.*)Attribute '(.*)' must appear on element '(.*)'.")) 
		{
			//compile the regex
			Pattern p = Pattern.compile("(.*)Attribute '(.*)' must appear on element '(.*)'");
        	//set the input
			Matcher m = p.matcher(exceptionMessage);
        	//the attribute name
			String attribute = ""; 
			//the elemet name
			String element = ""; 
        	while (m.find())
        	{
        	    //get the attribute name
        		attribute = m.group(2).toString();
        		//get element name
        	    element = m.group(3).toString();
        	}
        	//create the text of the exception
    		String message = resourceBundle.getString("MISSING_ATTRIBUTE_LEFT_TEXT") +
	  		                 attribute +
	  		                 resourceBundle.getString("MISSING_ATTRIBUTE_CENTER_TEXT") +
	  		                 element +
	  		                 resourceBundle.getString("MISSING_ATTRIBUTE_RIGHT_TEXT");
        	
            System.err.println("At line " + ex.getLineNumber()  + " of " + ex.getSystemId() + ':');
            System.err.println(message);
            //System.exit(0);
           
    	}
    }
    
    
}
