"use strict";
$(document).ready(function () {
  $('.menu-btn').on('click', function () {
    console.log('menu button clicked!')
    $('.nav-links').toggleClass('active');
  });

  $(window).on("resize", function () {
    var tables = $("table");
    for (var i = 0; i < tables.length; i++) {
      let table = tables[i];
      if (table.id) {
        let id = "#" + table.id;
        var $grid = $(id),
        newWidth = $grid.closest(".ui-jqgrid").parent().width();
        $grid.jqGrid("setGridWidth", newWidth, true);
      }
    }
  })
});

function init_jqGrid(gridId, pageId, getUrl, createUrl, editUrl,
  colModel, caption, subGrid, func_loadcomplete,
  func_onSelectRow, func_subGridRowExpanded) {
  $("#" + gridId).jqGrid({
    url: getUrl,
    editurl: editUrl,
    datatype: "json",
    mtype: 'GET',
    colModel: colModel,
    searching: {
      searchOnEnter: true,
      defaultSearch: "bw"
    },
    caption: caption,
    autowidth: true,
   // loadonce: true,
    rownumbers: true,
    viewrecords: true,
    height: 250,
    rowNum: 100,
    pager: "#" + pageId,
    subGrid: subGrid,
    subGridRowExpanded: function (subgrid_id, id) {
      if (typeof func_subGridRowExpanded === "function") {
        func_subGridRowExpanded(subgrid_id, id);
      }
    },
    loadComplete: function (data) {
      if (typeof func_loadcomplete === "function") {
        func_loadcomplete(data, createUrl, editUrl);
      }
    },
    onSelectRow: function (id) {
      if (typeof func_onSelectRow === "function") {
        func_onSelectRow(id);
      }
    }
  });
}

var lastsel;
function loadUsers() {
  var colModel = [
    {
      name: 'id',
      index: 'id',
      key: true,
      hidden: true
    },
    { label: 'Name', name: 'fullname', width: 150, editable: true },
    { label: 'Email', name: 'email', width: 100, editable: true },
    { label: 'Active', name: 'active', width: 70, editable: true, template: "booleanCheckbox" },
    { label: 'Date created', name: 'created_at', width: 100, editable: false, align: 'center', formatter: 'date' },
    { label: 'Date updated', name: 'updated_at', width: 100, editable: false, align: 'center', formatter: 'date' }
  ];

  init_jqGrid('gridUser', 'pager', '/api/user', '', '/api/user/edit',
    colModel, 'Uses Management', false, function (data) { user_loadComplete(data) },
    function (id) { user_onSelectRow(id) }, function (subgrid_id, id) { })
}

function loadCustomers() {
  const colModel = [
    {
      name: 'id',
      index: 'id',
      key: true,
      hidden: true
    },
    { name: 'canInvoice',index: 'canInvoice',hidden: true},
    { label: 'Frist Name', name: 'firstName', width: 150, editable: true, editrules: { required: true }, editoptions: { dataEvents: [createAutoCorrectEvent()] } },
    { label: 'Last Name', name: 'lastName', width: 150, editable: true, editrules: { required: true }, editoptions: { dataEvents: [createAutoCorrectEvent()] } },
    { label: 'Email', name: 'email', width: 120, editable: true, editrules: { required: true }, editoptions: { dataEvents: [createAutoCorrectMailEvent()] } },
    { label: 'Mobile', name: 'mobile', width: 100, editable: true },
    { label: 'Date created', name: 'created_at', width: 100, editable: false, align: 'center', formatter: 'date' },
    { label: 'Date updated', name: 'updated_at', width: 100, editable: false, align: 'center', formatter: 'date' },
    { name :'inv', label:'' , width: 70, align: 'center',formatter: function (cellvalue, options, rowObject) {  
        if (rowObject.canInvoice == 1)
          return `<a class='btn btn-link' href='/${rowObject.id}/order'>Invoice</a>`;

         return `<a class='btn btn-link' style='pointer-events: none;cursor: default; color:#808080'  href='#'>Invoice</a>`;
    }}
  ];

  init_jqGrid('gridCustomers', 'pager', '/api/customers', '/api/customer/new', '/api/customer/edit',
    colModel, 'Customers Registration', true, function (data) { customer_loadComplete(data, '/api/customer/new', '/api/customer/edit') },
    function (id) { }, function (subgrid_id, id) { cust_subGridRowExpanded(subgrid_id, id) })
}

function loadProducts() {
  $("#gridProducts").jqGrid({
    url: '/api/products',
    datatype: "json",
    height: 350,
    rowNum: 100,
    colModel: [
      {
        name: 'id',
        index: 'id',
        key: true,
        hidden: true
      },
      { label: 'Category', index: 'category', name: 'category', width: 90, editable: true },
      { label: 'Name', index: 'name', name: 'name', width: 110, editable: true },
      { label: 'Description', index: 'description', name: 'description', width: 150, editable: true },
      // { label: 'Stock Keeping Unit', index:'sku', name: 'sku', width: 100, editable: true },   		
      { name: 'price', label: "Price", index: 'total', width: 60, align: "right", sorttype: "float", formatter: "number", summaryType: 'sum' }
    ],
    loadonce: true,
    pager: "#pager",
    autowidth: true,
    viewrecords: true,
    sortname: 'price',
    grouping: true,
    groupingView: {
    groupField: ['category'],
    groupSummary: [true],
    groupColumnShow: [true],
    groupText: ['<b>{0}</b>'],
    groupCollapse: false,
    groupOrder: ['asc']
    },
    searching: {
      searchOnEnter: true,
      defaultSearch: "bw"
    },
    caption: "Products"
  }).navGrid('#pager', { add: false, edit: false, del: false, search: true });
}

function loadProdsInterest() {
  $("#gridProdsInterest").jqGrid({
    url: '/api/products/lead/interested',
    datatype: "json",
    mtype: 'GET',
    colModel: [
      { name: 'id', hidden: true, key: true },
      { name: 'name', label: 'Name', width: 150 },
      { name: 'description', label: 'Description', width: 180 },
      { name: 'price', label: 'Price', width: 80, align: "right" } //,
      //{name:'interested',label:'Interested', width:80, formatter: "checkbox", align:"center"}
    ],
    autowidth: true,
    rownumbers: true,
    height: 150,
    rowNum: 200,
    pager: '#_pager',
    sortname: 'item',
    sortorder: "asc",
    multiselect: true,
    caption: "Interested Products",
    footerrow: true,
    userDataOnFooter: true,
    loadComplete: function (data) {
      let sumAmoutPrice = 0;
      data.forEach((product, idx) => {
        if (product.interested) {
          sumAmoutPrice += product.price;
          $("#gridProdsInterest").jqGrid('setSelection', product.id);
        }
      });
      $("#gridProdsInterest").jqGrid('footerData', 'set', { 'description': 'Total' });
      $("#gridProdsInterest").jqGrid('footerData', 'set', { 'price': sumAmoutPrice });
    }
  }).navGrid('#_pager', { add: false, edit: false, del: false });

  $("#gridProdsInterest").navButtonAdd("#_pager", {
    buttonicon: "ui-icon ui-icon-disk",
    title: "Save",
    caption: "",
    position: "last",
    onClickButton: function () {
      var ids = $('#gridProdsInterest').jqGrid('getGridParam', 'selarrrow');
      var cell_id = $('#gridLeads').jqGrid('getGridParam', 'selrow');
      var leadId = $('#gridLeads').jqGrid('getCell', cell_id, 'id');

      $.post('/api/product/interested', {
        ids: ids,
        leadId: leadId
      },
        function () {
          $("#gridProdsInterest").trigger("reloadGrid");
        });
    }
  })


}

function loadLeads() {
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

  init_jqGrid('gridLeads', 'pager', '/api/leads', '/api/lead/new', '/api/lead/edit',
    colModel, 'Leads Management', true, function (data) { leads_loadComplete(data) },
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

function cust_subGridRowExpanded(subgrid_id, id) {
  var subgrid_table_id = subgrid_id + "_address";
  var pager_id = "p_" + subgrid_table_id;
  $("#" + subgrid_id).html("<table id='" + subgrid_table_id + "'></table><div id='" + pager_id + "' class='scroll'></div>");
  $("#" + subgrid_table_id).jqGrid({
    url: `/api/customer/${id}/address`,
    editurl: `/api/customer/${id}/address/edit`,
    datatype: "json",
    colModel: [
      { name: 'id', key: true, hidden: true },
      { name: 'customerId', key: false, hidden: true },
      { name: 'addressLine1', label: 'Line 1', width: 180, editable: true, editrules: { required: true } },
      { name: 'addressLine2', label: 'Line 2', width: 180, editable: true },
      { name: 'addressType', label: 'Type', width: 75, editable: true },
      { name: 'city', label: 'City', width: 120, editable: true, editrules: { required: true } },
      { name: 'state', label: 'State', width: 120, editable: true },
      { name: 'country', label: 'Country', width: 100, editable: true, editrules: { required: true } },
      { name: 'postalCode', label: 'Zip code', width: 95, editable: true, editrules: { required: true } },
      { name: 'isPrimary', label: 'Primary', width: 70, editable: true, formatter: "checkbox", edittype: "checkbox", align: "center" }
    ],
    loadonce:true,
    pager: pager_id,
    multiselect: false,
    height: "100%",
    caption: "Customer Address"
  });

  $("#" + subgrid_table_id).navGrid("#" + pager_id,{ edit: false, add: false, del: false, search: false, refresh: false })

  $("#" + subgrid_table_id).jqGrid('inlineNav', "#" + pager_id, 
    {
      edit: true,
      add: true,
      del: true,
      cancel: true,
      save: true,
      editParams: {
        keys: true,
        url: `/api/customer/${id}/address/edit`,
        mtype: 'POST',
        aftersavefunc: function (rowid, response) {
          $("#" + subgrid_table_id).trigger("reloadGrid");
          $("#gridCustomers").trigger("reloadGrid");
        },
        errorfunc: function (rowid, response) {
          alert("Error saving address: " + response.responseText);
        }
      },
      addParams: {
        addRowParams: {
          keys: true,
          url: `/api/customer/${id}/address/new`,
          mtype: 'POST',
          aftersavefunc: function (rowid, response) {
            $("#" + subgrid_table_id).trigger("reloadGrid");
            $("#gridCustomers").trigger("reloadGrid");
          },
          errorfunc: function (rowid, response) {
            alert("Error saving address: " + response.responseText);
          }
        }
      }
    }
  )

  $("#" + subgrid_table_id).navButtonAdd("#" + pager_id, {
    buttonicon: "ui-icon ui-icon-trash",
    title: "Delete",
    caption: "",
    position: "last",
    onClickButton: function () {
      var cell_id = $("#" + subgrid_table_id).jqGrid('getGridParam', 'selrow');
      var addressId = $("#" + subgrid_table_id).jqGrid('getCell', cell_id, 'id');
      $.post('/api/customer/' + id + '/address/delete', {
        addressId: addressId
      }, function () {
        $("#" + subgrid_table_id).trigger("reloadGrid");
         console.log('Reloading parent grid....')   
        $("#gridCustomers").trigger("reloadGrid");
      });
    }
  })
}

function customer_loadComplete(datas, createUrl = null, editUrl = null) {
  fetch('/api/userRoles', {
    headers: {
      'Accept': 'application/json'
    }
  }).then(resp => resp.json()
  ).then(data => {
    $("#gridCustomers").navGrid("#pager",
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
        url: editUrl, //'/api/customer/edit',
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
        url: createUrl, //'/api/customer/new',
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

function user_loadComplete(data) {
  $("#gridUser").navGrid("#pager",
    { edit: false, add: false, del: false, search: false, refresh: true },
    {
      // edit options
      closeAfterEdit: true,
      recreateForm: true
    }
  );
}

var lastsel
function user_onSelectRow(id) {
  if (id) {
    jQuery('#gridUser').jqGrid('restoreRow', lastsel);
    jQuery('#gridUser').jqGrid('editRow', id, true);
    lastsel = id;
  }
}

function loadRoles() {
  var colModel = [
    {
      name: 'id',
      index: 'id',
      key: true,
      hidden: true
    },
    { label: 'Role', name: 'roleName', width: 150, editable: true },
    { label: 'Description', name: 'description', width: 100, editable: true },
    { label: 'Active', name: 'active', width: 70, editable: true, template: "booleanCheckbox" },
    { label: 'Date created', name: 'created_at', width: 100, editable: false, align: 'center', formatter: 'date' },
    { label: 'Date updated', name: 'updated_at', width: 100, editable: false, align: 'center', formatter: 'date' }
  ];
  init_jqGrid('gridRole', 'pager', '/api/roles', '/api/roles/create', '/api/roles/edit',
    colModel, 'Roles Management', true, function (data) { role_loadComplete(data) },
    function (id) { }, function (subgrid_id, id) { roles_subGridRowExpanded(subgrid_id, id) })
}

function role_loadComplete(data) {
  $("#gridRole").navGrid("#pager",
    { edit: true, add: true, del: false, search: false, refresh: true },
    {
      // Edit options
      url: '/api/roles/edit',
      closeAfterEdit: true,
      reloadAfterSubmit: true
    },
    {
      // Add options
      url: '/api/roles/create',
      closeAfterAdd: true,
      reloadAfterSubmit: true
    }
  );
}

function roles_subGridRowExpanded(subgrid_id, id) {
  var subgrid_table_id = subgrid_id + "_t";
  var pager_id = "p_" + subgrid_table_id;
  $("#" + subgrid_id).html("<table id='" + subgrid_table_id + "'></table><div id='" + pager_id + "' class='scroll'></div>");
  $("#" + subgrid_table_id).jqGrid({
    url: '/api/roles/' + id + '/assignment',
    datatype: "json",
    colModel: [
      { name: 'id', key: true, hidden: true },
      { name: 'fullname', label: 'User Name' },
      { name: 'email', label: 'Email' },
      {
        name: 'assigned',
        label: 'Assigned',
        formatter: "checkbox",
        edittype: "checkbox",
        align: "center"
      }
    ],
    pager: pager_id,
    multiselect: true,
    height: "100%",
    caption: "Users in Role",
    loadComplete: function (data) {
      let users = data;
      users.forEach((user, idx) => {
        if (user.assigned) {
          $("#" + subgrid_table_id).jqGrid('setSelection', user.id);
        }
      });
    }
  });

  $("#" + subgrid_table_id).navGrid("#" + pager_id, { edit: false, add: false, del: false, search: false, refresh: false })

  $("#" + subgrid_table_id).navButtonAdd("#" + pager_id, {
    buttonicon: "ui-icon-circle-plus",
    title: "Assign",
    caption: "Assign",
    position: "last",
    onClickButton: function () {
      var ids = $("#" + subgrid_table_id).jqGrid('getGridParam', 'selarrrow');
      $.post('/api/roles/' + id + '/assignment', {
        user_ids: ids
      }, function () {
        $("#" + subgrid_table_id).trigger("reloadGrid");
      });
    }
  });
}

function createAutoCorrectMailEvent() {
  return {
    type: 'blur',
    fn: function (e) {
      const input = $(e.target);
      const mail = input.val();
      Mailcheck.run({
        email: mail,
        suggested: function (suggestion) {
          input.val(suggestion.full);
        }
      });
    }
  };
}

function createAutoCorrectEvent() {
  return {
    type: 'blur',
    fn: function (e) {
      const input = $(e.target);
      const original = input.val();
      checkGrammar(original).then(result => {
        if (result.length > 0) {
          let idx = Math.floor(Math.random() * (result.length - 0 + 1)) + 0;
          const suggestion = result[idx].value;
          input.val(suggestion);
        }
      });
    }
  };
}

async function checkGrammar(text) {
  const res = await fetch("https://api.languagetool.org/v2/check", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    }
    ,
    body: new URLSearchParams({
      text: text,
      language: "en-US"
    })
  });

  const data = await res.json();
  if (data.matches.length > 0)
    return data.matches[0].replacements;

  return []
}
