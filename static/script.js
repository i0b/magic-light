$(document).ready(function() {
  var currentActiveElement = "";
  getState();

  function updateActiveElement(uiElement) {
    $('#' + currentActiveElement).removeClass("active");
    $('#' + uiElement).addClass("active");
    currentActiveElement = uiElement;
  };
  function setState(element, color) {
    $.post($SCRIPT_ROOT + "/_state", { element: element, color: color })
    .done(function(data) {
      $('#status').text(data.value);
    });
  };
  function getState() {
    $.get($SCRIPT_ROOT + "/_state", function(data) {
      updateActiveElement(data.element);
    });
  };
  function updateMagicLight(mode, color) {
    $.post($SCRIPT_ROOT + "/_mode", { color: color, mode: mode })
    .done(function(data) {
      $('#status').text(data.value);
    });
  };
  $('.mode').click(function() {
    var splitComponents=this.id.split('-');
    var mode=splitComponents[0];
    var color=splitComponents[1];
    updateMagicLight(mode, color);

    setState(this.id, color);
    updateActiveElement(this.id);
  });
  $('#picker').ready(function() {
    getState();
    this.setColor(data.value);
  });
  $('#picker').farbtastic(function (color) {
    updateMagicLight(colorMode, color);
  });
  $('.mode-choose-color').click(function() {
    colorMode = this.id;
  });
});
