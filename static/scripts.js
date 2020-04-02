window.onload = function () {
  if(window.location.href == localStorage.getItem('lastUrl')) {
	mainScrollArea.scrollTop = localStorage.getItem('scrollTop');
  } else {
	localStorage.setItem('lastUrl', window.location.href);
	localStorage.setItem('scrollTop', 0);
  }
}
