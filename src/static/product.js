
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