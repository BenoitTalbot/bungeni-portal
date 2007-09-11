package org.bungeni.testsuite;

import com.sun.star.beans.XPropertySet;
import com.sun.star.container.XIndexAccess;
import com.sun.star.document.XEventListener;
import com.sun.star.frame.XController;
import com.sun.star.lang.EventObject;
import com.sun.star.lang.WrappedTargetException;
import com.sun.star.lang.XComponent;
import com.sun.star.lang.XServiceInfo;
import com.sun.star.text.XTextCursor;
import com.sun.star.text.XTextRange;
import com.sun.star.text.XTextSection;
import com.sun.star.text.XTextViewCursor;
import com.sun.star.uno.Any;
import com.sun.star.uno.UnoRuntime;
import com.sun.star.uno.XComponentContext;
import com.sun.star.view.XSelectionChangeListener;
import com.sun.star.view.XSelectionSupplier;
import org.bungeni.ooo.BungenioOoHelper;
import org.bungeni.ooo.OOComponentHelper;
import org.bungeni.ooo.ooQueryInterface;
/*
 * testBungeniLibs.java
 *
 * Created on September 1, 2007, 9:44 PM
 */

/**
 *
 * @author  Administrator
 */
public class testBungeniLibs extends javax.swing.JPanel implements com.sun.star.lang.XEventListener {
    
    private XComponentContext theComponentContext;
    private XComponent  theComponent = null;
    private OOComponentHelper ooDocument;

    private String templatePath;
    SelectionChangeListener selList;
    /** Creates new form testBungeniLibs */
    
    
    public testBungeniLibs() {
        initComponents();
        
       
    }
    
    public testBungeniLibs(XComponentContext context) {
        initComponents();
        theComponentContext  = context;
        selList = new SelectionChangeListener(); 
    }
    
    /** This method is called from within the constructor to
     * initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is
     * always regenerated by the Form Editor.
     */
    // <editor-fold defaultstate="collapsed" desc=" Generated Code ">//GEN-BEGIN:initComponents
    private void initComponents() {
        btnLaunch = new javax.swing.JButton();
        jScrollPane1 = new javax.swing.JScrollPane();
        txtMessage = new javax.swing.JTextArea();
        btnClear = new javax.swing.JButton();
        txtTemplatePath = new java.awt.TextField();
        jLabel1 = new javax.swing.JLabel();
        btnSelectiListener = new javax.swing.JButton();
        btnRemoveSelListener = new javax.swing.JButton();
        execBasicMacro = new javax.swing.JButton();
        btnMacroReturnValue = new javax.swing.JButton();
        jButton1 = new javax.swing.JButton();
        jTextField1 = new javax.swing.JTextField();

        btnLaunch.setText("Launch OO and Connect");
        btnLaunch.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnLaunchActionPerformed(evt);
            }
        });

        txtMessage.setColumns(20);
        txtMessage.setLineWrap(true);
        txtMessage.setRows(5);
        jScrollPane1.setViewportView(txtMessage);

        btnClear.setText("Clear");

        jLabel1.setText("Enter PATH to template or leave blank to launch a blank doc.");

        btnSelectiListener.setText("Attach Selection Listener....");
        btnSelectiListener.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnSelectiListenerActionPerformed(evt);
            }
        });

        btnRemoveSelListener.setText("Detach Selection list...");
        btnRemoveSelListener.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnRemoveSelListenerActionPerformed(evt);
            }
        });

        execBasicMacro.setText("Exec. Search Replace Macro");
        execBasicMacro.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                execBasicMacroActionPerformed(evt);
            }
        });

        btnMacroReturnValue.setText("Get Macro Return value");
        btnMacroReturnValue.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnMacroReturnValueActionPerformed(evt);
            }
        });

        jButton1.setText("import doc above+replace text+apply attributes");
        jButton1.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButton1ActionPerformed(evt);
            }
        });

        jTextField1.setText("jTextField1");

        org.jdesktop.layout.GroupLayout layout = new org.jdesktop.layout.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(layout.createSequentialGroup()
                .add(layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
                    .add(layout.createSequentialGroup()
                        .addContainerGap()
                        .add(jLabel1, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 400, Short.MAX_VALUE))
                    .add(layout.createSequentialGroup()
                        .addContainerGap()
                        .add(jScrollPane1, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 400, Short.MAX_VALUE))
                    .add(layout.createSequentialGroup()
                        .add(118, 118, 118)
                        .add(btnClear, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, 112, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE))
                    .add(org.jdesktop.layout.GroupLayout.TRAILING, layout.createSequentialGroup()
                        .addContainerGap()
                        .add(btnLaunch, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 400, Short.MAX_VALUE))
                    .add(layout.createSequentialGroup()
                        .addContainerGap()
                        .add(txtTemplatePath, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 400, Short.MAX_VALUE))
                    .add(layout.createSequentialGroup()
                        .addContainerGap()
                        .add(layout.createParallelGroup(org.jdesktop.layout.GroupLayout.TRAILING, false)
                            .add(org.jdesktop.layout.GroupLayout.LEADING, execBasicMacro, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                            .add(org.jdesktop.layout.GroupLayout.LEADING, btnSelectiListener, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, 148, Short.MAX_VALUE))
                        .add(16, 16, 16)
                        .add(layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
                            .add(btnMacroReturnValue, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 213, Short.MAX_VALUE)
                            .add(btnRemoveSelListener, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 213, Short.MAX_VALUE)))
                    .add(layout.createSequentialGroup()
                        .addContainerGap()
                        .add(jButton1, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 400, Short.MAX_VALUE))
                    .add(org.jdesktop.layout.GroupLayout.TRAILING, layout.createSequentialGroup()
                        .addContainerGap()
                        .add(jTextField1, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 400, Short.MAX_VALUE)))
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(org.jdesktop.layout.GroupLayout.TRAILING, layout.createSequentialGroup()
                .add(jLabel1, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, 26, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                .add(1, 1, 1)
                .add(txtTemplatePath, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(btnLaunch)
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(layout.createParallelGroup(org.jdesktop.layout.GroupLayout.BASELINE)
                    .add(btnSelectiListener)
                    .add(btnRemoveSelListener))
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(layout.createParallelGroup(org.jdesktop.layout.GroupLayout.BASELINE)
                    .add(execBasicMacro)
                    .add(btnMacroReturnValue))
                .add(12, 12, 12)
                .add(jTextField1, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(jButton1, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, 33, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED, 41, Short.MAX_VALUE)
                .add(jScrollPane1, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                .add(9, 9, 9)
                .add(btnClear))
        );
    }// </editor-fold>//GEN-END:initComponents

    private void jButton1ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButton1ActionPerformed
// TODO add your handling code here:
            Object[] params = new Object[2];
            params[0] = new String("Section1")   ;
            params[1] =  jTextField1.getText();
            txtMessage.append("running macro : InsertDocIntoSection");
            ooDocument.executeMacro("InsertDocIntoSection", params);
            params[0] = new String("[[QUESTION_TITLE]]");
            params[1] = new String("new string title");
            ooDocument.executeMacro("SearchAndReplace" , params);
    }//GEN-LAST:event_jButton1ActionPerformed

    private void btnMacroReturnValueActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnMacroReturnValueActionPerformed
// TODO add your handling code here:
        Object[] params = {};
        Object value = ooDocument.executeMacro("CursorInSection", params);
        txtMessage.append("Output values from macro was: " + (String)value);
        
    }//GEN-LAST:event_btnMacroReturnValueActionPerformed




    private void execBasicMacroActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_execBasicMacroActionPerformed
// TODO add your handling code here:
        Object[] params = new Object[2];
        params[0] = new String("Search for this");
        params[1] = new String("Replace with that");
        ooDocument.executeMacro("SearchAndReplace", params);
    }//GEN-LAST:event_execBasicMacroActionPerformed

    private void btnRemoveSelListenerActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnRemoveSelListenerActionPerformed
// TODO add your handling code here:
        ooQueryInterface.XSelectionSupplier(ooDocument.getDocumentModel().getCurrentController()).removeSelectionChangeListener(selList);
    }//GEN-LAST:event_btnRemoveSelListenerActionPerformed

    public String getSectionName()
{
    XTextSection loXTextSection;
    XTextViewCursor loXTextCursor;
    XPropertySet loXPropertySet;

    String lstrSectionName = "";

    try
    {
        loXTextCursor = ooDocument.getViewCursor();
        
        
        loXPropertySet = (XPropertySet)UnoRuntime.queryInterface(XPropertySet.class, loXTextCursor);

        loXTextSection = (XTextSection)((Any)loXPropertySet.getPropertyValue("TextSection")).getObject();

        if (loXTextSection != null)
        {
            loXPropertySet = (XPropertySet)UnoRuntime.queryInterface(XPropertySet.class, loXTextSection);

            lstrSectionName = (String)loXPropertySet.getPropertyValue("LinkDisplayName");
        }
    }
    catch (java.lang.Exception poException)
    {
        poException.printStackTrace();
    }

    return lstrSectionName;
} 
    class SelectionChangeListener implements XSelectionChangeListener {
        public SelectionChangeListener() {
            
        }

        public void selectionChanged(EventObject eventObject)  {
            XSelectionSupplier sel = ooQueryInterface.XSelectionSupplier(eventObject.Source);
            Object selection = null;
            if (sel == null ) {
                txtMessage.append("\n NULL SUPPLIER");
                return;
            } else {
                selection = sel.getSelection();
                if (selection == null ) 
                 txtMessage.append("\n NULL SELECTION");
                else {
                       XServiceInfo xSelInfo = ooQueryInterface.XServiceInfo(selection);
                           String strSelection = getSectionName();
                           txtMessage.append("Current Selectio = " + strSelection);
                        if ( xSelInfo.supportsService("com.sun.star.text.TextRanges") ){
                              XIndexAccess xIndexAccess = ooQueryInterface.XIndexAccess(selection);
                              if (xIndexAccess == null ) 
                                  txtMessage.append("\n NULL INDEX ");
                              else {
                            Object singleSel = null;
                            try {
                                singleSel = xIndexAccess.getByIndex(0);
                            } catch (WrappedTargetException ex) {
                                ex.printStackTrace();
                            } catch (com.sun.star.lang.IndexOutOfBoundsException ex) {
                                ex.printStackTrace();
                            }
                                    XTextRange xRange = ooQueryInterface.XTextRange(singleSel);
                                     //get the cursor for the selected range
                                     XTextCursor xRangeCursor = xRange.getText().createTextCursorByRange(xRange);
                                     if (xRangeCursor.isCollapsed())
                                     {
                                         txtMessage.append("\n ZERO LENGTH SELECTION!!!");
                                     } else {
                                         txtMessage.append("\n VALID SELECTION!!!!! ");
                                     }
                              }
                                 
                        } else {
                            txtMessage.append("\n NULL SELECTION");
                        }
         
                }
            }
            
            return;
        }

        public void disposing(EventObject eventObject) {
             System.out.println( "disposing called.  detaching as listener" );

        // stop listening for selection changes
            XSelectionSupplier aCtrl = ooQueryInterface.XSelectionSupplier( eventObject );
             if( aCtrl != null )
                aCtrl.removeSelectionChangeListener( selList );

            // remove as dispose listener
            //theComponent.removeEventListener( this );


            return;
        }
    }
    private void btnSelectiListenerActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnSelectiListenerActionPerformed
// TODO add your handling code here:
       XController xDocController = ooDocument.getDocumentModel().getCurrentController();
       XSelectionSupplier aSelSupp = (XSelectionSupplier) UnoRuntime.queryInterface(XSelectionSupplier.class,xDocController);
       if (aSelSupp != null  ) {
        aSelSupp.addSelectionChangeListener(selList);
        txtMessage.append("\nSuccessfully add text selection listener ");
       } else {
           txtMessage.append("\nFailed adding text selecton listener");
       }
     
       
    }//GEN-LAST:event_btnSelectiListenerActionPerformed

    private void btnLaunchActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnLaunchActionPerformed
// TODO add your handling code here:
        templatePath = txtTemplatePath.getText().trim();
        if (theComponent != null  ) {
            txtMessage.setText("There is already a window Open!!!");
            return;
        }
       BungenioOoHelper openofficeObject = new org.bungeni.ooo.BungenioOoHelper(theComponentContext);
       openofficeObject.initoOo();
       String templateURL = "";
        if (templatePath.length() != 0 )    
         templateURL = openofficeObject.convertPathToURL(templatePath);
        theComponent = openofficeObject.newDocument(templateURL);
        theComponent.addEventListener(this);
        ooDocument = new OOComponentHelper(theComponent, theComponentContext);
    
    }//GEN-LAST:event_btnLaunchActionPerformed

    public void disposing(EventObject eventObject) {
        XSelectionSupplier sel = ooQueryInterface.XSelectionSupplier(ooDocument.getDocumentModel().getCurrentController());
        if (sel != null ) {
            sel.removeSelectionChangeListener(selList);
            
        }
        theComponent.removeEventListener(this);
        
    }

    
    
    
    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JButton btnClear;
    private javax.swing.JButton btnLaunch;
    private javax.swing.JButton btnMacroReturnValue;
    private javax.swing.JButton btnRemoveSelListener;
    private javax.swing.JButton btnSelectiListener;
    private javax.swing.JButton execBasicMacro;
    private javax.swing.JButton jButton1;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JTextField jTextField1;
    private javax.swing.JTextArea txtMessage;
    private java.awt.TextField txtTemplatePath;
    // End of variables declaration//GEN-END:variables
    
}
