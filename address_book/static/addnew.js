var current_edit_id = null;

function get_btn_id(clicked_id){
    //console.log("Clicked ID: " + clicked_id)
    current_edit_id = clicked_id;
    //console.log("CURRENT ID: " + current_edit_id);
}

function apply_sort(sort_function){
    
    contact_info = $(".contact").get();
    contact_info.sort(sort_function);
    $("#contact_table").html(contact_info);
    console.log("Applied Sort!")
    
}

function get_contact_zip(contact){

    return $(contact).find("#zip"+$(contact).attr("id")).text();
    
}

var zip_descending = false;
var name_descending = false;

function zip_sort_descending(a, b){

    a_zip_code = get_contact_zip(a)
    b_zip_code = get_contact_zip(b);
    return a_zip_code > b_zip_code ? 1 : -1;
    
}

function zip_sort_ascending(a, b){

    a_zip_code = get_contact_zip(a);
    b_zip_code = get_contact_zip(b);
    return a_zip_code < b_zip_code ? 1 : -1;
    
}

function zip_sort_toggle(){

    name_descending = false;

    if(zip_descending == false){

    apply_sort(zip_sort_descending);
    zip_descending = true;
    
    }else{

    apply_sort(zip_sort_ascending);
    zip_descending = false;
    
    }
    
}

function get_contact_name(contact){

    return $(contact).find("#lname"+$(contact).attr("id")).text();

}

function name_sort_descending(a, b){

    a_name = get_contact_name(a);
    b_name = get_contact_name(b);
    return a_name > b_name ? 1 : -1;

}

function name_sort_ascending(a, b){

    a_name = get_contact_name(a);
    b_name = get_contact_name(b);
    return a_name < b_name ? 1 : -1;

}

function name_sort_toggle(){
    
    zip_descending = false;

    if(name_descending == false){

    apply_sort(name_sort_descending);
    name_descending = true;
    
    }else{

    apply_sort(name_sort_ascending);
    name_descending = false;
    
    }

}


function delete_contact(id_num){
    console.log("deleting: " + id_num)
    document.getElementById(id_num).remove()
    $.post("/deleteContact", {
            id: id_num
    });  

    window.onbeforeunload = function (event) {
        var message = 'Important: If you have made any edits to this address book and not clicked SAVE, these changes will be lost. Press OK to continue anyway.';
        if (typeof event == 'undefined') {
            event = window.event;
        }
        if (event) {
            event.returnValue = message;
        }
        return message;
    };
}

$(document).ready(function() {

    function get_new_id(){
        // Generate a new id for each contact row, so that we have the ability to access them directly for edits/deletes
        // both on the view page as well as within the DB.
        var contacts = document.getElementsByClassName("contact")
        var contact_count = contacts.length
        if (contact_count > 0){
            var last_contact = contacts[contact_count-1]
            var id_num = parseInt(last_contact.getAttribute("id")) + 1
        }
        else{
            var id_num = 0
        }
        return id_num;
    }

    $("#cancel").click(function(){
        // Clear the "Add Contact" form if the user selects the Cancel button.
        $("#firstname").val('');
        $("#lastname").val('');
        $("#phone").val('');
        $("#zip").val('');
        $("#address").val('');
        $("#city").val('');
        $("#state").val('');
    });

    $("#new_contact_form").submit(function(event) {

        /* stop form from submitting normally */
        event.preventDefault();
        var id_num = get_new_id();
        
        /* get some values from elements on the page: */
        var $form = $(this),
            fname = $form.find('input[name="first_name"]').val(),
            lname = $form.find('input[name="last_name"]').val(),
            phone = $form.find('input[name="phone_num"]').val(),
            user_email = $form.find('input[name="email"]').val(),
            addy = $form.find('input[name="address"]').val(),
            city_name = $form.find('input[name="city"]').val(),
            state_abrv = $form.find('input[name="state"]').val(),
            zip = $form.find('input[name="zip_code"]').val(),
            url = $form.attr('action');

        console.log(id_num + "for: " + fname)
        /* Send the data using post */
        var posting = $.post(url, {
            first_name: fname,
            last_name: lname,
            phone_num: phone,
            email: user_email,
            address: addy,
            city: city_name,
            state: state_abrv,
            zipcode: zip,
            id: id_num
        });

        /* Put the results in a div */
        posting.done(function(data) {

            $("#contact_table").append('<div id=' +id_num+ ' style="border-style:groove; margin-bottom:5px;" class="text-center contact"><p><strong>First Name:</strong><span id="fname'+id_num+'"> ' 
            + fname + '</span>&nbsp;&nbsp;&nbsp;&nbsp;<strong>Last Name:</strong><span id="lname'+id_num+'">' + lname + '</span>&nbsp;&nbsp;&nbsp;&nbsp;<strong>Phone:</strong><span id="phone'+id_num+'"> ' 
            + phone + '</span>&nbsp;&nbsp;&nbsp;&nbsp;<strong>Email:</strong><span id="email'+id_num+'">' + user_email + '</span> <br><strong>Address:</strong><span id="addy'+id_num+'">' + addy + '</span>&nbsp;&nbsp;&nbsp;&nbsp;<strong>City:</strong><span id="city'+id_num+'">' 
            + city_name + '</span>&nbsp;&nbsp;&nbsp;&nbsp;<strong>State:</strong><span id="state'+id_num+'">' 
            + state_abrv + '</span>&nbsp;&nbsp;&nbsp;&nbsp;<strong>Zipcode:</strong><span id="zip'+id_num+'">' 
            + zip + '</span></p> <button id=' +id_num+ ' type="button" onclick="get_btn_id(this.id)" class="btn btn-outline-dark edit_btn" data-toggle="modal" data-target="#exampleModal">Edit Contact</button> <button id=del' +id_num+ ' type="button" onclick="delete_contact(' + id_num + ')" class="btn btn-outline-dark delete_btn">Delete Contact</button></div></div>'); 


            //clear the add form

            $("#firstname").val('');
            $("#lastname").val('');
            $("#phone").val('');
            $("#zip").val('');
            $("#address").val('');
            $("#city").val('');
            $("#state").val('');
            $("#email").val('');

            window.onbeforeunload = function (event) {
                
                    var message = 'Important: If you have made any edits to this address book and not clicked SAVE, these changes will be lost. Press OK to continue anyway.';
                    if (typeof event == 'undefined') {
                        event = window.event;
                    }
                    if (event) {
                        event.returnValue = message;
                    }
                    return message;
            };
            
        });

    });

    $("#save").submit(function(event) {

        /* stop form from submitting normally */
        event.preventDefault();

        /* get the address book title from the page: */
        var $form = $(this),
            title = $("#address_book_title").html();
            url = $form.attr('action');
        
        /* Send the data using post */
        var posting = $.post(url, {
            book_name:title
        });

        /* Alert the user that their results have been saved */
        posting.done(function(data) {
            alert("You're work has been saved!")
            window.onbeforeunload = null;
        });
    });

    $("#delete_book").submit(function(event) {

        /* stop form from submitting normally */
        event.preventDefault();

        $("delete_btn").remove();
        
        /* get the address book title from the page: */
        var $form = $(this),
            title = $("#address_book_title").html();
            url = $form.attr('action');
        
        /* Send the data using post */
        var posting = $.post(url, {
            book_name:title
        });

        /* Alert the user that their results have been saved */
        posting.done(function(data) {
            alert("Your book has been deleted!")
        });
    });

    $("#contact_table").on("click", ".edit_btn", function(){
        // Populate edit form with currently selected contact's info so 
        // that the user can quickly update only relevant fields. 

        var fname = document.getElementById("fname"+current_edit_id).textContent;
        $("#contact_fname").val(fname);

        var lname = document.getElementById("lname"+current_edit_id).textContent;
        $("#contact_lname").val(lname);

        var phone = document.getElementById("phone"+current_edit_id).textContent;
        $("#contact_phone").val(phone);

        var zip = document.getElementById("zip"+current_edit_id).textContent;
        $("#contact_zipcode").val(zip);

        var city = document.getElementById("city"+current_edit_id).textContent;
        $("#contact_city").val(city);

        var state = document.getElementById("state"+current_edit_id).textContent;
        $("#contact_state").val(state);

        var address = document.getElementById("addy"+current_edit_id).textContent;
        $("#contact_address").val(address);

        var email = document.getElementById("email"+current_edit_id).textContent;
        $("#contact_email").val(email);

    });

    $("#edit_contact").submit(function(event) {

        // AJAX for updating a contact entry. 

        /* stop form from submitting normally */
        event.preventDefault();
        var contact_id = current_edit_id

        /* get new updated values from elements on the page: */
        var $form = $(this),
            fname = $form.find('input[name="contact_fname"]').val(),
            lname = $form.find('input[name="contact_lname"]').val(),
            phone = $form.find('input[name="contact_phone"]').val(),
            user_email = $form.find('input[name="contact_email"]').val(),
            addy = $form.find('input[name="contact_address"]').val(),
            city_name = $form.find('input[name="contact_city"]').val(),
            state_abrv = $form.find('input[name="contact_state"]').val(),
            zip = $form.find('input[name="contact_zipcode"]').val(),
            url = $form.attr('action');

        /* Send the data using post */
        var posting = $.post(url, {
            first_name: fname,
            last_name: lname,
            phone_num: phone,
            email: user_email,
            address: addy,
            city: city_name,
            state: state_abrv,
            zipcode: zip,
            id: contact_id

        });
        
        /* Update contact via the outer div ID */
        posting.done(function(data) {
            
            $("#"+contact_id).replaceWith('<div id=' +contact_id+ ' style="border-style:groove; margin-bottom:5px;" class="text-center contact"><p><strong>First Name:</strong><span id="fname'+contact_id+'"> ' 
            + fname + '</span>&nbsp;&nbsp;&nbsp;&nbsp;<strong>Last Name:</strong><span id="lname'+contact_id+'">' + lname + '</span>&nbsp;&nbsp;&nbsp;&nbsp;<strong>Phone:</strong><span id="phone'+contact_id+'"> ' 
            + phone + '</span>&nbsp;&nbsp;&nbsp;&nbsp;<strong>Email:</strong><span id="email'+contact_id+'">' + user_email + '</span> <br><strong>Address:</strong><span id="addy'+contact_id+'">' + addy + '</span>&nbsp;&nbsp;&nbsp;&nbsp;<strong>City:</strong><span id="city'+contact_id+'">' 
            + city_name + '</span>&nbsp;&nbsp;&nbsp;&nbsp;<strong>State:</strong><span id="state'+contact_id+'">' 
            + state_abrv + '</span>&nbsp;&nbsp;&nbsp;&nbsp;<strong>Zipcode:</strong><span id="zip'+contact_id+'">' 
            + zip + '</span></p> <button id=' +contact_id+ ' type="button" onclick="get_btn_id(this.id)" class="btn btn-outline-dark edit_btn" data-toggle="modal" data-target="#exampleModal">Edit Contact</button> <button id=del' +contact_id+ ' type="button" onclick="delete_contact(' + contact_id + ')" class="btn btn-outline-dark delete_btn">Delete Contact</button></div></div>')

        
            $('#exampleModal').modal('hide');

            window.onbeforeunload = function (event) {
                var message = 'Important: If you have made any edits to this address book and not clicked SAVE, these changes will be lost. Press OK to continue anyway.';
                if (typeof event == 'undefined') {
                    event = window.event;
                }
                if (event) {
                    event.returnValue = message;
                }
                return message;
            };

        });
    });

});
