
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
      subGrid:  true,
    subGridRowExpanded: function (subgrid_id, row_id) {
      var cell_id = $('#gridLeads').jqGrid('getGridParam', 'selrow');
      var leadId = $('#gridLeads').jqGrid('getCell', cell_id, 'id');
      var productId =  row_id;

      var subgrid_table_id = subgrid_id + "_activities";
      var pager_id = "p_" + subgrid_table_id;
      $("#" + subgrid_id).html("<table id='" + subgrid_table_id + "' class='scroll' style='width:100%;'></table><div id='" + pager_id + "' class='scroll' style='width:100%;'></div>");
      $("#" + subgrid_table_id).jqGrid({
        url: `/${leadId}/interactions/${row_id}`,
        datatype: "json",
        mtype: 'GET',
        colModel: [
          { name: 'id', hidden: true, key: true },
          { name: 'customer_id', hidden: true, key: false },
          { name: 'product_id', hidden: true, key: false },
          { name: 'interaction_type', label: 'Contact via', width: 30 ,align: "center",editable: true,edittype:"select"
            ,editoptions:{value:"Email:Email;Phone:Phone;Other:Other"} },
          { name: 'notes', label: 'Note', width: 180 ,editable: true, editrules: { required: true } , edittype:"textarea" },
          { name: 'date_activity', label: 'Date contact', width: 60, align: "center",formatter: 'date', formatoptions: { newformat: 'd-m-YYYY H:i:s' } },
        ],
        autowidth: true,
        rownumbers: true,
        width: '100%',
        pager: pager_id,
        sortname: 'date_activity',
        sortorder: "asc",
        caption: "Interactions",
        loadonce: true, 
      
      }).navGrid('#' + pager_id, { add: false, edit: false, del: false, search: false });

      $("#" + subgrid_table_id).jqGrid('inlineNav', "#" + pager_id, {
        edit: false,
        add: true,
        del: false,
        cancel: true,
        save: true,
        addParams: {
          addRowPage: 'last', // Add the new row to the last page (or 'first', 'current')
          position: 'last',   // Position the new row at the end of the grid (or 'first')
          addRowParams: {
            keys: true,
            url: `${leadId}/interactions/${productId}`,
            mtype: 'POST',
            onSuccess: function (response) {
              var $self = $(this), p = $self.jqGrid("getGridParam");
              p.datatype = "json";
              $self.trigger("reloadGrid", { page: p.page, current: true });
              return [true, '']; // No error
            }
          },
          // editParams: {
          //   url: `/api/${leadId}/opportunities/edit`,
          //   keys: true,
          //   mtype: 'POST',
          //   onSuccess: function (response) {
          //     var $self = $(this), p = $self.jqGrid("getGridParam");
          //     p.datatype = "json";
          //     $self.trigger("reloadGrid", { page: p.page, current: true });
          //     return [true, '']; // No error
          //   },
          // },
          // This callback fires AFTER the new empty row is inserted and put into edit mode.
          // addRowCallback: function (rowid, response) {
          //   // Find the input field for 'closure_date' in the newly added row
          //   var closureDateInput = $('#' + rowid + '_closure_date');
          //   if (closureDateInput.length) {
          //     // Initialize the Datepicker on this specific input
          //     closureDateInput.datepicker({
          //       dateFormat: 'yy-mm-dd',
          //       showOn: 'focus',
          //       changeMonth: true,
          //       changeYear: true
          //     });
          //   }
          // },
        },
      })
    },
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
          var url = window.location.href;
          const match = url.match(/\/customers\/([0-9a-fA-F-]{36})?/);

          $("#gridProdsInterest").trigger("reloadGrid");
          const custId = match ? match[1] : null;
          if (custId)
             window.location.href = `/${custId}/order/`;
        });
    }
  })
}

$.jgrid.jqModal = $.extend($.jgrid.jqModal || {}, {
    beforeOpen: centerInfoDialog
});	

function centerInfoDialog()
{
    var $infoDlg = $("#info_dialog");
    var $parentDiv = $infoDlg.parent();
    var dlgWidth = $infoDlg.width();
    var parentWidth = $parentDiv.width();
    var dlgHeight = $infoDlg.height();
    var parentHeight = $parentDiv.height();
    $infoDlg[0].style.top = Math.round((parentHeight - dlgHeight) / 2) + "px";
    $infoDlg[0].style.left = Math.round((parentWidth - dlgWidth) / 2) + "px";
}