/*
 * sectionExists.java
 *
 * Created on January 26, 2008, 10:25 PM
 *
 * To change this template, choose Tools | Template Manager
 * and open the template in the editor.
 */

package org.bungeni.editor.toolbar.conditions.runnable;

import org.bungeni.editor.BungeniEditorProperties;
import org.bungeni.editor.toolbar.conditions.BungeniToolbarCondition;
import org.bungeni.editor.toolbar.conditions.IBungeniToolbarCondition;
import org.bungeni.ooo.OOComponentHelper;

/**
 * 
 * Contextual evaluator that checks if text has been selected in the document.
 * (i.e. the cursor has highlight some text)
 * e.g. textSelected: false
 * will evaluate to true if no text was selected in the document
 * will evalaute to false if text selected in the document.
 * @author Administrator
 */
public class textSelected implements IBungeniToolbarCondition {
    private static org.apache.log4j.Logger log = org.apache.log4j.Logger.getLogger(textSelected.class.getName());
 
    private OOComponentHelper ooDocument;
    /** Creates a new instance of sectionExists */
    public textSelected() {
    }

    public void setOOoComponentHelper(OOComponentHelper ooDocument) {
        this.ooDocument = ooDocument;
    }

 boolean check_textSelected(BungeniToolbarCondition condition) {
         String conditionValue = condition.getConditionValue();
         boolean bSelected = ooDocument.isTextSelected();
         if (bSelected) {
             if (conditionValue.equals("true"))
                 return true;
             else
                 return false;
         } else  {
             if (conditionValue.equals("false"))
                 return true;
             else
                 return false;
         }
     }
    
    public boolean processCondition(BungeniToolbarCondition condition) {
        return check_textSelected(condition);
    }
        
    /*
       boolean check_sectionExists(String[] arrCondition) {
             boolean bReturn = false;
          try {
             String sectionToActUpon = arrCondition[1];

             if (sectionToActUpon.equals("root")) {
                String activeDoc =  BungeniEditorProperties.getEditorProperty("activeDocumentMode");
                sectionToActUpon = BungeniEditorProperties.getEditorProperty("root:"+activeDoc);
             }

             if (ooDocument.hasSection(sectionToActUpon)) {
                 bReturn =  true;
             } else {
                 bReturn = false;
             }
         } catch (Exception ex) {
             log.error("check_sectionNotExists:"+ex.getMessage());
             log.error("check_sectionNotExists:"+ CommonExceptionUtils.getStackTrace(ex));
             bReturn = false;
         } finally {
             return bReturn;
         }
     }    
       
    if (arrCondition[0].equals("sectionExists")) {
                    log.debug("processActionCondition:sectionExists");
                    bAction  = check_sectionExists(arrCondition);
                    log.debug("processActionCondition:"+bAction);
                }
*/



 }
