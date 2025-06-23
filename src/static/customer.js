function loadCustomers() {
  const colModel = [
    {
      name: 'id',
      index: 'id',
      key: true,
      hidden: true
    },
    { label: 'Frist Name', name: 'firstName', width: 150, editable: false, editrules: { required: true }, editoptions: { dataEvents: [createAutoCorrectEvent()] } },
    { label: 'Last Name', name: 'lastName', width: 150, editable: false, editrules: { required: true }, editoptions: { dataEvents: [createAutoCorrectEvent()] } },
    { label: 'Email', name: 'email', width: 120, editable: false, editrules: { required: true }, editoptions: { dataEvents: [createAutoCorrectMailEvent()] } },
    { label: 'Mobile', name: 'mobile', width: 100, editable: false, editrules: { required: true }, editoptions: { dataEvents: [createAutoCorrectEvent()] } },
    { label: 'Date created', name: 'created_at', width: 100, editable: false, align: 'center', formatter: 'date' },
    { label: 'Date updated', name: 'updated_at', width: 100, editable: false, align: 'center', formatter: 'date' }
  ];

  init_jqGrid('gridCustomers', 'pager', '/api/customers', '/api/customer/new', '/api/customer/edit',
    colModel, 'Customers', true, function (data) { customer_loadComplete(data, '/api/customer/new', '/api/customer/edit') },
    function (id) { loadCustOrders(id) }, function (subgrid_id, id) { cust_subGridRowExpanded(subgrid_id, id) })
}

var lastsel;
function loadCustOrders(custId) {
 $("#gridOrders").jqGrid({
    url: `/invoice/${custId}/orderDetails`,
    datatype: "json",
    height: 200,
    cellEdit: true,
    colModel: [
      {
        name: 'orderId',
        index: 'orderId',
        key: true,
        hidden: true
      },
      { label: 'Invoice NO.', index: 'invNumber', name: 'invNumber', width: 80 , align: "center", formatter: function (cellvalue, options, rowObject) {  
        return `<a class='btn btn-link' href='/${custId}/order/${rowObject.orderId}'>${rowObject.invNumber}</a>`;``
      }},
      { label: 'Date Order', index: 'orderDate', name: 'orderDate', width: 80, align: "center" ,formatter: "date"},
      { label: 'Total', index:'total', name: 'total', width: 60, editable: true ,formatter: "number",align: "right"},   		
      { name: 'status', label: "Status", index: 'status', width: 60, align: "center" ,editable: true,edittype:"select"
        ,editoptions:{value:"Pending:Pending;Completed:Completed;Cancelled:Cancelled"}}
    ],
    loadonce: true,
    pager: "#ordersPager",
    autowidth: true,
    viewrecords: true,
    caption: "Invoices",
    onSelectRow: function (id) {
    	if (id) {
        jQuery('#ordersPager').jqGrid('restoreRow', lastsel);
        jQuery('#ordersPager').jqGrid('editRow', id, true);
			  lastsel = id;
      	}
    },
    afterSaveCell: function(rowid, name, value, iRow, iCol) {
        var orderId = $('#gridOrders').jqGrid('getCell', rowid, 'orderId');
        $.ajax({
          url: `/invoice/${orderId}/updateOrderStatus`,
          type: 'PUT',
          contentType: 'application/json',
          data: JSON.stringify({
            "status": value
          }),
          success: function(response) {
            console.log("Order status updated successfully");
            $("#gridOrders").trigger("reloadGrid");
          },
          error: function(error) {
            console.log(error);
          }
			});
    }
  }).navGrid('#ordersPager', { add: false, edit: false, del: false, search: false });

    $("#gridOrders").navButtonAdd("#ordersPager" , {
      buttonicon: "ui-icon ui-icon-plus",
      title: "Create Invoice",
      caption: "",
      position: "last",
      onClickButton: function () {
        var cell_id = $('#gridCustomers').jqGrid('getGridParam', 'selrow');
        var customerId = $('#gridCustomers').jqGrid('getCell', cell_id, 'id');
    
        fetch(`/check/${customerId}/orderLeft`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
        }).then(resp => resp.json())
        .then(data => {
          //THis check if the customer has any order left to create (when the customer has first convert form leads)
          if (data && data.orderLeft  == 0) {
            console.log('Customer has no order left to create');
            window.location.href = `/customers/${customerId}`;
          } else {
            console.log('Customer has order left to create');
            window.location.href = `/${customerId}/order/`;
          }
        });
      }
    });
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
      { name: 'addressType', label: 'Type', width: 75, editable: true ,edittype:"select",editoptions:{value:"Billing:Billing;Shipping:Shipping;Work:Work;Home:Home"} },
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
        edit: false,
        add: false, //data.isAdminRole,
        del: false,
        search: true,
        refresh: true,
        view: false,
        position: "left",
        cloneToTop: false
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