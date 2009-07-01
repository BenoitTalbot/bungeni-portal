(function($) {
  $(document).ready(function() {
      // wire workflow dropdown menu to use POST actions
      var menu_links = $('#plone-contentmenu-workflow dd.actionMenuContent a');
      menu_links.bungeniPostWorkflowActionMenuItem();

      // set up parliament date range selection
      $("select[id=form.parliament]").bungeniTimeRangeSelect(false, false);

      // set up time range form automation
      var errors = $(".groupsitting-form .widget.error").length > 0;
      $(".groupsitting-form .widget-dropdownwidget select").
        bungeniTimeRangeSelect(true, !errors);

      // set up calendar resizing
      $("#calendar-table").bungeniSafeResize();

      // set up calendar item scheduling (drag and drop)
      $("#items-for-scheduling tbody tr").bungeniDragAndDropScheduling();
      
      // set up calendar ajax
      $('#weekly-calendar').bungeniCalendarInteractivity(true);
      $('#daily-calendar').bungeniCalendarInteractivity(false);
      $('#scheduling-calendar').bungeniSchedulingCalendar();
      $('#scheduling-calendar').bungeniInteractiveSchedule();
    });
 })(jQuery);
