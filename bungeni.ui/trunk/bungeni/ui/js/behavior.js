(function($) {
  $(document).ready(function() {
      // wire workflow dropdown menu to use POST actions
      var menu_links = $('#plone-contentmenu-workflow dd.actionMenuContent a');
      menu_links.bungeniPostWorkflowActionMenuItem();

      // set up time range form automation
      $("select").bungeniTimeRangeSelect();

      // set up calendar resizing
      $("#calendar-table").bungeniSafeResize();

      // set up calendar item scheduling (drag and drop)
      $("#items-for-scheduling tbody tr").bungeniDragAndDropScheduling();
      
      // set up calendar ajax
      $('#weekly-calendar').bungeniCalendarInteractivity();

    });
 })(jQuery);
