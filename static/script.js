$(document).ready(function() {
  var socket = io.connect('http://' + document.domain + ':' + location.port + '/socketio');
  var currentActiveElement = "";

  socket.on('setUi', function(message) {
    $('#' + currentActiveElement).removeClass("active");
    $('#' + message.element).addClass("active");
    currentActiveElement = message.element;
  });

  function setState(element, color) {
    $.post($SCRIPT_ROOT + "/_state", { element: element, color: color })
    .done(function(data) {
      $('#status').text(data.value);
    });
  };
  function updateMagicLight(mode, color) {
    $.post($SCRIPT_ROOT + "/_mode", )
    .done(function(data) {
      $('#status').text(data.value);
    });
  };
  $('.mode').click(function() {
    var splitComponents=this.id.split('-');
    var mode=splitComponents[0];
    var color=splitComponents[1];
    { color: color, mode: mode }
    socket.emit('my event', {data: $('#emit_data').val()});

    setState(this.id, color);
  });
  $('#picker').ready(function() {
    this.setColor(data.value);
  });
  $('#picker').farbtastic(function (color) {
    updateMagicLight(colorMode, color);
  });
  $('.mode-choose-color').click(function() {
    colorMode = this.id;
  });
});
