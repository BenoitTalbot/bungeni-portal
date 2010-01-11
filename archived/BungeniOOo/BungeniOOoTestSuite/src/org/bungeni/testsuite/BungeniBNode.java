/*
 * BungeniBNode.java
 *
 * Created on October 21, 2007, 5:12 PM
 *
 * To change this template, choose Tools | Template Manager
 * and open the template in the editor.
 */

package org.bungeni.testsuite;

import java.util.HashMap;
import java.util.TreeMap;

/**
 *
 * @author Administrator
 */
    
      class BungeniBNode {
            private String Name;
            private TreeMap<Integer, BungeniBNode> childNodes = new TreeMap<Integer,BungeniBNode>();
            private HashMap<String, BungeniBNode> childNodeNames = new HashMap<String,BungeniBNode>();
            
            public BungeniBNode(String n) {
                Name = n;
            }
            
            public String getName() {
                return Name;
            }
            
            public String toString(){
                return getName();
            }
            public HashMap<String,BungeniBNode> getChildrenByName() {
                return childNodeNames;
            }
            
            public TreeMap<Integer,BungeniBNode> getChildrenByOrder(){
                return childNodes;
            }
            
            public void addChild(BungeniBNode node) {
                childNodes.put(childNodes.size()+1, node);
                childNodeNames.put(node.getName(), node);
            }
            
            public int getChildCount(){
                return childNodes.size();
            }
            
            public boolean containsNodeByName(String name) {
                return childNodeNames.containsKey(name);
            }
            
        }
      
