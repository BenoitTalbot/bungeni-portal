/*
This software is allowed to use under GPL or you need to obtain Commercial or Enterise License
to use it in non-GPL project. Please contact sales@dhtmlx.com for details
*/
scheduler._wa={};scheduler.xy.week_agenda_scale_height=20;scheduler.templates.week_agenda_event_text=function(c,g,h){return scheduler.templates.event_date(c)+" "+h.text};scheduler.date.week_agenda_start=scheduler.date.week_start;scheduler.date.week_agenda_end=function(c){return scheduler.date.add(c,7,"day")};scheduler.date.add_week_agenda=function(c,g){return scheduler.date.add(c,g*7,"day")};
scheduler.attachEvent("onSchedulerReady",function(){var c=scheduler.templates;if(!c.week_agenda_date)c.week_agenda_date=c.week_date});(function(){var c=scheduler.date.date_to_str("%l, %F %d");scheduler.templates.week_agenda_scale_date=function(g){return c(g)}})();
scheduler.attachEvent("onTemplatesReady",function(){scheduler.attachEvent("onSchedulerResize",function(){return this._mode=="week_agenda"?(this.week_agenda_view(!0),!1):!0});var c=scheduler.render_data;scheduler.render_data=function(b){if(this._mode=="week_agenda")scheduler.week_agenda_view(!0);else return c.apply(this,arguments)};var g=function(){scheduler._cols=[];var b=parseInt(scheduler._els.dhx_cal_data[0].style.width);scheduler._cols.push(Math.floor(b/2));scheduler._cols.push(b-scheduler._cols[0]-
1);scheduler._colsS={0:[],1:[]};for(var a=parseInt(scheduler._els.dhx_cal_data[0].style.height),m=0;m<3;m++)scheduler._colsS[0].push(Math.floor(a/(3-scheduler._colsS[0].length))),a-=scheduler._colsS[0][m];scheduler._colsS[1].push(scheduler._colsS[0][0]);scheduler._colsS[1].push(scheduler._colsS[0][1]);a=scheduler._colsS[0][scheduler._colsS[0].length-1];scheduler._colsS[1].push(Math.floor(a/2));scheduler._colsS[1].push(a-scheduler._colsS[1][scheduler._colsS[1].length-1])},h=function(){g();scheduler._els.dhx_cal_data[0].innerHTML=
"";scheduler._rendered=[];for(var b="",a=0;a<2;a++){var m=scheduler._cols[a],c="dhx_wa_column";a==1&&(c+=" dhx_wa_column_last");b+="<div class='"+c+"' style='width: "+m+"px;'>";for(var e=0;e<scheduler._colsS[a].length;e++){var j=scheduler.xy.week_agenda_scale_height-2,u=scheduler._colsS[a][e]-j-2,k=Math.min(6,e*2+a);b+="<div class='dhx_wa_day_cont'><div style='height:"+j+"px; line-height:"+j+"px;' class='dhx_wa_scale_bar'></div><div style='height:"+u+"px;' class='dhx_wa_day_data' day='"+k+"'></div></div>"}b+=
"</div>"}scheduler._els.dhx_cal_date[0].innerHTML=scheduler.templates[scheduler._mode+"_date"](scheduler._min_date,scheduler._max_date,scheduler._mode);scheduler._els.dhx_cal_data[0].innerHTML=b;for(var l=scheduler._els.dhx_cal_data[0].getElementsByTagName("div"),o=[],a=0;a<l.length;a++)l[a].className=="dhx_wa_day_cont"&&o.push(l[a]);scheduler._wa._selected_divs=[];for(var h=scheduler.get_visible_events(),i=scheduler.date.week_start(scheduler._date),n=scheduler.date.add(i,1,"day"),a=0;a<7;a++){o[a]._date=
i;var v=o[a].childNodes[0],w=o[a].childNodes[1];v.innerHTML=scheduler.templates.week_agenda_scale_date(i);for(var p=[],r=0;r<h.length;r++){var s=h[r];s.start_date<n&&s.end_date>i&&p.push(s)}p.sort(function(a,b){return a.start_date.valueOf()==b.start_date.valueOf()?a.id>b.id?1:-1:a.start_date>b.start_date?1:-1});for(e=0;e<p.length;e++){var d=p[e],f=document.createElement("div");scheduler._rendered.push(f);var t=scheduler.templates.event_class(d.start_date,d.end_date,d);f.className="dhx_wa_ev_body"+
(t?" "+t:"");if(d._text_style)f.style.cssText=d._text_style;if(d.color)f.style.background=d.color;if(d.textColor)f.style.color=d.textColor;if(scheduler._select_id&&d.id==scheduler._select_id&&(scheduler.config.week_agenda_select||scheduler.config.week_agenda_select===void 0))f.className+=" dhx_cal_event_selected",scheduler._wa._selected_divs.push(f);var q="";d._timed||(q="middle",d.start_date.valueOf()>=i.valueOf()&&d.start_date.valueOf()<=n.valueOf()&&(q="start"),d.end_date.valueOf()>=i.valueOf()&&
d.end_date.valueOf()<=n.valueOf()&&(q="end"));f.innerHTML=scheduler.templates.week_agenda_event_text(d.start_date,d.end_date,d,i,q);f.setAttribute("event_id",d.id);w.appendChild(f)}i=scheduler.date.add(i,1,"day");n=scheduler.date.add(n,1,"day")}};scheduler.week_agenda_view=function(b){scheduler._min_date=scheduler.date.week_start(scheduler._date);scheduler._max_date=scheduler.date.add(scheduler._min_date,1,"week");scheduler.set_sizes();if(b)scheduler._table_view=scheduler._allow_dnd=!0,scheduler._wa._prev_data_border=
scheduler._els.dhx_cal_data[0].style.borderTop,scheduler._els.dhx_cal_data[0].style.borderTop=0,scheduler._els.dhx_cal_data[0].style.overflowY="hidden",scheduler._els.dhx_cal_date[0].innerHTML="",scheduler._els.dhx_cal_data[0].style.top=parseInt(scheduler._els.dhx_cal_data[0].style.top)-scheduler.xy.bar_height-1+"px",scheduler._els.dhx_cal_data[0].style.height=parseInt(scheduler._els.dhx_cal_data[0].style.height)+scheduler.xy.bar_height+1+"px",scheduler._els.dhx_cal_header[0].style.display="none",
h();else{scheduler._table_view=scheduler._allow_dnd=!1;if(scheduler._wa._prev_data_border)scheduler._els.dhx_cal_data[0].style.borderTop=scheduler._wa._prev_data_border;scheduler._els.dhx_cal_data[0].style.overflowY="auto";scheduler._els.dhx_cal_data[0].style.top=parseInt(scheduler._els.dhx_cal_data[0].style.top)+scheduler.xy.bar_height+"px";scheduler._els.dhx_cal_data[0].style.height=parseInt(scheduler._els.dhx_cal_data[0].style.height)-scheduler.xy.bar_height+"px";scheduler._els.dhx_cal_header[0].style.display=
"block"}};scheduler.mouse_week_agenda=function(b){for(var a=b.ev,c=a.srcElement||a.target;c.parentNode;){if(c._date)var g=c._date;c=c.parentNode}if(!g)return b;b.x=0;var e=g.valueOf()-scheduler._min_date.valueOf();b.y=Math.ceil(e/6E4/this.config.time_step);if(this._drag_mode=="move"){this._drag_event._dhx_changed=!0;this._select_id=this._drag_id;for(var j=0;j<scheduler._rendered.length;j++)if(scheduler._drag_id==this._rendered[j].getAttribute("event_id"))var h=this._rendered[j];if(!scheduler._wa._dnd){var k=
h.cloneNode(!0);this._wa._dnd=k;k.className=h.className;k.id="dhx_wa_dnd";k.className+=" dhx_wa_dnd";document.body.appendChild(k)}var l=document.getElementById("dhx_wa_dnd");l.style.top=(a.pageY||a.clientY)+20+"px";l.style.left=(a.pageX||a.clientX)+20+"px"}return b};scheduler.attachEvent("onBeforeEventChanged",function(){if(this._mode=="week_agenda"&&this._drag_mode=="move"){var b=document.getElementById("dhx_wa_dnd");b.parentNode.removeChild(b);scheduler._wa._dnd=!1}return!0});scheduler.attachEvent("onEventSave",
function(b,a,c){if(c&&this._mode=="week_agenda")this._select_id=b;return!0});scheduler._wa._selected_divs=[];scheduler.attachEvent("onClick",function(b){if(this._mode=="week_agenda"&&(scheduler.config.week_agenda_select||scheduler.config.week_agenda_select===void 0)){if(scheduler._wa._selected_divs)for(var a=0;a<this._wa._selected_divs.length;a++){var c=this._wa._selected_divs[a];c.className=c.className.replace(/ dhx_cal_event_selected/,"")}this.for_rendered(b,function(a){a.className+=" dhx_cal_event_selected";
scheduler._wa._selected_divs.push(a)});scheduler.select(b);return!1}return!0})});
