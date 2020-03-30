var mainScrollArea = document.getElementsByClassName('mdl-layout__content')[0];
var scrollTimeout;

window.onload = function () {
  if(window.location.href == localStorage.getItem('lastUrl')) {
	mainScrollArea.scrollTop = localStorage.getItem('scrollTop');
  } else {
	localStorage.setItem('lastUrl', window.location.href);
	localStorage.setItem('scrollTop', 0);
  }
}

mainScrollArea.addEventListener('scroll', function() {
  clearTimeout(scrollTimeout);
  scrollTimeout = setTimeout(function() {
	localStorage.setItem('scrollTop', mainScrollArea.scrollTop);
  }, 100)
});
