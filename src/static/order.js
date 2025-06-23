 "use strict";
	var lastsel
	var datas;
	var order;
	var url = window.location.href;
	const match = url.match(/\/([0-9a-fA-F-]{36})(?:\/order\/([0-9a-fA-F-]{36}))?/);

	const custId = match ? match[1] : null;
	const orderId = match ? match[2] : null;
	url = `/invoice/${custId}/order`;
	if (orderId)
		url = `/invoice/${custId}/order/${orderId}`;

    fetch(url, {
		headers: {
		'Accept': 'application/json'
		}
	}).then(resp => resp.json()
	).then(data => {
		
		order = data[0]
		$("#invoice").tmpl(data).appendTo("#container");
	});

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

loadOrderItems(custId,orderId)
function loadOrderItems(custId,orderId) {
  var url = `/invoice/${custId}/orderItems`;
  if (orderId) {
	url = `/invoice/${custId}/orderItems/${orderId}`;
  }

  $("#gridInvoice").jqGrid({
    url: url,
    datatype: "json",
    height: 200,
    colModel: [
      {
        name: 'productId',
        index: 'productId',
        key: true,
        hidden: true
      },
      { label: 'Name', index: 'productName', name: 'productName', width: 120},
      { label: 'Description', index: 'description', name: 'description', width: 150 },
      { label: 'Quantity', index:'quantity', name: 'quantity', width: 60, editable: true ,formatter: "number",align: "right" ,
	  		editrules: {custom: true,
				custom_func: function (value, colName) {
					if (value === "") {
						return [false, "Quantity cannot be empty"];
					}
					if (isNaN(value)) {
						return [false, "Quantity must be a number"];
					}

					value = parseFloat(value);
					
					if (value <= 0) {
						return [false, "Quantity cannot be negative or zero"];
					}
					return [true, ""];
				}}},   		
      { name: 'unitPrice', label: "Price", index: 'unitPrice', width: 60, align: "right", sorttype: "float", formatter: "number", summaryType: 'sum' }
    ],
    loadonce: true,
    pager: "#orderPager",
    autowidth: true,
    viewrecords: true,
    sortname: 'unitPrice',
    searching: {
      searchOnEnter: true,
      defaultSearch: "bw"
    },
	cellEdit: true,
    afterSaveCell: function(rowid, name, value, iRow, iCol) {
        var allData = $("#gridInvoice").jqGrid('getRowData');
        var editedRows = $("#gridInvoice").jqGrid('getGridParam', 'savedRow');

        // Merge changes
        editedRows.forEach(function(edit) {
            var rowIndex = allData.findIndex(row => row.id === edit.id);
            if (rowIndex !== -1) {
                allData[rowIndex] = {...allData[rowIndex], ...edit};
            }
        });
		var amount = 0;
		var vat = 0;
		var total = 0;
		allData.forEach(function(product, idx) {
			amount += (parseInt(product.quantity) * parseFloat(product.unitPrice));
		})
		vat = amount * 0.07;
		total = amount + vat;
		$('#amount').val(amount.toFixed(2));
		$('#tax').val(vat.toFixed(2));	
		$('#total').val(total.toFixed(2));

		if (orderId){
			var orderItems = allData;
			order['amount'] = amount.toFixed(2)
			order['tax'] = vat.toFixed(2)
			order['total'] = total.toFixed(2)
			order['status'] ='Pending'
			$.ajax({
				url: '/invoice',
				type: 'PUT',
				contentType: 'application/json',
				data: JSON.stringify({
					"order": order,
					"orderItems": orderItems
				}),
				success: function(response) {
					console.log(response);
					orderId = response.id;
					order.orderId = orderId
				},
				error: function(error) {
					console.log(error);
				}
			});
		}
    },
	onSelectRow: function (id) {
    	if (id) {
			jQuery('#gridInvoice').jqGrid('restoreRow', lastsel);
			jQuery('#gridInvoice').jqGrid('editRow', id, true);
			lastsel = id;
      	}
    },
	loadComplete: function(invoiceData) {
		datas = invoiceData;
	 },
	 gridComplete: function() {
        var allData = $("#gridInvoice").jqGrid('getRowData');
		if (allData.length == 0)
			allData = datas;
	
        var editedRows = $("#gridInvoice").jqGrid('getGridParam', 'savedRow');

        // Merge changes
        editedRows.forEach(function(edit) {
            var rowIndex = allData.findIndex(row => row.id === edit.id);
            if (rowIndex !== -1) {
                allData[rowIndex] = {...allData[rowIndex], ...edit};
            }
        });

		var currentDate = new Date();
		if (order.orderDate){
			currentDate = new Date(order.orderDate);
		}
	
		var formattedDate = currentDate.toISOString().split('T')[0];
		$('#orderDate').val(formattedDate)

		var amount = order.amount;
		var vat = order.tax;
		var total = order.total;
		if (amount == 0 && vat == 0 && total == 0){
			allData.forEach(function(product, idx) {
				amount += (parseFloat(product.quantity) * parseFloat(product.unitPrice));
			})
			vat = amount * 0.07;
			total = amount + vat;
		}

		$('#amount').val(amount.toFixed(2));
		$('#tax').val(vat.toFixed(2));	
		$('#total').val(total.toFixed(2));

		order['amount'] = amount.toFixed(2)
		order['tax'] = vat.toFixed(2)
		order['total'] = total.toFixed(2)
		order['status'] ='Pending'

		if (orderId == null){
			var orderItems = allData;
			$.ajax({
				url: '/invoice',
				type: 'POST',
				contentType: 'application/json',
				data: JSON.stringify({
					"order": order,
					"orderItems": orderItems
				}),
				success: function(response) {
					orderId =  response.id;
					window.history.pushState({}, '', `/invoice/${custId}/order/${orderId}`);
				},
				error: function(error) {
					console.log(error);
				}
			});
		}
    },
    caption: "Order Items"
  }).navGrid('#orderPager', { add: false, edit: false, del: false, search: false });
}