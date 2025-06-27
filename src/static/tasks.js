var previousSelection = [];
function fetchSalePersons() {
  var sales = fetch('/sales', {
    headers: {
      'Accept': 'application/json'
    }
  }).then(resp => resp.json()
  ).then(data => {
    return data;
  });
  return sales;
}

function fetchCustomers(saleId) {
  var custs = fetch(`/tasks/leads/${saleId}`, {
    headers: {
      'Accept': 'application/json'
    }
  }).then(resp => resp.json()
  ).then(data => {
    let custOptions = "";
    data.forEach(item => {
      custOptions += item.id + ":" + item.name + ";";
    });
    custOptions = custOptions.slice(0, -1);
    return custOptions
  });
  return custs;
}

async function loadMyTasksGrid() {
  //var tasks = []
  let salePersons = await fetchSalePersons();
  let salesOptions = "";
  if (Array.isArray(salePersons)) {
    salePersons.forEach(item => {
      salesOptions += item.id + ":" + item.name + ";";
    });
    salesOptions = salesOptions.slice(0, -1);
  }

  $("#gridTasks").jqGrid({
    url: `/tasks`,
    editurl: '/tasks',
    datatype: "json",
    height: 400,
    colModel: [
      { name: 'id', index: 'id', key: true, hidden: true },
      { name: 'isNotify', index: 'isNotify', key: false, hidden: true },
      { label: 'Title', index: 'title', name: 'title', editable: true, width: 120 },
      { label: 'Description', index: 'description', name: 'description', editable: true, width: 150 },
      {
        label: 'Assigned To', index: 'assigned_to', name: 'assigned_to', width: 150, editable: true, edittype: 'select', editoptions: {
          value: salesOptions,
          dataInit: function (elem) {
            setTimeout(() => {
              $(elem).trigger('change');
            }, 0);
          },
          dataEvents: [
            {
              type: 'change',
              fn: function (e) {
                const selected = $(e.target).val();
                fetchCustomers(selected).then(custOptions => {
                  const $row = $(this).closest('tr');
                  $row.find("select[name='relatedTo_id']").empty();

                  custOptions.split(';').filter(Boolean).forEach(opt => {
                    const [val, text] = opt.split(':');
                    const $select = $row.find("select[name='relatedTo_id']");
                    if ($select.length) {
                      $select.append(new Option(text, val));
                    }
                  });
                });
              }
            },
            {
              // This event fires when the select is first created (before any change)
              type: 'focus',
              fn: function (e) {
                const selected = $(e.target).val();
                console.log(selected)
                // Only fire if this is the first focus and no previous selection
                if (!this._hasFocused) {
                  this._hasFocused = true;
                //   
                  fetchCustomers(selected).then(custOptions => {
                    const $row = $(this).closest('tr');
                    $row.find("select[name='relatedTo_id']").empty();

                    custOptions.split(';').filter(Boolean).forEach(opt => {
                      const [val, text] = opt.split(':');
                      const $select = $row.find("select[name='relatedTo_id']");
                      if ($select.length) {
                        $select.append(new Option(text, val));
                      }
                    });
                  });
                }
              }
            }
          ]
        }
      },
      {
        label: 'Due Date', index: 'due_date', name: 'due_date', width: 120, editable: true, editrules: { required: true, date: true }, datefmt: 'yyyy-mm-dd',
        editoptions: {
          dataInit: function (element) {
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
      { label: 'Priority', index: 'priority', name: 'priority', editable: true, width: 120, edittype: 'select', editoptions: { value: "High:High;Medium:Medium;Low:Low" } },
      { label: 'Related To', index: 'relatedTo_id', name: 'relatedTo_id', editable: true, width: 150, edittype: 'select', editoptions: { value: " : " } }
    ],
    loadonce: true,
    pager: "#pager",
    autowidth: true,
    multiselect: true,
    onSelectRow: function (id, status) {
        var currentSelection = $("#gridTasks").jqGrid("getGridParam", "selarrrow"); 
        var tasks = $("#gridTasks").jqGrid('getRowData');

        tasks.forEach(function(task) {
          if(!status && task.id == id && task.isNotify == 1){
            $.ajax({
              url: `/task/${id}`,
              type: 'PUT',
              contentType: 'application/json',
              data: JSON.stringify({}),
              success: function(response) {
                console.log(response);
                $("#gridTasks").trigger("reloadGrid")
              },
              error: function(error) {
                console.log(error);
              }
            });
          }

          // if (status && task.isNotify == 0){
          //   $('#'+  task.id ).removeClass('ui-state-highlight');
          // }
        })
        previousSelection = [...currentSelection];
    },
    loadComplete: function (tasks) {
      if (Array.isArray(tasks)){
          tasks.forEach((task, idx) => {
              if (task.isNotify) {
                  $("#gridTasks").jqGrid('setSelection', task.id);
                  $("#gridTasks tr#" + task.id +" input.cbox").prop("disabled", false);
              }else{
                  $("#gridTasks tr#" + task.id +" input.cbox").prop("disabled", true);
              }
          });
      }
    },
    gridComplete: function () {
    
    },
    caption: "Tasks"
  }).navGrid('#pager', { add: false, edit: false, del: false, search: false });

  $("#gridTasks").jqGrid('inlineNav', "#pager", {
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
        url: `/tasks`,
        mtype: 'POST',
        aftersavefunc: function (rowid, response) {
          let userId = response.responseJSON.assigned_to;
          subscribeUser(userId);
        },
        onSuccess: function (response) {
          var $self = $(this), p = $self.jqGrid("getGridParam");
          p.datatype = "json";
          $self.trigger("reloadGrid", { page: p.page, current: true });
          return [true, '']; // No error
        }
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

$.jgrid.jqModal = $.extend($.jgrid.jqModal || {}, {
  beforeOpen: centerInfoDialog
});

function centerInfoDialog() {
  var $infoDlg = $("#info_dialog");
  var $parentDiv = $infoDlg.parent();
  var dlgWidth = $infoDlg.width();
  var parentWidth = $parentDiv.width();
  var dlgHeight = $infoDlg.height();
  var parentHeight = $parentDiv.height();
  $infoDlg[0].style.top = Math.round((parentHeight - dlgHeight) / 2) + "px";
  $infoDlg[0].style.left = Math.round((parentWidth - dlgWidth) / 2) + "px";
}

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');

  // Remove any characters not valid in base64
  const cleanedBase64 = base64.replace(/[^A-Za-z0-9+/=]/g, '');

  const rawData = atob(cleanedBase64);
  return Uint8Array.from([...rawData].map(char => char.charCodeAt(0)));
}

async function subscribeUser(userId) {
  console.log(`SubscribeUser....${userId}`)
  // Register Service Worker
  const registration = await navigator.serviceWorker.register('/sw.js', { scope: '/' });

  // Ask for permission
  const permission = await Notification.requestPermission();
  if (permission !== 'granted') {
    alert('Notifications blocked!');
    return;
  }

  // Fetch public key using fetch API and await
  const env = await $.getJSON('/tasks/publicKey');
  const publicKey = env.publicKey;

  const applicationServerKey = urlBase64ToUint8Array(publicKey);
  const subscription = await registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: applicationServerKey // must be a Uint8Array
  });

  // Send subscription to backend
  await fetch('/tasks/subscription', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      subscription_json: JSON.stringify(subscription)
    })
  });

 // alert('✅ Subscribed to notifications!');
}