$(document).ready(function() {
  var socket = io.connect('http://' + document.domain + ':' + location.port + '/socketio');
  var currentActiveElement = "";
  var otherColorData = {};

  $('.power-toggle-switch').bootstrapSwitch('state', false);

  function setElement(element) {
    $('#' + currentActiveElement).removeClass("active");
    $('#' + element).addClass("active");
    currentActiveElement = element;
  }

  function setRelays(relayStates) {
    for (var relay in relayStates) {
      if (relayStates[relay] == 'on') {
        $('#uplight-power-checkbox').bootstrapSwitch('state', true);
      }
      else if (relayStates[relay] == 'off') {
        $('#uplight-power-checkbox').bootstrapSwitch('state', false);
      }
    }
  }

  socket.on('setSensorValues', function(message) {
    message.forEach(function(sensorValue) {
      switch (sensorValue['sensorType']) {
        case 23:
          $('#sensor-light').text("Light: " + sensorValue['sensorValue'] + "%");
          break;
        case 0:
          $('#sensor-temperature').text("Temperature: " + sensorValue['sensorValue'] + "°C");
          break;
        case 1:
          $('#sensor-humidity').text("Humidity: " + sensorValue['sensorValue'] + "%");
          break;
      }
    });
  });

  socket.on('setUi', function(message) {
    otherColorData.color = message.color;
    setElement(message.element);
    setRelays(message.relays);
  });

  $('.all-off').click(function() {
    // turn off relay
    data = {};
    data.element  = "uplight-power";
    data.mode     = "power";
    data.relay    = "uplight";
    data.state    = "off";
    socket.emit('update', data, namespace='/socketio');
    //$('#uplight-power-checkbox').bootstrapSwitch('state', false);
    
    // turn of neopixel
    var data = {};
    data.element  = "staticColor-000000";
    data.mode     = "staticColor";
    data.color    = "000000";
    socket.emit('update', data, namespace='/socketio');
  });

  $('.pins').click(function() {
    var data = {};
    var splitComponents=this.id.split('-');
    data.element = this.id;
    data.mode     = splitComponents[0];
    data.pin      = splitComponents[1];
    data.pinValue = splitComponents[2];
    socket.emit('update', data, namespace='/socketio');
  });

  $('.power').click(function() {
    var element = this.id.split('-')[0];
    $('#'+element+'-power-checkbox').bootstrapSwitch('toggleState');
  });

  $('.power-toggle-switch').on('switchChange.bootstrapSwitch', function (event, state) {
    data = {}
    data.element = this.id;
    data.mode = "power";
    data.relay = this.id.split('-')[0];
    if (state == true) {
      data.state = "on";
    }
    else {
      data.state = "off";
    }

    socket.emit('update', data, namespace='/socketio');
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
  $('#btn-set-color').click(function() {
    socket.emit('update', otherColorData, namespace='/socketio');
  });
  $('#picker').farbtastic(function (color) {
    if (color.charAt(0) === '#') {
      color = color.substr(1);
    }
    otherColorData.color = color;
  });
  $('.mode-choose-color').click(function() {
    var picker = $.farbtastic('#picker');
    if (typeof otherColorData.color !== 'undefined' && /^[0-9A-F]{6}$/i.test(otherColorData.color)) {
      picker.setColor("#" + otherColorData.color);
    }
    otherColorData.element = this.id;
    otherColorData.mode = this.id;
  });
});
