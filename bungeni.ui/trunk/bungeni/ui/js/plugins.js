(function($) {
  var re_time_range = /(.*) \((\d+):(\d+):\d+-(\d+):(\d+):\d+\)/;

  function _update_tables(selector, data) {
    var calendar = $(selector);
    var old_tables = calendar.find("table");
    var new_tables = $(data).find(selector).find("table");
    
    old_tables.eq(0).replaceWith(new_tables.eq(0));
    old_tables.eq(1).replaceWith(new_tables.eq(1));
  }

  $.fn.bungeniDragAndDropScheduling = function() {
    $(this).draggable({
        cursor: 'move',
            cursorAt: { left: 5 },
            helper: function() {
            var title = $(this).children().eq(1).text();
            var helper = $('<div class="helper" />');
            helper.text(title);
            return helper;
          },
        });

  }

  $.fn.bungeniReorderSchedulings = function() {
    var calendar = $(this);
    var selector = '#'+calendar.attr('id');

    $("#scheduling-table tbody td.actions a").click(function() {
        $(this).blur();
        
        var row = $(this).parents("tr").eq(0);
        
        // manipulate dom to move row up or down
        if ($(this).attr("rel") == "move-up") {
          var element = row.prev();
          if (!element) return false;
          element.insertAfter(row);
        } else {
          var element = row.next();
          if (!element) return false;
          element.insertBefore(row);
        }
        
        var ids = [];
        $.each(calendar.find("a[rel=item]"), function(i, o) {
            var name = $(o).attr('name');
            if (name && ids.indexOf(name) == -1)
              ids.push(name);
          });

        // the url is defined as the first link's parent
        var url = $("a[rel=sitting]").attr('href')+'/items/reorder';
        
        var data = {
          "headless": 'true',
          "ordering.count": ids.length,
        };
        
        $.each(ids, function(i, o) {
            data["ordering."+i+"."] = o;
          });

        $("#kss-spinner").show();
        $.post(url, data, function(data, status) {
            $("#kss-spinner").hide();
            if (status == 'success') {
              // throw away result
            }
          });
        return false;
      });
  };
  
  $.fn.bungeniSchedulingCalendar = function() {
    var calendar = $(this);
    var selector = '#'+calendar.attr('id');

    $.each(calendar.find("fieldset"), function(i, o) {
        $(o)
          .droppable({
            accept: "tr",
            tolerance: "touch",
                })
          .bind('drop', function(event, draggable) {
              var target = $(o);
              var element = draggable.draggable;
              var id = $(element).find("a[rel=id]").attr('name');
              var link = target.find("a[rel=schedule-item]");
              var url = link.attr('href');
              
              // ask for a redirect to the current (updated) calendar
              var next_url = $("a[rel=calendar]").attr('href');
              
              $("#kss-spinner").show();
              $.post(url, {
                headless: 'true',
                    next_url: next_url,
                    item_id: id}, function(data, status) {
                  $("#kss-spinner").hide();
                  if (status == 'success') {
                    _update_tables(selector, data);
                    calendar.bungeniReorderSchedulings();
                  }
                });
            });
      });
  }

  $.fn.bungeniCalendarInteractivity = function(ajax_navigation) {
    var calendar = $(this);
    var selector = '#'+calendar.attr('id');

    if (ajax_navigation)
      calendar.find("thead a.navigation")
        .click(function() {
            $("#kss-spinner").show();
            var href = $(this).attr('href');
            $.get(href, {}, function(data, status) {
                $("#kss-spinner").hide();
                if (status == 'success') {
                  _update_tables(selector, data);
                  calendar.bungeniCalendarInteractivity(ajax_navigation);
                }
              });
            return false;
          });
  }
  
  $.fn.bungeniSafeResize = function() {
    $.each($(this), function(i, o) {
        var table = $(o);
        if (table) {
          var wrapper = $('<div id="calendar-table-resize-wrapper" />');
          table.wrap(wrapper);
          wrapper = table.parents("#calendar-table-resize-wrapper");
          
          wrapper
            .resizable({
              helper: "resize-proxy",
                  handles: "s",
                  });
          
          wrapper.bind("resizestop", function(event, ui) {
              var height = wrapper.height();
              table.css("height", height+"px");
            });
        }
      });
  };
  
  $.fn.bungeniCalendarSittingsDragAndDrop = function(sittings) {
    $.each($(this), function(i, o) {
        var id = $(o).attr('id');
        var dd = new YAHOO.util.DDProxy(id);

      });
  };
  
  $.fn.bungeniPostWorkflowActionMenuItem = function() {
    $(this).click(function() {
        var url_parts = $(this).attr("href").split('?');
        var url = url_parts[0];
        var args = url_parts[1].split('=');
        if (args[0] == 'transition') {
          var transition_id = args[1];
          
          var input = $('<input type="hidden" name="transition"/>').
            attr("value", transition_id);
          
          var form = $("<form/>").
            attr("method", "POST").
            attr("action", url).
            appendTo(document.body);
          
          input.appendTo(form);
          form.get(0).submit();
          
          return false;
        }
      });
  };
  
  // when selecting an option on the format "Label
  // (start_time-end_time)", listen to the ``change`` event and
  // update corresponding start- and end time options
  $.fn.bungeniTimeRangeSelect = function() {
    $.each($(this), function(i, o) {
      var options = $(o).children();
      var form = $(o).parents("form").eq(0);

      var start_hour = form.find("select[name$=start_date__hour]").get(0);
      if (!start_hour) return;
      var start_minute = form.find("select[name$=start_date__minute]").get(0);
      if (!start_minute) return;
      var end_hour = form.find("select[name$=end_date__hour]").get(0);
      if (!end_hour) return;
      var end_minute = form.find("select[name$=end_date__minute]").get(0);
      if (!end_minute) return;

      var option_matches = [];
      $.each(options, function(j, p) {
          var option = $(p);
          var matches = re_time_range.exec(option.text());
          
          if (matches) {
            option_matches.push(matches);
            option.text(matches[1]);
          }
        });

      function handle_change() {
        var matches = option_matches[o.selectedIndex];

        if (!matches) return;

        // convert matches to integers
        for (var k=1; k < 5; k++) {
          var v = matches[k];
          if (v[0] == '0') v = v[1];
          matches[k] = parseInt(v);
        }

        // for each dropdown, change selection
        start_hour.selectedIndex = matches[2]
        start_minute.selectedIndex = matches[3];
        end_hour.selectedIndex = matches[4];
        end_minute.selectedIndex = matches[5];
      };

      // setup event handler
      $(o).change(handle_change);

      // initialize
      handle_change();
    });
  };
    
    
  $.fn.yuiTabView = function(elements) {
    if (!YAHOO.widget.TabView) {
      return console.log("Warning: YAHOO.widget.TabView module not loaded.")
    }
    var tab_view = new YAHOO.widget.TabView();
    
    $.each(elements, function(i, o) {
        var label = YAHOO.util.Dom.getFirstChild(o)
          tab_view.addTab(new YAHOO.widget.Tab({
              labelEl : label, contentEl : o,
                  }));
      });

    tab_view.appendTo($(this).get(0));
    tab_view.set('activeTab', tab_view.getTab(0));
  };
  
  $.fn.yuiDataTable = function(context_name, link_url, data_url, fields, columns, table_id) {
    if (!YAHOO.widget.DataTable) {
      return console.log("Warning: YAHOO.widget.DataTable module not loaded.")
    }

    var datasource, columns, config;
    
    var formatter = function(elCell, oRecord, oColumn, oData) {
      var object_id = oRecord.getData("object_id");
      elCell.innerHTML = "<a href=\"" +  link_url + '/' + object_id + "\">" + oData + "</a>";
    };
    
    YAHOO.widget.DataTable.Formatter[context_name+"Custom"] = formatter;

    // Setup Datasource for Container Viewlet
    fields.push({key:"object_id"});
    datasource = new YAHOO.util.DataSource(data_url);
    datasource.responseType   = YAHOO.util.DataSource.TYPE_JSON;
    datasource.responseSchema = {
    resultsList: "nodes",
    fields: fields,
    metaFields: { totalRecords: "length", sortKey:"sort", sortDir:"dir", paginationRecordOffset:"start"}
    }
      
    var get_filter = function(oSelf) {
        var table_columns = oSelf.getColumnSet()
        var qstr = '';
        for (i=0;i<table_columns.keys.length;i++){
            var input_id = 'input#input-' + table_columns.keys[i].getId();
            
            //alert( 'filter_' + table_columns.keys[i].getKey() + ' : input-' + table_columns.keys[i].getId());
            qstr = qstr + '&filter_' + table_columns.keys[i].getKey() + '=' + $(input_id).val()

        };   
        return qstr;
    };  
      
    // A custom function to translate the js paging request into a datasource query    
    var RequestBuilder = function(oState, oSelf) {
      // Get states or use defaults
      oState = oState || {pagination:null, sortedBy:null};
      var sort = (oState.sortedBy) ? oState.sortedBy.key : "";
      var dir = (oState.sortedBy && oState.sortedBy.dir === YAHOO.widget.DataTable.CLASS_DESC) ? "" : "desc";
      var startIndex = (oState.pagination) ? oState.pagination.recordOffset : 0;
      var results = (oState.pagination) ? oState.pagination.rowsPerPage : 100;  
       
      // Build custom request
      return  "sort=" + sort +
      "&dir=" + dir +
      "&start=" + startIndex +
      "&limit=" +  results +
      get_filter(oSelf); 
     
      
      
    };

    
    
    config = {
    paginator: new YAHOO.widget.Paginator({
      rowsPerPage: 25,
          template: YAHOO.widget.Paginator.TEMPLATE_ROWS_PER_PAGE,
          rowsPerPageOptions: [10,25,50,100],
          //pageLinks: 5
          }),
    initialRequest : 'start=0&limit=20',
    generateRequest : RequestBuilder, 
    sortedBy : { dir : YAHOO.widget.DataTable.CLASS_ASC },
    dynamicData: true, // Enables dynamic server-driven data
    }

    table = new YAHOO.widget.DataTable(YAHOO.util.Dom.get(table_id), columns, datasource, config  );
    // Update totalRecords on the fly with value from server
    table.handleDataReturnPayload = function(oRequest, oResponse, oPayload) {
      oPayload.totalRecords = oResponse.meta.totalRecords;
      oPayload.pagination = oPayload.pagination || {};
      oPayload.pagination.recordOffset = oResponse.meta.paginationRecordOffset;
      return oPayload;
    };

    // create the inputs for column filtering
    var i=0;
    var table_columns = table.getColumnSet()
    for (i=0;i<table_columns.keys.length;i++){
        var input = document.createElement('input');
        input.setAttribute('type', 'text');
        input.setAttribute('name', 'filter_' + table_columns.keys[i].getKey());
        input.setAttribute('id', 'input-' + table_columns.keys[i].getId());
        table_columns.keys[i].getThEl().appendChild(input);
    }

    table.sortColumn = function(oColumn, sDir) {
      // Default ascending
      cDir = "asc";
      // If already sorted, sort in opposite direction
      var sorted_by =   this.get("sortedBy");
      sorted_by = sorted_by || {key:null, dir:null};
      if(oColumn.key == sorted_by.key) {
        cDir = (sorted_by.dir === YAHOO.widget.DataTable.CLASS_ASC || sorted_by.dir == "") ? "desc" : "asc";
      };
       
      if (sDir == YAHOO.widget.DataTable.CLASS_ASC) {
        cDir = "asc"
          }
      else if (sDir == YAHOO.widget.DataTable.CLASS_DESC) {
        cDir = "desc"
      };

      // Pass in sort values to server request
      var newRequest = "sort=" + oColumn.key + "&dir=" + cDir + "&start=0";
      // Create callback for data request
      var oCallback = {
      success: this.onDataReturnInitializeTable,
      failure: this.onDataReturnInitializeTable,
      scope: this,
      argument: {
          // Pass in sort values so UI can be updated in callback function
        sorting: {
          key: oColumn.key,
          dir: (cDir === "asc") ? YAHOO.widget.DataTable.CLASS_ASC : YAHOO.widget.DataTable.CLASS_DESC,
        }
        }
      };
      newRequest = newRequest + get_filter(this);                  
      // Send the request
      this.getDataSource().sendRequest(newRequest, oCallback);
    };

  };
 })(jQuery);
