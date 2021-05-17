var modalImg = $("#modalImg")[0]
var captionText = $("#caption")[0]
var modal = $("#modalOverlay")[0]

function fillModal(){
  modal.style.display = "block";
  modalImg.src = this.src;
  captionText.innerHTML = this.alt;
}

$("#serviceScreenshot1").click(fillModal)
$("#serviceScreenshot2").click(fillModal)
$("#serviceScreenshot3").click(fillModal)
$("#workflow").click(fillModal)

$(".modalClose").click(function() {
modal.style.display = "none";
})
