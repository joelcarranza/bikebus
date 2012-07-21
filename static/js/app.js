function updateTimeField() {
  if($('#timemode').val() == 'now') {
    $('#time').hide();
  }
  else {
    $('#time').show();
  }
}

$(document).ready(function() {
  if($('.details').length > 1) {
    $('.details').hide();
  }
  $(".leg-header").click(function() {
    $('.details',this.parentNode).toggle();
  });
  $("#edit-link").click(function(event) {
    $("#prompt").show();
    $("#result-head").hide();
    event.preventDefault();
  })
  $("#timemode").change(function() {
    updateTimeField();
  })
  updateTimeField()
});
