$(document).ready(function() {

    function login(){
        $.ajax({
            url: '/',
            method:'POST',
            headers:{
                "authorization": "Basic " + btoa($("#usernameinput").val() + ":" + $("#password").val())
            },
            success: function(res, textStatus, data) {
                redirect = data.getResponseHeader('location')
                window.location.href = "/";
            }
        })
    }

    $(document).keypress(function(event){
        if (event.key === "Enter") {
            login();
        }
    });

    $('#submitButton').click(function() {
        login();
    });
});