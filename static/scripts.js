function activate_dialog(suffix) {
	var dialog = document.querySelector('#dialog-' + suffix);
	dialogPolyfill.registerDialog(dialog)
	var showDialogButton = document.querySelector('#' + suffix);
	if(!dialog.showModal) {
		dialogPolyfill.registerDialog(dialog);
	}
	showDialogButton.addEventListener('click', function() {
		dialog.showModal();
	});
	dialog.querySelector('.close').addEventListener('click', function() {
		dialog.close();
	});
}

function append_path_to_history() {
	var path = window.location.pathname
	if(sessionStorage.path_history === undefined) {
		sessionStorage.path_history = path
	}
	else {
		sessionStorage.path_history += "," + path
	}
}
append_path_to_history();

function back_from_problem() {
	var arr = sessionStorage.path_history.split(',');
	found = '/contest/all';

	for(i = arr.length - 1; i >= 0; --i) {
		if(arr[i] == "/problems/") {
			found = arr[i];
			break;
		}
		if(arr[i].indexOf('/contest/') == 0) {
			var words = arr[i].split('/');
			var last_word = words[words.length - 1];
			if(last_word != 'edit') {
				found = arr[i];
				break;
			}
		}
	}
	window.location.replace(found);
}

$(document).ready(function () {
	var s = "scrollsave-" + window.location.pathname
    if(localStorage.getItem(s) != null) {
		$(window).scrollTop(localStorage.getItem(s));
    }

    $(window).on("scroll", function() {
        localStorage.setItem(s, $(window).scrollTop());
    });
});
