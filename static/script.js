$(document).ready(function() {
  var currentActiveElement = "";
  getActiveElement();

  function setActiveElement(uiElement) {
    $.ajax({
      type: "GET",
      url: $SCRIPT_ROOT + "/_setActiveElement",
      contentType: "application/json; charset=utf-8",
      data: { activeElement: uiElement }
      });
  };
  function updateActiveElement(uiElement) {
    $('#' + currentActiveElement).removeClass("active");
    $('#' + uiElement).addClass("active");
    currentActiveElement = uiElement;
  };
  function getActiveElement() {
    $.ajax({
      type: "GET",
      url: $SCRIPT_ROOT + "/_getActiveElement",
      contentType: "application/json; charset=utf-8",
      success: function(data) {
        updateActiveElement(data.value);
      }
    });
  };
  $('.mode').click(function() {
    setActiveElement(this.id);
    updateActiveElement(this.id);
  });

  $('#picker').onload(function() {
       $.ajax({
          type: "GET",
          url: $SCRIPT_ROOT + "/_getSetColor",
          contentType: "application/json; charset=utf-8",
          data: {},
          success: function(data) {
            this.setColor(data.value);
          }
      });
  });
  $('#picker').farbtastic(function (color) {
       $.ajax({
          type: "GET",
          url: $SCRIPT_ROOT + "/_setColor",
          contentType: "application/json; charset=utf-8",
          data: { color: color, mode: colorMode },
          success: function(data) {
            $('#status').text(data.value);
          }
      });
  });
  $('.mode-choose-color').click(function() {
    colorMode = this.id;
  });
});
