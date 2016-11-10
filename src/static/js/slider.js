$(document).ready(function() {

      $("#owl-demo").owlCarousel({
        items : 5,
		autoPlay: 2500
      });

      $('.link').on('click', function(event){
        var $this = $(this);
        if($this.hasClass('clicked')){
          $this.removeAttr('style').removeClass('clicked');
        } else{
          $this.css('background','#7fc242').addClass('clicked');
        }
      });
	  
		// Custom Navigation Events
		
			var owl = $("#owl-demo");
		  $(".next").click(function(){
			owl.trigger('owl.next');
		  })
		  $(".prev").click(function(){
			owl.trigger('owl.prev');
		  })
		  


    });