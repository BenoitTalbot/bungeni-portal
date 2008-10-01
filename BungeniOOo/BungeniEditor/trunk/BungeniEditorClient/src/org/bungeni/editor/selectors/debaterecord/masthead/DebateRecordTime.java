/*
 * DebateRecordTime.java
 *
 * Created on August 11, 2008, 10:36 PM
 */

package org.bungeni.editor.selectors.debaterecord.masthead;

import com.sun.star.container.XNameAccess;
import com.sun.star.container.XNamed;
import com.sun.star.text.XTextContent;
import com.sun.star.text.XTextCursor;
import java.awt.Component;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.HashMap;
import javax.swing.JSpinner;
import javax.swing.SpinnerDateModel;
import org.bungeni.editor.BungeniEditorProperties;
import org.bungeni.editor.selectors.BaseMetadataPanel;
import org.bungeni.ooo.OOComponentHelper;
import org.bungeni.ooo.ooDocMetadata;
import org.bungeni.ooo.ooQueryInterface;

/**
 *
 * @author  undesa
 */
public class DebateRecordTime extends BaseMetadataPanel {
   private static org.apache.log4j.Logger log = org.apache.log4j.Logger.getLogger(DebateRecordTime.class.getName());

   /**
    * metadata variable declarations
    */
   
    final String _debatetimeRefName_ = "BungeniDebateOfficialTime";

    /** Creates new form DebateRecordTime */
    public DebateRecordTime() {
        super();
        initComponents();
        initCommon();
    }

    /** This method is called from within the constructor to
     * initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is
     * always regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        dt_initdebate_timeofhansard = new javax.swing.JSpinner();
        lbl_initdebate_timeofhansard = new javax.swing.JLabel();

        setName("DebateRecord Time"); // NOI18N

        dt_initdebate_timeofhansard.setName("dt_initdebate_timeofhansard"); // NOI18N

        lbl_initdebate_timeofhansard.setText("Hansard Time");
        lbl_initdebate_timeofhansard.setName("lbl_initdebate_timeofhansard"); // NOI18N

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(dt_initdebate_timeofhansard, javax.swing.GroupLayout.PREFERRED_SIZE, 86, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(lbl_initdebate_timeofhansard, javax.swing.GroupLayout.PREFERRED_SIZE, 160, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addComponent(lbl_initdebate_timeofhansard)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(dt_initdebate_timeofhansard, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
        );
    }// </editor-fold>//GEN-END:initComponents


    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JSpinner dt_initdebate_timeofhansard;
    private javax.swing.JLabel lbl_initdebate_timeofhansard;
    // End of variables declaration//GEN-END:variables

    @Override
    public String getPanelName() {
        return getName();
    }

    @Override
    public Component getPanelComponent() {
        return this;
    }

    @Override
    public boolean preFullEdit() {
return true;
    }

    @Override
    public boolean processFullEdit() {
return true;
    }

    @Override
    public boolean postFullEdit() {
return true;
    }

    @Override
    public boolean preFullInsert() {
return true;
    }

    @Override
    public boolean processFullInsert() {
return true;
    }

    @Override
    public boolean postFullInsert() {
return true;
    }

    @Override
    public boolean preSelectEdit() {
return true;
    }

    @Override
    public boolean processSelectEdit() {
return true;
    }

    @Override
    public boolean postSelectEdit() {
return true;
    }

    @Override
    public boolean preSelectInsert() {
return true;
    }

    private void insertRefMark (OOComponentHelper ooHandle, XTextCursor thisCursor, String referenceName ) {
       Object referenceMark = ooHandle.createInstance("com.sun.star.text.ReferenceMark");
       XNamed xRefMark = ooQueryInterface.XNamed(referenceMark);
       xRefMark.setName(referenceName);
       XTextContent xContent = ooQueryInterface.XTextContent(xRefMark);
       try {
       thisCursor.getText().insertTextContent(thisCursor, xContent, true);
       } catch (Exception ex) {
           log.error("insertReferenceMark :" + ex.getMessage()); 
       }
   }

    @Override
    public boolean processSelectInsert() {
           //1 check if reference exists .. if yes then fail... 
        //if no markhighlighted text with named reference
       //also store selected date to metadata 
        //1 - add reference mark
       OOComponentHelper ooDoc = getContainerPanel().getOoDocument();
       insertRefMark(ooDoc, ooDoc.getViewCursor(), this._debatetimeRefName_);
       //2 - add metadata
       SimpleDateFormat formatter = new SimpleDateFormat (BungeniEditorProperties.getEditorProperty("metadataTimeFormat"));
       Object timeValue = this.dt_initdebate_timeofhansard.getValue();
       Date hansardTime = (Date) timeValue;
       final String strTimeOfHansard = formatter.format(hansardTime);
       com.sun.star.text.XTextSection currentSection = ooDoc.currentSection();
       HashMap<String,String> sectionMeta = new HashMap<String,String>() {{
               put (_debatetimeRefName_, strTimeOfHansard);
           }};
       ooDoc.setSectionMetadataAttributes(currentSection, sectionMeta);     
       return true;       
    }

    @Override
    public boolean postSelectInsert() {
return true;
    }

    @Override
    public boolean validateSelectedEdit() {
return true;
    }
    
 
     
    @Override
    public boolean validateSelectedInsert() {
        OOComponentHelper ooDoc = getContainerPanel().getOoDocument();
        XNameAccess refs = ooDoc.getReferenceMarks();
        if (refs.hasByName(_debatetimeRefName_)){
            this.addErrorMessage(null, "This item has already been marked up. Please use the 'Edit Metadata' option to modify it");
            return false;
        }
        
        return true;
    }

    @Override
    public boolean validateFullInsert() {
        return true;
    }

    @Override
    public boolean validateFullEdit() {
        return true;
    }

    @Override
    public boolean doCancel() {
        return true;
    }

    @Override
    public boolean doReset() {
        return true;
    }
    @Override
    protected void initFieldsSelectedEdit() {
        return;
    }

    @Override
    protected void initFieldsSelectedInsert() {
        return;
    }

    @Override
    protected void initFieldsInsert() {
        return;
    }

    @Override
    protected void initFieldsEdit() {
        dt_initdebate_timeofhansard.setModel(new SpinnerDateModel(new Date(), null, null, Calendar.HOUR));
        dt_initdebate_timeofhansard.setEditor(new JSpinner.DateEditor(dt_initdebate_timeofhansard, "HH:mm"));
       ((JSpinner.DefaultEditor)dt_initdebate_timeofhansard.getEditor()).getTextField().setEditable(false);
        
        if (getOoDocument().propertyExists("Bungeni_DebateOfficialTime")) {
                    try {
                        ooDocMetadata meta = new ooDocMetadata(getOoDocument());
                        String strTime = meta.GetProperty("Bungeni_DebateOfficialTime");
                         SimpleDateFormat timeFormat = new SimpleDateFormat("HH:mm");
                        dt_initdebate_timeofhansard.setValue(timeFormat.parse(strTime));
                    } catch (ParseException ex) {
                        log.error("initFieldsEdit : " + ex.getMessage());
                    }
                }
        return;
    }
    
    private void initCommon(){
        dt_initdebate_timeofhansard.setModel(new SpinnerDateModel(new Date(), null, null, Calendar.HOUR));
        dt_initdebate_timeofhansard.setEditor(new JSpinner.DateEditor(dt_initdebate_timeofhansard, BungeniEditorProperties.getEditorProperty("metadataTimeFormat")));
        ((JSpinner.DefaultEditor)dt_initdebate_timeofhansard.getEditor()).getTextField().setEditable(false);
 
    }
}
