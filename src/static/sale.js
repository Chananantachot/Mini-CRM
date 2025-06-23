function loadSalesGrid()
{
    $("#gridSales").jqGrid({ 
        url: '/sales',
        datatype: "json",
        mtype: 'GET',
        colModel: [
            { label: 'id', name: 'id', key: true, hidden: true },
            { label: 'Name', name: 'name', editable: true, width: 200 },
            { label: 'Email', name: 'email', editable: true, width: 100,  },
            { label: 'Mobile', name: 'phone', editable: true, width: 100, },
            { label: 'Active', name: 'active', width: 100, align: 'center' }
        ],
        viewrecords: true,
        autowidth: true,
        height: 'auto',
        shrinkToFit: true,
        rowNum: 100,
        pager: "#pager",
        caption: "Sales Data",
        editurl: "/sales"
    });
    $("#gridSales").jqGrid('navGrid', '#pager', { edit: true, add: true, del: false, search: true, refresh: true },
        {
            // Edit options
            mtype: 'PUT',
            url: '/sales',
            afterSubmit: function(response, postdata) {
                var data = JSON.parse(response.responseText);
                if (data.success) {
                    return [true, "", data.id];
                } else {
                    return [false, data.message];
                }
            }
        },
        {
            // Add options
            mtype: 'POST',
            url: '/sales',
            afterSubmit: function(response, postdata) {
                var data = JSON.parse(response.responseText);
                if (data.success) {
                    return [true, "", data.id];
                } else {
                    return [false, data.message];
                }
            }
        },
        {
            // Search options
            multipleSearch: true,
            closeAfterSearch: true
        }
    ); 
}