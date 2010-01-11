<?php

if (!defined('MEDIAWIKI')) die();
 
global $IP;
require_once( "$IP/includes/SpecialPage.php" );

function doSpecialOrderStaff() {
	$MV_SpecialOrderStaff = new MV_SpecialOrderStaff();
	$MV_SpecialOrderStaff->execute();
}

SpecialPage::addPage( new SpecialPage('Mv_order_staff','',true,'doSpecialOrderStaff',false) );

class MV_SpecialOrderStaff
{
	function execute()
	{
		global $wgOut,$wgJsMimeType,$mvgScriptPath, $reporterOrderTable, $readerOrderTable, $editorOrderTable;
		//$wgOut->addScript("<script type=\"{$wgJsMimeType}\" src=\"{$mvgScriptPath}/skins/orderStaff.js\"></script>");
		$wgOut->addScript("<script type=\"{$wgJsMimeType}\" src=\"{$mvgScriptPath}/skins/mv_stream.js\"></script>");
		$wgOut->addStyle("<script type=\"{$wgJsMimeType}\" src=\"{$mvgScriptPath}/skins/drag.css\"></script>");
		$html .= "<div id=\"success\"></div>";
		/*
		$html.='<form name=staff >';
		$html.='<table>';
		$dbr =& wfGetDB(DB_SLAVE);
		
		//$sql = 'SELECT ug_user FROM user_groups WHERE ug_group="editor"';
		$sql = 'SELECT ug_user FROM user_groups LEFT OUTER JOIN '.$editorOrderTable.' ON user_groups.ug_user = '.$editorOrderTable.'.id  WHERE user_groups.ug_group="editor" ORDER BY '.$editorOrderTable.'.rank';
		$result = $dbr->query($sql);
		$html .= '<tr><td><table>';
		$html.='<tr><td colspan=2>Editors</td></tr>';
		$html.='<tr><td rowspan=2><select name=editor size=10 id=editor>';
		while  ($rowEditors = $dbr->fetchobject($result))
		{
			$id = $rowEditors->ug_user;
			$user = User::newFromId($rowEditors->ug_user);
			$name = $user->getRealName();
			$html.='<option value='.$id.'>'.$name.'</option>';
		}
		
		$html.='</select></td><td>';  
		$html.="<img src=\"{$mvgScriptPath}/skins/images/arrows/sortup.png\" onclick=up(\"editor\")>";
		$html.="</td></tr><tr><td> <img src=\"{$mvgScriptPath}/skins/images/arrows/sortdown.png\" onclick=down(\"editor\")></td></tr>";
		$html.='</table></td>';
		
		//$sql = 'SELECT ug_user FROM user_groups WHERE ug_group="reader"';
		$sql = 'SELECT ug_user FROM user_groups LEFT OUTER JOIN '.$readerOrderTable.' ON user_groups.ug_user = '.$readerOrderTable.'.id  WHERE user_groups.ug_group="reader" ORDER BY '.$readerOrderTable.'.rank';
		
		$result = $dbr->query($sql);
		$html .= '<td><table>';
		$html.='<tr><td colspan=2>Readers</td></tr>';
		
		
		$html.='<tr><td rowspan=2><select name=reader size=10 id=reader>';
		while  ($rowReaders = $dbr->fetchobject($result))
		{
			$id = $rowReaders->ug_user;
			$user = User::newFromId($rowReaders->ug_user);
			$name = $user->getRealName();
			$html.='<option value='.$id.'>'.$name.'</option>';
		}
		
		$html.='</select></td><td>';  
		$html.="<img src=\"{$mvgScriptPath}/skins/images/arrows/sortup.png\" onclick=up(\"reader\")>";
		$html.="</td></tr><tr><td> <img src=\"{$mvgScriptPath}/skins/images/arrows/sortdown.png\" onclick=down(\"reader\")></td></tr>";
		//$sql = 'SELECT ug_user FROM user_groups WHERE ug_group="reporter"';
		$sql = 'SELECT ug_user FROM user_groups LEFT OUTER JOIN '.$reporterOrderTable.' ON user_groups.ug_user = '.$reporterOrderTable.'.id  WHERE user_groups.ug_group="reporter" ORDER BY '.$reporterOrderTable.'.rank';
		
		$result = $dbr->query($sql);
		$html.='</table></td>';
		$html .= '<td><table>';
		$html.='<tr><td colspan=2>Reporters</td></tr>';
		$html.='<tr><td rowspan=2><select name=reporter size=10 id=reporter>';
		while  ($rowReporters = $dbr->fetchobject($result))
		{
			$id = $rowReporters->ug_user;
			$user = User::newFromId($rowReporters->ug_user);
			$name = $user->getRealName();
			$html.='<option value='.$id.'>'.$name.'</option>';
		}
		
		$html.='</select></td><td>';  
		$html.="<img src=\"{$mvgScriptPath}/skins/images/arrows/sortup.png\" onclick=up(\"reporter\")>";
		$html.="</td></tr><tr><td> <img src=\"{$mvgScriptPath}/skins/images/arrows/sortdown.png\" onclick=down(\"reporter\")></td></tr>";
		
		$html.='</table></td>';
		$html .= '</td></table>';
		$html.='<input type="hidden" name="xmldata"></input>';
		$html.='</form>';
		$html.='<a onclick=save()>save</a>';
		*/
		$sql = 'SELECT ug_user FROM user_groups LEFT OUTER JOIN '.$editorOrderTable.' ON user_groups.ug_user = '.$editorOrderTable.'.id  WHERE user_groups.ug_group="editor" ORDER BY '.$editorOrderTable.'.rank';
		$result = $dbr->query($sql);
		$html .= "<div class="workarea"><h3>List 1</h3><ul id="ul1" class="draglist">";
		while  ($rowEditors = $dbr->fetchobject($result))
		{
			$id = $rowEditors->ug_user;
			$user = User::newFromId($rowEditors->ug_user);
			$name = $user->getRealName();
			$html.='<li class="list1" id='.$id.'>'.$name.'</li>';
		}
		$html .= '</ul></div>';
		
    <li class="list1" id="li1_1">list 1, item 1</li>
    <li class="list1" id="li1_2">list 1, item 2</li>
    <li class="list1" id="li1_3">list 1, item 3</li>
  

<div class="workarea">
  <h3>List 2</h3>
  <ul id="ul2" class="draglist">
    <li class="list2" id="li2_1">list 2, item 1</li>
    <li class="list2" id="li2_2">list 2, item 2</li>
    <li class="list2" id="li2_3">list 2, item 3</li>
  </ul>
</div>
<div id="user_actions">
  <input type="button" id="showButton" value="Show Current Order" />
  <input type="button" id="switchButton" value="Remove List Background" />
</div>";
		$html .= '<div id=debug></div>';
		$html .= <<< SCRIPT
<script type="text/javascript">

(function() {

var Dom = YAHOO.util.Dom;
var Event = YAHOO.util.Event;
var DDM = YAHOO.util.DragDropMgr;

//////////////////////////////////////////////////////////////////////////////
// example app
//////////////////////////////////////////////////////////////////////////////
YAHOO.example.DDApp = {
    init: function() {

        var rows=3,cols=2,i,j;
        for (i=1;i<cols+1;i=i+1) {
            new YAHOO.util.DDTarget("ul"+i);
        }

        for (i=1;i<cols+1;i=i+1) {
            for (j=1;j<rows+1;j=j+1) {
                new YAHOO.example.DDList("li" + i + "_" + j);
            }
        }

        Event.on("showButton", "click", this.showOrder);
        Event.on("switchButton", "click", this.switchStyles);
    },

    showOrder: function() {
        var parseList = function(ul, title) {
            var items = ul.getElementsByTagName("li");
            var out = title + ": ";
            for (i=0;i<items.length;i=i+1) {
                out += items[i].id + " ";
            }
            return out;
        };

        var ul1=Dom.get("ul1"), ul2=Dom.get("ul2");
        alert(parseList(ul1, "List 1") + "\n" + parseList(ul2, "List 2"));

    },

    switchStyles: function() {
        Dom.get("ul1").className = "draglist_alt";
        Dom.get("ul2").className = "draglist_alt";
    }
};

//////////////////////////////////////////////////////////////////////////////
// custom drag and drop implementation
//////////////////////////////////////////////////////////////////////////////

YAHOO.example.DDList = function(id, sGroup, config) {

    YAHOO.example.DDList.superclass.constructor.call(this, id, sGroup, config);

    this.logger = this.logger || YAHOO;
    var el = this.getDragEl();
    Dom.setStyle(el, "opacity", 0.67); // The proxy is slightly transparent

    this.goingUp = false;
    this.lastY = 0;
};

YAHOO.extend(YAHOO.example.DDList, YAHOO.util.DDProxy, {

    startDrag: function(x, y) {
        this.logger.log(this.id + " startDrag");

        // make the proxy look like the source element
        var dragEl = this.getDragEl();
        var clickEl = this.getEl();
        Dom.setStyle(clickEl, "visibility", "hidden");

        dragEl.innerHTML = clickEl.innerHTML;

        Dom.setStyle(dragEl, "color", Dom.getStyle(clickEl, "color"));
        Dom.setStyle(dragEl, "backgroundColor", Dom.getStyle(clickEl, "backgroundColor"));
        Dom.setStyle(dragEl, "border", "2px solid gray");
    },

    endDrag: function(e) {

        var srcEl = this.getEl();
        var proxy = this.getDragEl();

        // Show the proxy element and animate it to the src element's location
        Dom.setStyle(proxy, "visibility", "");
        var a = new YAHOO.util.Motion( 
            proxy, { 
                points: { 
                    to: Dom.getXY(srcEl)
                }
            }, 
            0.2, 
            YAHOO.util.Easing.easeOut 
        )
        var proxyid = proxy.id;
        var thisid = this.id;

        // Hide the proxy and show the source element when finished with the animation
        a.onComplete.subscribe(function() {
                Dom.setStyle(proxyid, "visibility", "hidden");
                Dom.setStyle(thisid, "visibility", "");
            });
        a.animate();
    },

    onDragDrop: function(e, id) {

        // If there is one drop interaction, the li was dropped either on the list,
        // or it was dropped on the current location of the source element.
        if (DDM.interactionInfo.drop.length === 1) {

            // The position of the cursor at the time of the drop (YAHOO.util.Point)
            var pt = DDM.interactionInfo.point; 

            // The region occupied by the source element at the time of the drop
            var region = DDM.interactionInfo.sourceRegion; 

            // Check to see if we are over the source element's location.  We will
            // append to the bottom of the list once we are sure it was a drop in
            // the negative space (the area of the list without any list items)
            if (!region.intersect(pt)) {
                var destEl = Dom.get(id);
                var destDD = DDM.getDDById(id);
                destEl.appendChild(this.getEl());
                destDD.isEmpty = false;
                DDM.refreshCache();
            }

        }
    },

    onDrag: function(e) {

        // Keep track of the direction of the drag for use during onDragOver
        var y = Event.getPageY(e);

        if (y < this.lastY) {
            this.goingUp = true;
        } else if (y > this.lastY) {
            this.goingUp = false;
        }

        this.lastY = y;
    },

    onDragOver: function(e, id) {
    
        var srcEl = this.getEl();
        var destEl = Dom.get(id);

        // We are only concerned with list items, we ignore the dragover
        // notifications for the list.
        if (destEl.nodeName.toLowerCase() == "li") {
            var orig_p = srcEl.parentNode;
            var p = destEl.parentNode;

            if (this.goingUp) {
                p.insertBefore(srcEl, destEl); // insert above
            } else {
                p.insertBefore(srcEl, destEl.nextSibling); // insert below
            }

            DDM.refreshCache();
        }
    }
});

Event.onDOMReady(YAHOO.example.DDApp.init, YAHOO.example.DDApp, true);

})();
</script>		
		
SCRIPT
		
		
		
		$wgOut->addHTML($html);
	}
}
?>
