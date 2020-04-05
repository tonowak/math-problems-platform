function activate_dialog(suffix) {
	var dialog = document.querySelector('#dialog-' + suffix);
	dialogPolyfill.registerDialog(dialog)
	var showDialogButton = document.querySelector('#show-delete-' + suffix);
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
