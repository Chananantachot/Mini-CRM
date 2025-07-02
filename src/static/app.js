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
    loadonce: true,
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
// document.getElementById("notif-allow-btn").addEventListener("click", () => {
//   Notification.requestPermission().then(permission => {
//     if (permission === "granted") {
//       // Optionally show a welcome notification
//       new Notification("You're in! We’ll keep you posted. ✅");
//       $('#notif-banner').hide();
//       //document.getElementById("notif-banner").style.display = "none";
//     } else {
//       $('#notif-banner').show();
//       // Optional fallback or message
//      // alert("No problem! You can enable notifications anytime.");
//     }
//   });
// });

const socket = io();
let peerConnection;
let localStream;

window.dataLayer = window.dataLayer || [];

function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());

fetch('/GAMEASUREMENTID',{
  headers: {
    'Accept': 'application/json'
  }
}).then(resp => resp.json()
).then(data => {
  gtag('config', data.GAID);
});

const config = {
  iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
};

function answerCall(room){
  socket.emit('join', { room });
  setupCall(room);
}

function endCall(room) {
  gtag('event', 'call_ended', {'method': 'VoIP'});
  socket.emit('leave', { room });      // Notify others you've left the room
  teardownCall();                  // Clean up media streams, UI changes
}

function declineCall(room) {
  gtag('event', 'call_decline', {'method': 'VoIP'});
  socket.emit('decline', { room });    // Custom event to notify caller
  teardownCall();                  // Optional cleanup if needed
}

function teardownCall() {
    if (peerConnection) {
      peerConnection.close();
      peerConnection = null;
    }

    if (localStream) {
      localStream.getTracks().forEach(track => track.stop());
      localStream = null;
    }

    // Stop and remove any dynamically created audio elements
    document.querySelectorAll('audio').forEach(audio => {
      audio.pause();
      audio.srcObject = null;
      audio.remove();
    });
     
}

async function startCall(room){
  gtag('event', 'call_started', {'method': 'VoIP'});
  await subscribeUser(room);
  await fetch(`/call/notification/${room}`);
  fetch('/start_call', {
      method: "POST",
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ lead_id: room })
    }).then(res => {
      if (res.ok) {
        socket.emit('join', { room });
        setupCall(room);
      } else {
       // alert("Someone is already calling this lead.");
      }
  });
}

function setupCall(room) {
  teardownCall(); // 💥 Clean up previous call

  navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
    localStream = stream;
    peerConnection = new RTCPeerConnection(config);

    stream.getTracks().forEach(track => peerConnection.addTrack(track, stream));

    peerConnection.onicecandidate = e => {
      if (e.candidate) socket.emit('signal', { type: 'ice', data: e.candidate, room });
    };

    peerConnection.ontrack = e => {
      const audio = new Audio();
      audio.srcObject = e.streams[0];
      audio.play();
    };

    peerConnection.createOffer().then(offer => {
      peerConnection.setLocalDescription(offer);
      socket.emit('signal', { type: 'offer', data: offer, room });
    });
  });
}

socket.on('signal', async ({ type, data, room }) => {
  if (type === 'offer') {
    const accept = confirm('Incoming call. Accept and end current call?');
    if (!accept) {
      socket.emit('decline', { room });
      return;
    }

    teardownCall(); // 📞 Accepting a new call, so teardown any current call

    peerConnection = new RTCPeerConnection(config);
    peerConnection.onicecandidate = e => {
      if (e.candidate) socket.emit('signal', { type: 'ice', data: e.candidate, room });
    };
    peerConnection.ontrack = e => {
      const audio = new Audio();
      audio.srcObject = e.streams[0];
      audio.play();
    };

    await peerConnection.setRemoteDescription(new RTCSessionDescription(data));
    localStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));

    const answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);
    socket.emit('signal', { type: 'answer', data: answer, room });

  } else if (type === 'answer') {
    if (peerConnection) {
      await peerConnection.setRemoteDescription(new RTCSessionDescription(data));
    }
  } else if (type === 'ice') {
    if (peerConnection) {
      peerConnection.addIceCandidate(new RTCIceCandidate(data));
    }
  }
});

socket.on('lead:locked', ({ lead_id, rep_name }) => {
  $('#btnCall').hide()
});

socket.on('lead:released', ({ lead_id }) => {
    $('#btnCall').show()
});

async function subscribeUser(userId) {
  // Register Service Worker
  const registration = await navigator.serviceWorker.register('/sw.js', { scope: '/' });
  // Fetch public key using fetch API and await
  const env = await $.getJSON('/tasks/publicKey');
  const publicKey = env.publicKey;

  const applicationServerKey = urlBase64ToUint8Array(publicKey);
  let s = await registration.pushManager.getSubscription();
  if (s) {
    await s.unsubscribe();
    s = null;
  }

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
}

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');

  // Remove any characters not valid in base64
  const cleanedBase64 = base64.replace(/[^A-Za-z0-9+/=]/g, '');

  const rawData = atob(cleanedBase64);
  return Uint8Array.from([...rawData].map(char => char.charCodeAt(0)));
}

function isSafari() {
  return /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
}
