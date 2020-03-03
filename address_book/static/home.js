$(document).ready(function() {




    $(document).on("click", "#create", function(){

        $("#create_new").modal("hide");
    });

    $("a").click(function(){

        $("#open_existing").modal("hide");
    });

});

function hide_create_new_modal(){
    $('#create_new').modal('hide');
}

document.querySelector('.button').onmousemove = (e) => {
            const x = e.pageX - e.target.offsetLeft;
            const y = e.pageY - e.target.offsetTop;
            e.target.style.setProperty('--x', `${ x }px`);
            e.target.style.setProperty('--y', `${ y }px`);
}

document.querySelector(".button1").onmousemove = (e) => {
            const x = e.pageX - e.target.offsetLeft;
            const y = e.pageY - e.target.offsetTop;
            e.target.style.setProperty('--x', `${ x }px`);
            e.target.style.setProperty('--y', `${ y }px`);
}
