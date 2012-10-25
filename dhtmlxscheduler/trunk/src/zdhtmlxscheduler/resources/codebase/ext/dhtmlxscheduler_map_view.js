/*
This software is allowed to use under GPL or you need to obtain Commercial or Enterise License
to use it in non-GPL project. Please contact sales@dhtmlx.com for details
*/
scheduler.xy.map_date_width=188;scheduler.xy.map_description_width=400;scheduler.config.map_resolve_event_location=!0;scheduler.config.map_resolve_user_location=!0;scheduler.config.map_initial_position=new google.maps.LatLng(48.724,8.215);scheduler.config.map_error_position=new google.maps.LatLng(15,15);scheduler.config.map_infowindow_max_width=300;scheduler.config.map_type=google.maps.MapTypeId.ROADMAP;scheduler.config.map_zoom_after_resolve=15;scheduler.locale.labels.marker_geo_success="It seems you are here.";
scheduler.locale.labels.marker_geo_fail="Sorry, could not get your current position using geolocation.";scheduler.templates.marker_date=scheduler.date.date_to_str("%Y-%m-%d %H:%i");scheduler.templates.marker_text=function(f,g,e){return"<div><b>"+e.text+"</b><br/><br/>"+(e.event_location||"")+"<br/><br/>"+scheduler.templates.marker_date(f)+" - "+scheduler.templates.marker_date(g)+"</div>"};
scheduler.dblclick_dhx_map_area=function(){!this.config.readonly&&this.config.dblclick_create&&this.addEventNow({start_date:scheduler._date,end_date:scheduler.date.add(scheduler._date,scheduler.config.time_step,"minute")})};scheduler.templates.map_time=function(f,g,e){return e._timed?this.day_date(e.start_date,e.end_date,e)+" "+this.event_date(f):scheduler.templates.day_date(f)+" &ndash; "+scheduler.templates.day_date(g)};scheduler.templates.map_text=function(f,g,e){return e.text};
scheduler.date.map_start=function(f){return f};scheduler.date.add_map=function(f){return new Date(f.valueOf())};scheduler.templates.map_date=function(){return""};scheduler._latLngUpdate=!1;
scheduler.attachEvent("onSchedulerReady",function(){function f(a){if(a){var c=scheduler.locale.labels;scheduler._els.dhx_cal_header[0].innerHTML="<div class='dhx_map_line' style='width: "+(scheduler.xy.map_date_width+scheduler.xy.map_description_width+2)+"px;' ><div class='headline_date' style='width: "+scheduler.xy.map_date_width+"px;'>"+c.date+"</div><div class='headline_description' style='width: "+scheduler.xy.map_description_width+"px;'>"+c.description+"</div></div>";scheduler._table_view=!0;
scheduler.set_sizes()}}function g(){scheduler._selected_event_id=null;scheduler.map._infowindow.close();var a=scheduler.map._markers,c;for(c in a)a.hasOwnProperty(c)&&(a[c].setMap(null),delete scheduler.map._markers[c],scheduler.map._infowindows_content[c]&&delete scheduler.map._infowindows_content[c])}function e(){var a=scheduler.get_visible_events();a.sort(function(a,b){return a.start_date.valueOf()==b.start_date.valueOf()?a.id>b.id?1:-1:a.start_date>b.start_date?1:-1});for(var c="<div class='dhx_map_area'>",
d=0;d<a.length;d++){var b=a[d],h=b.id==scheduler._selected_event_id?"dhx_map_line highlight":"dhx_map_line",e=b.color?"background:"+b.color+";":"",f=b.textColor?"color:"+b.textColor+";":"";c+="<div class='"+h+"' event_id='"+b.id+"' style='"+e+""+f+""+(b._text_style||"")+" width: "+(scheduler.xy.map_date_width+scheduler.xy.map_description_width+2)+"px;'><div style='width: "+scheduler.xy.map_date_width+"px;' >"+scheduler.templates.map_time(b.start_date,b.end_date,b)+"</div>";c+="<div class='dhx_event_icon icon_details'>&nbsp</div>";
c+="<div class='line_description' style='width:"+(scheduler.xy.map_description_width-25)+"px;'>"+scheduler.templates.map_text(b.start_date,b.end_date,b)+"</div></div>"}c+="<div class='dhx_v_border' style='left: "+(scheduler.xy.map_date_width-2)+"px;'></div><div class='dhx_v_border_description'></div></div>";scheduler._els.dhx_cal_data[0].scrollTop=0;scheduler._els.dhx_cal_data[0].innerHTML=c;scheduler._els.dhx_cal_data[0].style.width=scheduler.xy.map_date_width+scheduler.xy.map_description_width+
1+"px";var g=scheduler._els.dhx_cal_data[0].firstChild.childNodes;scheduler._els.dhx_cal_date[0].innerHTML=scheduler.templates[scheduler._mode+"_date"](scheduler._min_date,scheduler._max_date,scheduler._mode);scheduler._rendered=[];for(d=0;d<g.length-2;d++)scheduler._rendered[d]=g[d]}function k(a){var c=document.getElementById(a),d=scheduler._y-scheduler.xy.nav_height;d<0&&(d=0);var b=scheduler._x-scheduler.xy.map_date_width-scheduler.xy.map_description_width-1;b<0&&(b=0);c.style.height=d+"px";c.style.width=
b+"px";c.style.marginLeft=scheduler.xy.map_date_width+scheduler.xy.map_description_width+1+"px";c.style.marginTop=scheduler.xy.nav_height+2+"px"}(function(){scheduler._isMapPositionSet=!1;var a=document.createElement("div");a.className="dhx_map";a.id="dhx_gmap";a.style.dispay="none";var c=scheduler._obj;c.appendChild(a);scheduler._els.dhx_gmap=[];scheduler._els.dhx_gmap.push(a);k("dhx_gmap");var d={zoom:scheduler.config.map_inital_zoom||10,center:scheduler.config.map_initial_position,mapTypeId:scheduler.config.map_type||
google.maps.MapTypeId.ROADMAP},b=new google.maps.Map(document.getElementById("dhx_gmap"),d);b.disableDefaultUI=!1;b.disableDoubleClickZoom=!scheduler.config.readonly;google.maps.event.addListener(b,"dblclick",function(a){if(!scheduler.config.readonly&&scheduler.config.dblclick_create){var b=a.latLng;geocoder.geocode({latLng:b},function(a,c){if(c==google.maps.GeocoderStatus.OK)b=a[0].geometry.location,scheduler.addEventNow({lat:b.lat(),lng:b.lng(),event_location:a[0].formatted_address,start_date:scheduler._date,
end_date:scheduler.date.add(scheduler._date,scheduler.config.time_step,"minute")})})}});var e={content:""};if(scheduler.config.map_infowindow_max_width)e.maxWidth=scheduler.config.map_infowindow_max_width;scheduler.map={_points:[],_markers:[],_infowindow:new google.maps.InfoWindow(e),_infowindows_content:[],_initialization_count:-1,_obj:b};geocoder=new google.maps.Geocoder;scheduler.config.map_resolve_user_location&&navigator.geolocation&&(scheduler._isMapPositionSet||navigator.geolocation.getCurrentPosition(function(a){var c=
new google.maps.LatLng(a.coords.latitude,a.coords.longitude);b.setCenter(c);b.setZoom(scheduler.config.map_zoom_after_resolve||10);scheduler.map._infowindow.setContent(scheduler.locale.labels.marker_geo_success);scheduler.map._infowindow.position=b.getCenter();scheduler.map._infowindow.open(b);scheduler._isMapPositionSet=!0},function(){scheduler.map._infowindow.setContent(scheduler.locale.labels.marker_geo_fail);scheduler.map._infowindow.setPosition(b.getCenter());scheduler.map._infowindow.open(b);
scheduler._isMapPositionSet=!0}));google.maps.event.addListener(b,"resize",function(){a.style.zIndex="5";b.setZoom(b.getZoom())});google.maps.event.addListener(b,"tilesloaded",function(){a.style.zIndex="5"});a.style.display="none"})();scheduler.attachEvent("onSchedulerResize",function(){return this._mode=="map"?(this.map_view(!0),!1):!0});var l=scheduler.render_data;scheduler.render_data=function(a,c){if(this._mode=="map"){e();for(var d=scheduler.get_visible_events(),b=0;b<d.length;b++)scheduler.map._markers[d[b].id]||
i(d[b],!1,!1)}else return l.apply(this,arguments)};scheduler.map_view=function(a){scheduler.map._initialization_count++;var c=scheduler._els.dhx_gmap[0];scheduler._els.dhx_cal_data[0].style.width=scheduler.xy.map_date_width+scheduler.xy.map_description_width+1+"px";scheduler._min_date=scheduler.config.map_start||new Date;scheduler._max_date=scheduler.config.map_end||scheduler.date.add(new Date,1,"year");scheduler._table_view=!0;f(a);if(a){g();e();c.style.display="block";k("dhx_gmap");for(var d=scheduler.map._obj.getCenter(),
b=scheduler.get_visible_events(),h=0;h<b.length;h++)scheduler.map._markers[b[h].id]||i(b[h])}else c.style.display="none";google.maps.event.trigger(scheduler.map._obj,"resize");scheduler.map._initialization_count===0&&d&&scheduler.map._obj.setCenter(d);scheduler._selected_event_id&&m(scheduler._selected_event_id)};var m=function(a){scheduler.map._obj.setCenter(scheduler.map._points[a]);scheduler.callEvent("onClick",[a])},i=function(a,c,d){var b=scheduler.config.map_error_position;a.lat&&a.lng&&(b=
new google.maps.LatLng(a.lat,a.lng));var e=scheduler.templates.marker_text(a.start_date,a.end_date,a);scheduler._new_event||(scheduler.map._infowindows_content[a.id]=e,scheduler.map._markers[a.id]&&scheduler.map._markers[a.id].setMap(null),scheduler.map._markers[a.id]=new google.maps.Marker({position:b,map:scheduler.map._obj}),google.maps.event.addListener(scheduler.map._markers[a.id],"click",function(){scheduler.map._infowindow.setContent(scheduler.map._infowindows_content[a.id]);scheduler.map._infowindow.open(scheduler.map._obj,
scheduler.map._markers[a.id]);scheduler._selected_event_id=a.id;scheduler.render_data()}),scheduler.map._points[a.id]=b,c&&scheduler.map._obj.setCenter(scheduler.map._points[a.id]),d&&scheduler.callEvent("onClick",[a.id]))};scheduler.attachEvent("onClick",function(a){if(this._mode=="map"){scheduler._selected_event_id=a;for(var c=0;c<scheduler._rendered.length;c++)scheduler._rendered[c].className="dhx_map_line",scheduler._rendered[c].getAttribute("event_id")==a&&(scheduler._rendered[c].className+=
" highlight");scheduler.map._points[a]&&scheduler.map._markers[a]&&(scheduler.map._obj.setCenter(scheduler.map._points[a]),google.maps.event.trigger(scheduler.map._markers[a],"click"))}return!0});var j=function(a){a.event_location&&geocoder?geocoder.geocode({address:a.event_location,language:scheduler.uid().toString()},function(c,d){var b={};if(d!=google.maps.GeocoderStatus.OK){if(b=scheduler.callEvent("onLocationError",[a.id]),!b||b===!0)b=scheduler.config.map_error_position}else b=c[0].geometry.location;
a.lat=b.lat();a.lng=b.lng();scheduler._selected_event_id=a.id;scheduler._latLngUpdate=!0;scheduler.callEvent("onEventChanged",[a.id,a]);i(a,!0,!0)}):i(a,!0,!0)},n=function(a){a.event_location&&geocoder&&geocoder.geocode({address:a.event_location,language:scheduler.uid().toString()},function(c,d){var b={};if(d!=google.maps.GeocoderStatus.OK){if(b=scheduler.callEvent("onLocationError",[a.id]),!b||b===!0)b=scheduler.config.map_error_position}else b=c[0].geometry.location;a.lat=b.lat();a.lng=b.lng();
scheduler._latLngUpdate=!0;scheduler.callEvent("onEventChanged",[a.id,a])})},o=function(a,c,d,b){setTimeout(function(){var b=a.apply(c,d);a=c=d=null;return b},b||1)};scheduler.attachEvent("onEventChanged",function(a){if(this._latLngUpdate)this._latLngUpdate=!1;else{var c=scheduler.getEvent(a);c.start_date<scheduler._min_date&&c.end_date>scheduler._min_date||c.start_date<scheduler._max_date&&c.end_date>scheduler._max_date||c.start_date.valueOf()>=scheduler._min_date&&c.end_date.valueOf()<=scheduler._max_date?
(scheduler.map._markers[a]&&scheduler.map._markers[a].setMap(null),j(c)):(scheduler._selected_event_id=null,scheduler.map._infowindow.close(),scheduler.map._markers[a]&&scheduler.map._markers[a].setMap(null))}return!0});scheduler.attachEvent("onEventIdChange",function(a,c){var d=scheduler.getEvent(c);if(d.start_date<scheduler._min_date&&d.end_date>scheduler._min_date||d.start_date<scheduler._max_date&&d.end_date>scheduler._max_date||d.start_date.valueOf()>=scheduler._min_date&&d.end_date.valueOf()<=
scheduler._max_date)scheduler.map._markers[a]&&(scheduler.map._markers[a].setMap(null),delete scheduler.map._markers[a]),scheduler.map._infowindows_content[a]&&delete scheduler.map._infowindows_content[a],j(d);return!0});scheduler.attachEvent("onEventAdded",function(a,c){if(!scheduler._dataprocessor&&(c.start_date<scheduler._min_date&&c.end_date>scheduler._min_date||c.start_date<scheduler._max_date&&c.end_date>scheduler._max_date||c.start_date.valueOf()>=scheduler._min_date&&c.end_date.valueOf()<=
scheduler._max_date))scheduler.map._markers[a]&&scheduler.map._markers[a].setMap(null),j(c);return!0});scheduler.attachEvent("onBeforeEventDelete",function(a){scheduler.map._markers[a]&&scheduler.map._markers[a].setMap(null);scheduler._selected_event_id=null;scheduler.map._infowindow.close();return!0});scheduler._event_resolve_delay=1500;scheduler.attachEvent("onEventLoading",function(a){scheduler.config.map_resolve_event_location&&a.event_location&&!a.lat&&!a.lng&&(scheduler._event_resolve_delay+=
1500,o(n,this,[a],scheduler._event_resolve_delay));return!0});scheduler.attachEvent("onEventCancel",function(a,c){c&&(scheduler.map._markers[a]&&scheduler.map._markers[a].setMap(null),scheduler.map._infowindow.close());return!0})});
