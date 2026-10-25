function copyMessage() {
    let msg = document.getElementById("msgBox");
    msg.select();
    msg.setSelectionRange(0, 99999); // for mobile
    navigator.clipboard.writeText(msg.value);
    alert("Message copied to clipboard!");
}
