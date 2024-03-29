/*
 * BungeniToolbarConditionOperatorFactory.java
 *
 * Created on January 29, 2008, 11:41 AM
 *
 * To change this template, choose Tools | Template Manager
 * and open the template in the editor.
 */

package org.bungeni.editor.toolbar.conditions;

import java.util.HashMap;
import java.util.Vector;
import org.bungeni.db.BungeniClientDB;
import org.bungeni.db.DefaultInstanceFactory;
import org.bungeni.db.QueryResults;
import org.bungeni.db.SettingsQueryFactory;

/**
 *
 * @author Administrator
 */
public class BungeniToolbarConditionOperatorFactory {
    
    /** Creates a new instance of BungeniToolbarConditionOperatorFactory */
    public BungeniToolbarConditionOperatorFactory() {
    }
    
    public static HashMap<String, BungeniToolbarConditionOperator> getObjects(){
        HashMap<String,BungeniToolbarConditionOperator> toolMap = new HashMap<String,BungeniToolbarConditionOperator>();
        BungeniClientDB db =  new BungeniClientDB(DefaultInstanceFactory.DEFAULT_INSTANCE(), DefaultInstanceFactory.DEFAULT_DB());
        db.Connect();
        QueryResults qr = db.QueryResults(SettingsQueryFactory.Q_FETCH_CONDITIONAL_OPERATORS());
        if (qr.hasResults()) {
           Vector<Vector<String>> resultRows  = new Vector<Vector<String>>();
           resultRows = qr.theResults();
           for (Vector<String> resultRow: resultRows) {
               String conditionName = resultRow.elementAt(qr.getColumnIndex("CONDITION_NAME")-1);
               String conditionSyntax = resultRow.elementAt(qr.getColumnIndex("CONDITION_SYNTAX")-1);
               String conditionClass = resultRow.elementAt(qr.getColumnIndex("CONDITION_CLASS")-1);
               toolMap.put(conditionName, new BungeniToolbarConditionOperator(conditionName, conditionSyntax, conditionClass ));
           } 
        }
        db.EndConnect();
        return toolMap;
    }       
   
}
