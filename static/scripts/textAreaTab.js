function tabFix(e, textarea){
	if(e.keyCode==9 || e.which==9){
        e.preventDefault();
        var s = textarea.selectionStart;
        textarea.value = textarea.value.substring(0,textarea.selectionStart) + "\t" + textarea.value.substring(textarea.selectionEnd);
        textarea.selectionEnd = s+1; 
    }
}

