/*
 * BungeniToolbarCondition.java
 *
 * Created on January 26, 2008, 10:34 PM
 *
 * To change this template, choose Tools | Template Manager
 * and open the template in the editor.
 */

package org.bungeni.editor.toolbar.conditions;

import org.bungeni.db.BungeniClientDB;
import org.bungeni.db.DefaultInstanceFactory;
import org.bungeni.db.QueryResults;
import org.bungeni.db.SettingsQueryFactory;
import org.bungeni.editor.BungeniEditorProperties;

/**
 *
 * @author Administrator
 */
public class BungeniToolbarCondition {
    private String conditionName;
    private String conditionValue;
    private String conditionClass;
    
    /** Creates a new instance of BungeniToolbarCondition */
    public BungeniToolbarCondition(String fullCondition) {
        if (fullCondition.indexOf(":") != -1){
            String[] full = fullCondition.trim().split("[:]");
            conditionName = full[0].trim();
            conditionValue = full[1].trim();
            setConditionClass(getConditionClassFromName(conditionName));
        }
    }
     
   private String getConditionClassFromName(String conditionName) {
        BungeniClientDB db =  new BungeniClientDB(DefaultInstanceFactory.DEFAULT_INSTANCE(), DefaultInstanceFactory.DEFAULT_DB());
        db.Connect();
        QueryResults qr = db.QueryResults(SettingsQueryFactory.Q_FETCH_CONDITION_CLASS_BY_NAME(conditionName, BungeniEditorProperties.getEditorProperty("activeDocumentMode")));
        db.EndConnect();
        String[] conditionClass = null;
        if (qr.hasResults()) {
            conditionClass = qr.getSingleColumnResult("CONDITION_CLASS");
            return conditionClass[0];
        } else {
            return null;
        }
   } 
    public BungeniToolbarCondition(String name, String value ) {
        this.setConditionName(name);
        this.setConditionValue(value);
    }

    public String getConditionName() {
        return conditionName;
    }

    public void setConditionName(String conditionName) {
        this.conditionName = conditionName.trim();
    }

    public String getConditionValue() {
        return conditionValue;
    }

    public void setConditionValue(String conditionValue) {
        this.conditionValue = conditionValue.trim();
    }

    public String getConditionClass() {
        return conditionClass;
    }

    public void setConditionClass(String conditionClass) {
        this.conditionClass = conditionClass.trim();
    }
    
}
