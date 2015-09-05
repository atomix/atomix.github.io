// hljs
$(document).ready(function() {
  $('pre code').each(function(i, block) {
    hljs.highlightBlock(block);
    $(this).parent().css("word-wrap", "normal");
    $(this).css("white-space", "pre");
  });
});

/** scroll spy */
$('body').scrollspy({ target: '#sidebar-col' })

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
      return (this.bottom = $('#footer').outerHeight(true) + 64)
    }
  }
})
