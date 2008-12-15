package org.un.bungeni.translators.localization;

import java.util.ListResourceBundle;

/**
 * This class is used to set all the messages in English for Kenya
 */
public class Messages_en_KE extends ListResourceBundle {

	//The List that contains the messages for kenya
	static Object[][] contents = 
	{
	    { "MISSING_ATTRIBUTE_LEFT_TEXT",
	      "The additional info '" },
	    { "MISSING_ATTRIBUTE_CENTER_TEXT",
	      "' is mandatory for the section '" },
		{ "MISSING_ATTRIBUTE_RIGHT_TEXT",
		  "'" },
	};
	
	
	/**
	 * Return the list of the messages
	 * @Override
	 */
	protected Object[][] getContents() 
	{
		//return the list of the messages
		return contents;
	}

}
