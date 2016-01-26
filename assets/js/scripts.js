// hljs
$(document).ready(function() {
  $('pre code').each(function(i, block) {
    hljs.highlightBlock(block);
    $(this).parent().css("word-wrap", "normal");
    $(this).css("white-space", "pre");
  });
});

// scrollspy
$('body').scrollspy({ target: '#sidebar-col' })

// lightbox
$(document).delegate('*[data-toggle="lightbox"]', 'click', function(event) {
    event.preventDefault();
    $(this).ekkoLightbox();
});

// make sidebar sticky when it hits the top of the viewport
var $sideBar = $("#sidebar");
$sideBar.affix({
  offset: {
    top: function () {
      var offsetTop      = $sideBar.offset().top
      var sideBarMargin  = parseInt($sideBar.children(0).css('margin-top'), 10)
      var navOuterHeight = $('.navbar-fixed-top').height()
      return (this.top = offsetTop - navOuterHeight - sideBarMargin - 20)
    },
    bottom: function () {
      footerHeightOffset = 200 // Adjust for footer height
      return (this.bottom = $('#footer').outerHeight(true) + footerHeightOffset)
    }
  }
})

// Replace SVG images with inline SVG tags
jQuery('img.svg').each(function(){
  var $img = jQuery(this);
  var imgID = $img.attr('id');
  var imgClass = $img.attr('class');
  var imgURL = $img.attr('src');

  jQuery.get(imgURL, function(data) {
    // Get the SVG tag, ignore the rest
    var $svg = jQuery(data).find('svg');

    // Add replaced image's ID to the new SVG
    if(typeof imgID !== 'undefined') {
      $svg = $svg.attr('id', imgID);
    }
    // Add replaced image's classes to the new SVG
    if(typeof imgClass !== 'undefined') {
      $svg = $svg.attr('class', imgClass+' replaced-svg');
    }

    // Remove any invalid XML tags as per http://validator.w3.org
    $svg = $svg.removeAttr('xmlns:a');

    // Replace image with new SVG
    $img.replaceWith($svg);
  }, 'xml');
});

// Google analytics
var _gaq = _gaq || [];
_gaq.push(['_setAccount', 'UA-70798216-1']);
_gaq.push(['_trackPageview']);
(function() {
  var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
  ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
  var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();