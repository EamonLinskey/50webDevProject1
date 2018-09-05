console.log("hi")
$(".nav .nav-link").on("hover", function(){
   $(".nav").find(".active").removeClass("active");
   $(this).addClass("active");
});