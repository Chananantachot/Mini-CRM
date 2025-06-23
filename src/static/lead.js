
function loadLeads(custId) {
  const colModel = [
    {
      name: 'id',
      index: 'id',
      key: true,
      hidden: true
    },
    { label: 'Frist Name', name: 'firstName', width: 150, editable: true, editrules: { required: true }, editoptions: { dataEvents: [createAutoCorrectEvent()] } },
    { label: 'Last Name', name: 'lastName', width: 150, editable: true, editrules: { required: true }, editoptions: { dataEvents: [createAutoCorrectEvent()] } },
    { label: 'Email', name: 'email', width: 100, editable: true, editrules: { required: true }, editoptions: { dataEvents: [createAutoCorrectMailEvent()] } },
    { label: 'Source', name: 'source', width: 100, editable: true },
    { label: 'Status', name: 'status', width: 100, editable: true },
    { label: 'Date created', name: 'created_at', width: 100, editable: false, align: 'center', formatter: 'date' },
    { label: 'Date updated', name: 'updated_at', width: 100, editable: false, align: 'center', formatter: 'date' }
  ];
  var caption = custId ? `Customer Pickig Product Interestes` : 'Leads Management';
  var subGrid = custId ? false : true;
  var url = custId ? `/api/leads/${custId}` : '/api/leads';
  
  init_jqGrid('gridLeads', 'pager', url, '/api/lead/new', '/api/lead/edit',
    colModel, caption, subGrid, function (data) { leads_loadComplete(data) },
    function (id) { lead_onSelectRow(id) }, function (subgrid_id, id) { lead_subGridRowExpanded(subgrid_id, id) })
}

function lead_onSelectRow(ids) {
  $("#gridProdsInterest").jqGrid('setGridParam', { url: '/api/products/lead/' + ids + '/interested' });
  $("#gridProdsInterest").trigger("reloadGrid");
}

function leads_loadComplete(datas) {
  fetch('/api/userRoles', {
    headers: {
      'Accept': 'application/json'
    }
  }).then(resp => resp.json()
  ).then(data => {
    $("#gridLeads").navGrid("#pager",
      {
        edit: data.isAdminRole,
        add: false, //data.isAdminRole,
        del: false,
        search: true,
        refresh: true,
        view: true,
        position: "left",
        cloneToTop: true
      },
      {
        // edit options
        url: '/api/lead/edit', //'/api/customer/edit',
        closeAfterEdit: true,
        reloadAfterSubmit: true,
        errorTextFormat: function (response) {
          const json = JSON.parse(response.responseText);
          return json.message || "An error occurred";
        },
        afterSubmit: function (response, postdata) {
          var $self = $(this), p = $self.jqGrid("getGridParam");
          p.datatype = "json";
          $self.trigger("reloadGrid", { page: p.page, current: true });
          return [true, '']; // no error
        }
      },
      {
        // Add options
        url: '/api/lead/new', //'/api/customer/new',
        closeAfterAdd: true,
        reloadAfterSubmit: true,
        errorTextFormat: function (response) {
          const json = JSON.parse(response.responseText);
          return json.message || "An error occurred";
        },
        afterSubmit: function (response, postdata) {
          var $self = $(this), p = $self.jqGrid("getGridParam");
          p.datatype = "json";
          $self.trigger("reloadGrid", { page: p.page, current: true });
          return [true, '']; // no error
        }
      }
    );
  })
}

function lead_subGridRowExpanded(subgrid_id, leadId) {
  var editingRowId; 

  var subgrid_table_id = subgrid_id + "_opportunity";
  var pager_id = "p_" + subgrid_table_id;

  $("#" + subgrid_id).html("<table id='" + subgrid_table_id + "'></table><div id='" + pager_id + "' class='scroll'></div>");
  var grid = $("#" + subgrid_table_id).jqGrid({
    url: '/api/opportunities/' + leadId,
    editurl: `/api/${leadId}/opportunities/edit`,
    datatype: "json",
    colModel: [
      { name: 'id', key: true, hidden: true },
      { name: 'lead_id', key: false, hidden: true },
      { name: 'current_stage', label: 'Current Stage', editable: true, editrules: { required: true }},
      { name: 'expected_value', label: 'Expected Value', editable: true, editrules: { required: true }},
      { name: 'closure_date', label: 'Closure Date', editable: true, editrules: { required: true , date: true }, datefmt: 'yyyy-mm-dd',
        editoptions: { dataInit: function (element) {
            var $wrapper = $("<div class='input-group2 date'></div>");
            var $addon = $('<span class="input-group-addon2"><i class="glyphicon glyphicon-th"></i></span>');
            const today = new Date();
            const formattedDate = today.toISOString().slice(0, 10);
            $(element).val(formattedDate);
            $(element).wrap($wrapper).after($addon);

            $(element).datepicker({
              format: 'yyyy-mm-dd',
              orientation: "bottom left",
              clearBtn: true,
            });
          }
        }
      },
      {
        name: 'converted', label: 'Converted', editable: true,
        formatter: "checkbox",
        edittype: "checkbox", align: "center"
      }
    ],
    pager: pager_id,
    multiselect: false,
    height: "100%",
    caption: "Sales",
    onSelectRow: function (id) {
      editingRowId = id;
    }
  });

  var originalCheckValues = $.jgrid.checkValues,
      originalHideModal = $.jgrid.hideModal,
      iColWithError = 0;
  $.jgrid.checkValues = function(val, valref,g, customobject, nam) {
      var tr,td,
          ret = originalCheckValues.call(this,val, valref,g, customobject, nam);
      if (!ret[0]) {
          tr = this.rows.namedItem(editingRowId);;
          if (tr) {
              $(tr).children('td').children('input.editable[type="text"]').removeClass("ui-state-error");
              iColWithError = valref; // save to set later the focus
              td = tr.cells[valref];
              if (td) {
                  $(td).find('input.editable[type="text"]').addClass("ui-state-error");
                  $(td).find('input.editable[type="text"]').focus();
              }
          }
      }
      return ret
  };
  $.jgrid.hideModal = function (selector,o) {
      var input, oldOnClose, td,
          tr = grid[0].rows.namedItem(editingRowId);
      if (tr) {
          td = tr.cells[iColWithError];
          if (td) {
              input = $(td).children('input.editable[type="text"]:first');
              if (input.length > 0) {
                  oldOnClose = o.onClose;
                  o.onClose = function(s) {
                      if ($.isFunction(oldOnClose)) {
                          oldOnClose.call(s);
                      }
                      setTimeout(function(){
                          input.focus();
                      },100);
                  };
              }
          }
      }
      originalHideModal.call(this,selector,o);
  };

  $.jgrid.info_dialog = function() {
      console.log("jqGrid tried to show an error dialog, suppressing it.");
      return; // do nothing
  };

  $("#" + subgrid_table_id).navGrid("#" + pager_id,
    { edit: false, add: false, del: false, search: false, refresh: false },
    {}, {}
  )
  $("#" + subgrid_table_id).jqGrid('inlineNav', "#" + pager_id, {
    edit: true,
    add: true,
    del: false,
    cancel: true,
    save: true,
    addParams: {
      addRowPage: 'last', // Add the new row to the last page (or 'first', 'current')
      position: 'last',   // Position the new row at the end of the grid (or 'first')
      addRowParams: {
        keys: true,
        url: `/api/${leadId}/opportunities/new`,
        mtype: 'POST',
        onSuccess: function (response) {
          var $self = $(this), p = $self.jqGrid("getGridParam");
          p.datatype = "json";
          $self.trigger("reloadGrid", { page: p.page, current: true });
          return [true, '']; // No error
        }
      },
      editParams: {
        url: `/api/${leadId}/opportunities/edit`,
        keys: true,
        mtype: 'POST',
        onSuccess: function (response) {
          var $self = $(this), p = $self.jqGrid("getGridParam");
          p.datatype = "json";
          $self.trigger("reloadGrid", { page: p.page, current: true });
          return [true, '']; // No error
        },
      },
      // This callback fires AFTER the new empty row is inserted and put into edit mode.
      addRowCallback: function (rowid, response) {
        // Find the input field for 'closure_date' in the newly added row
        var closureDateInput = $('#' + rowid + '_closure_date');
        if (closureDateInput.length) {
          // Initialize the Datepicker on this specific input
          closureDateInput.datepicker({
            dateFormat: 'yy-mm-dd',
            showOn: 'focus',
            changeMonth: true,
            changeYear: true
          });
        }
      },
    },
  })
}
