(function($) {
  var re_time_range = /(.*) \((\d+):(\d+):\d+-(\d+):(\d+):\d+\)/;
  var re_date_range = /(.*) \((?:(\d+)\/(\d+)\/(\d+)|\?)-(?:(\d+)\/(\d+)\/(\d+)|\?)\)/;

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

  $.fn.bungeniInteractiveSchedule = function() {
    var calendar = $(this);
    var selector = '#'+calendar.attr('id');

    // hide edit action
    calendar.find("a[rel=edit-scheduling]").hide();

    var editors = {};
    
    // set up expandable sections
    calendar.find("a.expandable").click(function() {
        var expandable = $(this).siblings(".expandable");
        var form = $(this).siblings("form");
        var textarea = form.find("textarea");
        var id = textarea.attr('id');
          
        if ($(this).hasClass('enabled')) {
          expandable.hide();
          $(this).removeClass('enabled');
          var editor = editors[id];
          if (editor) {
            editor.destroy();
          }
        } else {
          $(this).addClass('enabled');
          expandable.show();
          var editor = new YAHOO.widget.SimpleEditor(id);
          editor.render();
          editors[id] = editor;
        }
      });
    
    // set up ajax form submit
    var form = calendar.find("form");
    $.each(form.find("textarea"), function(i, o) {
        var id = $(o).attr('id');
      });

    form.ajaxForm({
        'beforeSubmit': function() { $("#kss-spinner").show() },
          'success': function(html, status, form) {
          $("#kss-spinner").hide();
          var discussion = form.siblings(".discussion");
          form.siblings("a.expandable").triggerHandler("click");
          var html = form.find("textarea").val();
          discussion.empty();
          discussion.append($("<div>"+html+"</div>"));
        }});

    // create and insert category rows
    var current = null;
    $.each(calendar.find("a[rel=category]"), function(i, o) {
        var id = $(this).attr('name');
        if (id == current) return;
        current = id;
        
        var row = $(this).parents("tr").eq(0);
        var cols = row.children().length;
        
        category_row =
          $('<tr class="category"><td colspan="'+cols+'"></td></tr>');
        var column = category_row.find("td");
        column.text($(this).text());
        $(o).appendTo(column);

        category_row.insertBefore(row);
      });
    
    $.each(calendar.find("select"), function(i, o) {
        var dropdown = $(o);
        var row = dropdown.parents("tr").eq(0);

        dropdown.change(function(event) {
            var index = o.selectedIndex;
            o.selectedIndex = 0;

            var options = dropdown.children();
            var option = options.eq(index);
            var value = option.attr('value');
            if (!parseInt(value)) {
              window.location = value;
              return true;
            }
            
            // add/update category bar (vertical table row)
            var cols = row.children().length;

            // remove an immediate previous category row
            row.prev(".category").remove();
            
            // find a previous category rows that match this one
            var category_row = row.
              prevAll('.category').
              eq(0).
              find('a[name='+value+']').
              parents('tr').
              eq(0);

            // if there is a matching category row use it, else create
            // and insert a new row
            if (category_row.length == 0) {
              category_row =
                $('<tr class="category"><td colspan="'+cols+'"></td></tr>');
              category_row.insertBefore(row);
            }

            var column = category_row.find("td");
            column.text(option.text());
            column.find("a").remove();
            $('<a name="'+value+'"></a>').appendTo(column);
            
            // remove matching following category
            row.
              nextAll(".category").
              eq(0).
              find('a[name='+value+']').
              parents('tr').
              eq(0).
              remove();

            // save category assignment
            var url = row.find("a[rel=edit-scheduling]").attr('href');
            var data = {
              'headless': 'true',
              'category_id': value,
            }

            $("#kss-spinner").show();
            $.post(url, data, function(data, status) {
                $("#kss-spinner").hide();
                if (status == 'success') {
                  // throw away result
                }
              });
            dropdown.blur();
          });
      });

    $("#scheduling-table tbody td.actions a").click(function() {
        var link = $(this);
        link.blur();
        
        var mode = null;
        var row = link.parents("tr").eq(0);
        
        // manipulate dom to move row up or down
        switch ($(this).attr("rel")) {
        case "move-scheduling-up":
          var next = row.next();
          if (row.prev().is('.category') && (next.is('.category') || next.length == 0))
            row.prev().remove();
          
          var element = row.prev('not:(.category)');
          if (!element) return false;
          element.insertAfter(row);
          mode = 'up';
          break;
        case "move-scheduling-down":
          if (row.next().is('.category') && row.prev().is('.category'))
            row.prev('.category').remove();
          var element = row.next('not:(.category)');
          if (!element) return false;
          element.insertBefore(row);
          mode = 'down';
          break
        default:
            return true;
        }

        var url = link.attr('href');
        var data = {
          "headless": 'true',
          "mode": mode,
        };

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
                    calendar.bungeniInteractiveSchedule();
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
  $.fn.bungeniTimeRangeSelect = function(same_day, set_default) {
    $.each($(this), function(i, o) {
      var options = $(o).children();
      var form = $(o).parents("form").eq(0);

      var start_year = form.find("select[name$=start_date__year]").get(0);
      var start_month = form.find("select[name$=start_date__month]").get(0);
      var start_day = form.find("select[name$=start_date__day]").get(0);
      var start_hour = form.find("select[name$=start_date__hour]").get(0);
      var start_minute = form.find("select[name$=start_date__minute]").get(0);
      var end_year = form.find("select[name$=end_date__year]").get(0);
      var end_month = form.find("select[name$=end_date__month]").get(0);
      var end_day = form.find("select[name$=end_date__day]").get(0);
      var end_hour = form.find("select[name$=end_date__hour]").get(0);
      var end_minute = form.find("select[name$=end_date__minute]").get(0);

      var handle_date = false;
      var handle_time = false;

      if (start_year && start_month && start_day &&
          end_year && end_month && end_day) {
        handle_date = true;
      }

      if (start_hour && start_minute &&
          end_hour && end_minute) {
        handle_time = true;
      }

      if (!(handle_date || handle_time)) return;

      if (handle_date && same_day) {
        // the year, month and date of the end-time should follow the
        // start-time
        $([end_year, end_month, end_day]).
          attr('disabled', 'disabled');
        $(start_year).change(function() {
            end_year.selectedIndex = start_year.selectedIndex });
        $(start_month).change(function() {
            end_month.selectedIndex = start_month.selectedIndex });
        $(start_day).change(function() {
            end_day.selectedIndex = start_day.selectedIndex });
        form.submit(function() {
            $([end_year, end_month, end_day]).
              attr('disabled', '');
          });
      }
      
      var option_time_matches = [];
      var option_date_matches = [];
      $.each(options, function(j, p) {
          var option = $(p);
          var text = option.text();
          var matches = re_time_range.exec(text);
          
          if (matches) {
            option_time_matches.push(matches);
            option.text(matches[1]);
          }

          var matches = re_date_range.exec(text);
          
          if (matches) {
            option_date_matches.push(matches);
            option.text(matches[1]);
          }
        });

      function convert_matches(matches) {
        for (var k=1; k < matches.length; k++) {
          var v = matches[k];
          if (v[0] == '0') v = v[1];
          matches[k] = parseInt(v);
        }
      }
      
      function select_item(select, value) {
        var options = select.options;
        for (var index in options) {
          var option = options[index];
          if (option.value == value) {
            select.selectedIndex = parseInt(index);
            break;
          }
        }
      }
      
      function handle_time_change() {
        var matches = option_time_matches[o.selectedIndex];
        if (!matches) return;

        // convert matches to integers
        convert_matches(matches);

        // for each dropdown, change selection
        start_hour.selectedIndex = matches[2];
        start_minute.selectedIndex = matches[3];
        end_hour.selectedIndex = matches[4];
        end_minute.selectedIndex = matches[5];
      };

      function handle_date_change() {
        var matches = option_date_matches[o.selectedIndex-1];
        if (!matches) return;
        
        // for each dropdown, change selection
        select_item(start_year, matches[2]);
        select_item(start_month, matches[3]);
        select_item(start_day, matches[4]);
        select_item(end_year, matches[5]);
        select_item(end_month, matches[6]);
        select_item(end_day, matches[7]);
      };

      // setup event handlers
      if (handle_time) {
        $(o).change(handle_time_change);
        if (set_default) handle_time_change();
      }

      if (handle_date) {
        $(o).change(handle_date_change);
        if (set_default) handle_date_change();
      }
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
      
    // filter per column  
    var get_filter = function(oSelf) {
        var table_columns = oSelf.getColumnSet()
        var qstr = '';
        for (i=0;i<table_columns.keys.length;i++){
            var input_id = 'input#input-' + table_columns.keys[i].getId();            
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



     table.fnFilterCallback = {
        success: function(sRequest, oResponse, oPayload){
            var paginator = table.get('paginator');
            table.onDataReturnInitializeTable(sRequest, oResponse, oPayload);
            paginator.set('totalRecords', oResponse.results.length); 
            table.render();          
        },
        failure: function(sRequest, oResponse, oPayload) {
            table.onDataReturnInitializeTable(sRequest, oResponse, oPayload);
            table.render();
        },
    }; 

    table.fnFilterchange = function(e) {       
        table.getDataSource().connMgr.abort()
        table.getDataSource().sendRequest(RequestBuilder(null,table), table.fnFilterCallback);
    };

    // create the inputs for column filtering
    var i=0;
    var table_columns = table.getColumnSet();
    for (i=0;i<table_columns.keys.length;i++){
        var input = document.createElement('input');
        var sButton = document.createElement('button');        
        sButton.innerHTML = 'Search';
        input.setAttribute('type', 'text');
        input.setAttribute('name', 'filter_' + table_columns.keys[i].getKey());
        input.setAttribute('id', 'input-' + table_columns.keys[i].getId());
        sButton.setAttribute('id', 'button-' + table_columns.keys[i].getId());
        sButton.setAttribute('type', 'button');
        //input.setAttribute('change', table.sortColumn(table_columns.keys[i], null));
        var thEl = table_columns.keys[i].getThEl();  
        YAHOO.util.Event.addListener(sButton, 'click', table.fnFilterchange);
        //table_columns.keys[i].getThEl().appendChild(input);              
        thEl.innerHTML = "";
        thEl.appendChild(input);
        thEl.appendChild(sButton);        
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
