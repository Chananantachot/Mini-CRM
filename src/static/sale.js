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
            { label: 'Active', name: 'active', width: 100, align: 'center', template: "booleanCheckbox"  }
        ],
        viewrecords: true,
        autowidth: true,
        height: 'auto',
        rowNum: 100,
        pager: "#pager",
        caption: "Sales Data",
        editurl: "/sales",
        loadonce: true,
        subGrid: true,
        subGridRowExpanded: function(subgrid_id, row_id) {
            var subgrid_table_id = subgrid_id + "_leads";
            var pager_id = "p_" + subgrid_table_id;

            $("#" + subgrid_id).html("<table id='" + subgrid_table_id + "'></table><div id='" + pager_id + "' class='scroll'></div>");
            $("#" + subgrid_table_id).jqGrid({
                url: `/sale/${row_id}/leads`,
                datatype: "json",
                mtype: 'GET',
                colModel: [
                    { label: 'id', name: 'id', key: true, hidden: true },
                    { label: 'salesPersonId', name: 'salesPersonId', key: false, hidden: true },
                    { label: 'Name', name: 'name', width: 250 },
                    { label: 'Email', name: 'email', width: 200 },
                    { label: 'mobile', name: 'mobile', width: 100 }
                ],
                multiselect: true,
                loadonce: true,
                //autowidth: true,
                height: 250,
                rowNum: 20,
                pager: '#'+ pager_id,
                caption: "My Leads",
                loadComplete: function (data) {
                    let leads = data;
                    console.log(leads)
                    if (Array.isArray(leads)){
                        leads.forEach((lead, idx) => {
                            if (lead.isMyLead) {
                                $("#" + subgrid_table_id).jqGrid('setSelection', lead.id);
                            }
                        });
                    }
              
                }
            });
            $("#" + subgrid_table_id).jqGrid('navGrid', '#' + pager_id, { edit: false, add: false, del: false, search: true, refresh: true });
            $("#" + subgrid_table_id).navButtonAdd("#" + pager_id, {
                buttonicon: "ui-icon-circle-plus",
                title: "Save My Leads",
                caption: "",
                position: "last",
                onClickButton: function () {
                var ids = $("#" + subgrid_table_id).jqGrid('getGridParam', 'selarrrow');
                $.post(`/sale/${row_id}/leads`, {
                    ids: ids
                }, function () {
                    $("#" + subgrid_table_id).trigger("reloadGrid");
                });
                }
            });
        }
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