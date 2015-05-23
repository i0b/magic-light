$(document).ready(function() {
  var socket = io.connect('http://' + document.domain + ':' + location.port + '/socketio');
  var currentActiveElement = "";

  socket.on('setUi', function(message) {
    $('#' + currentActiveElement).removeClass("active");
    $('#' + message.element).addClass("active");
    currentActiveElement = message.element;
  });

  $('.mode').click(function() {
    var data = {};
    var splitComponents=this.id.split('-');
    data.element = this.id;
    data.mode    = splitComponents[0];
    if (typeof splitComponents[1] !== 'undefined') {
      data.color = splitComponents[1];
    }
    socket.emit('update', data, namespace='/socketio');
  });
  $('#picker').ready(function() {
  });
  $('#picker').farbtastic(function (color) {
    socket.emit('update', { color: color, mode: colorMode, element: "none" });
  });
  $('.mode-choose-color').click(function() {
    colorMode = this.id;
  });
});
