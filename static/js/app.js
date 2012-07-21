function updateTimeField() {
  if($('#timemode').val() == 'now') {
    $('#time').hide();
  }
  else {
    $('#time').show();
  }
}

function swapFromTo() {
  var fromv = $("#from-input").val();
  var tov = $("#to-input").val();
  $("#from-input").val(tov);
  $("#to-input").val(fromv);
}

$(document).ready(function() {
  if($('.details').length > 1) {
    $('.details').hide();
  }
  $(".leg-header").click(function() {
    $('.details',this.parentNode).toggle();
  });
  $("#action-swap").click(function(event) {
    swapFromTo();
    event.preventDefault();
  });
  $("#edit-link").click(function(event) {
    $("#prompt").show();
    $("#result-head").hide();
    event.preventDefault();
  });
  $("#timemode").change(function() {
    updateTimeField();
  });
  updateTimeField();
});
