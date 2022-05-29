$(document).ready(function(){
    $('.navbar-fostrap').click(function(){
        $('.nav-fostrap').toggleClass('visible');
        $('body').toggleClass('cover-bg');
    });
});
img1 = document.getElementById("img1")
img2 = document.getElementById("img2")
input1 = document.getElementById("file1")
input2 = document.getElementById("file2")
clear = document.getElementById("clear");
if(clear){
    clear.addEventListener("click", (e) => {
        e.preventDefault();
        img1.src = ""
        img2.src = ""
        input1.value = ""
        input2.value = ""
    });
}

setTimeout(() => {
    let flashed_messages = document.getElementsByClassName("flashed_messages")
    while(flashed_messages.length){
        flashed_messages[0].remove();
        }
}, 5000);

if(document.getElementById("back_button")){
    let back_button = document.getElementById("back_button")
    back_button.addEventListener("click", ()=>{
        window.history.back()
    } )
}