
$(document).ready(function(){

    /* MEMBER PROFILE FUNCTIONS */

    // Member Cover Letter
    $("#get_member_cover_letter").submit(function(event){
        
        // Use AJAX to populate cover letter data. 
        event.preventDefault();
        var view_member = this.name;
        var $form = $(this),
        url = $form.attr('action');

        var posting = $.post(url);

        /* Put the results in a div */
        posting.done(function(data) {
            $("#member_card_content").load("/member_cover_letters/"+view_member)
        });
    });

    // Member Resume
    $("#get_member_resume").submit(function(event){
        
        // Use AJAX to populate resume data. 
        event.preventDefault();
        var view_member = this.name;
        var $form = $(this),
        url = $form.attr('action');

        var posting = $.post(url);

        /* Put the results in a div */
        posting.done(function(data) {
            $("#member_card_content").load("/member_resumes/"+view_member)
        });
    });

    // Member Carousel
    $("#get_member_my_life").submit(function(event){
        
        // Use AJAX to populate carousel data. 
        event.preventDefault();
        var view_member = this.name;
        var $form = $(this),
        url = $form.attr('action');
        var posting = $.post(url);

        /* Put the results in a div */
        posting.done(function(data) {
            $("#member_card_content").load("/member_my_life/"+view_member)
        });
    });



    /* COVER LETTER FUNCTIONS */

    $("#get_cover_letter").submit(function(event){
        
        // Use AJAX to populate cover letter data. 
        event.preventDefault();

        var $form = $(this),
        url = $form.attr('action');

        var posting = $.post(url);

        /* Put the results in a div */
        posting.done(function(data) {
            $("#card_content").load("/cover_letter")
        });
    });

    // Upload Cover Letter
    $(function() {
        $('#cover_letter_upload_btn').click(function() {

            var form_data = new FormData($('#cover_letter_upload_form')[0]);

            $.ajax({
                type: 'POST',
                url: '/cover_letter_upload',
                data: form_data,
                contentType: false,
                cache: false,
                processData: false,
                success: function(data) {
                    if (data.response == "Invalid_Format"){
                        alert("Your file is not the correct format, please upload your cover letter as a PDF.");
                    } else if (data.response == "Success"){
                        alert("Cover Letter Upload Successful!");
                    } else if (data.response == "Max_Uploads"){
                        alert("You are already at the max number of cover letter uploads! Please delete an existing cover letter if you wish to upload a new one.");
                    }
                    $("#card_content").load("/cover_letter")
                },
            });
        });
    });

    // Delete Uploaded Cover Letter
    $(function(){
        $(".delete_uploaded_cl_btn").click(function() {

            console.log("Deleting cover letter...");
            cl_id = this.name

            var form_data = new FormData();
            form_data.append("cover_letter_key", cl_id)

            $.ajax({
                type: "POST",
                url: "/delete_uploaded_cover_letter",
                contentType: false,
                cache: false,
                processData: false,
                data: form_data,
                success: function(data, status) {
                    console.log("Cover letter deleted with status: ", status);
                    document.getElementById(cl_id).outerHTML = "";
                },
                error: function(xhr, status) {
                    console.log("Error: ", status);
                }
            });
        });
    });

    $(function(){
        $(".delete_created_cl_btn").click(function() {

            console.log("Deleting cover letter...");
            cl_id = this.name

            var form_data = new FormData();
            form_data.append("cl_key", cl_id)

            $.ajax({
                type: "POST",
                url: "/delete_created_cover_letter",
                contentType: false,
                cache: false,
                processData: false,
                data: form_data,
                success: function(data, status) {
                    console.log("Cover letter deleted with status: ", status);
                    document.getElementById(cl_id).outerHTML = "";
                },
                error: function(xhr, status) {
                    console.log("Error: ", status);
                }
            });
        });
    });

    // Create cover letter using cover-letter-builder form
    $(function() {
        $('#cover_letter_creation_form').submit(function(event) {

            event.preventDefault();
            var form_data = new FormData($("#cover_letter_creation_form")[0]);

            $.ajax({
                type: 'POST',
                url: '/cover_letter_create',
                data: form_data,
                contentType: false,
                cache: false,
                processData: false,
                success: function(data) {
                    $(".modal-header button").click();
                    if (data.response == "Max_Uploads"){
                        alert("You are already at the max number of cover letter creations! Please delete an existing cover letter if you wish to create a new one.");
                    } 
                    $("#card_content").load("/cover_letter")
                },
            });
        });
    });

    $(function() {
        $('#cl_builder_edit_btn').click(function() {

            var form_data = new FormData($("#cover_letter_edit_form")[0]);
            var cl_title = document.getElementById("title_data").innerHTML;
            console.log(cl_title)
            form_data.append("title", cl_title)
            $.ajax({
                type: 'POST',
                url: '/cover_letter_edit',
                data: form_data,
                contentType: false,
                cache: false,
                processData: false,
                success: function(data) {
                    $(".modal-header button").click();
                    location.reload();
                    alert("Update Successful!")
                },
            });
        });
    });

    $(function(){
        $(".set_default_cl_btn").click(function() {

            console.log("Setting default cover letter...");
            var cl_id = this.name;
            var cl_type = this.getAttribute("cl_type");

            var form_data = new FormData();
            form_data.append("cover_letter_key", cl_id)
            form_data.append("cover_letter_type", cl_type)

            $.ajax({
                type: "POST",
                url: "/cover_letter_select_default",
                contentType: false,
                cache: false,
                processData: false,
                data: form_data,
                success: function(data, status) {
                    console.log("Cover letter set to default with status: ", status);
                    alert("Cover letter '" + cl_id + "' set as default!")
                },
                error: function(xhr, status) {
                    console.log("Error: ", status);
                }
            });
        });
    });

    $("#edit_cl_modal_btn").on("click", function(){

        // populate general contact info
        var fname = document.getElementById("fname_data").textContent;
        $("#fname").val(fname);

        var lname = document.getElementById("lname_data").textContent;
        $("#lname").val(lname);

        var email = document.getElementById("email_data").textContent;
        $("#email").val(email);

        var address = document.getElementById("address_data").textContent;
        $("#address").val(address);

        var num = document.getElementById("num_data").textContent;
        $("#number").val(num);

        var city_state = document.getElementById("city_state_data").textContent;
        $("#city_state").val(city_state);

        var zip = document.getElementById("zip_data").textContent;
        $("#zip").val(zip);

        var body = document.getElementById("body_data").textContent;
        $("#bodyparagraph").val(body);

        var intro = document.getElementById("intro_data").textContent;
        $("#introduction").val(intro);

        var conclusion = document.getElementById("conclusion_data").textContent;
        $("#conclusion").val(conclusion);

    });

    /* MY LIFE PAGE FUNCTIONS */

    $("#get_my_life").submit(function(event){

        // Use AJAX to populate carousel data. 
        event.preventDefault();

        var $form = $(this),
        url = $form.attr('action');

        var posting = $.post(url);

        /* Put the results in a div */
        posting.done(function(data) {
            console.log(data)
            $("#card_content").load("/my_life");
        
        });
    });



    /* RESUME PAGE FUNCTIONS */

    // Delete Uploaded Resume
    $(function(){
        $(".delete_uploaded_resume_btn").click(function() {

            console.log("Deleting resume...");
            resume_id = this.name

            var form_data = new FormData();
            form_data.append("resume_key", resume_id)

            $.ajax({
                type: "POST",
                url: "/delete_uploaded_resume",
                contentType: false,
                cache: false,
                processData: false,
                data: form_data,
                success: function(data, status) {
                    console.log("Resume deleted with status: ", status);
                    document.getElementById(resume_id).outerHTML = "";
                },
                error: function(xhr, status) {
                    console.log("Error: ", status);
                }
            });
        });
    });

    // Upload Resume
    $(function() {
        $('#resume_upload_btn').click(function() {

            var form_data = new FormData($('#resume_upload_form')[0]);

            $.ajax({
                type: 'POST',
                url: '/resume_upload',
                data: form_data,
                contentType: false,
                cache: false,
                processData: false,
                success: function(data) {
                    if (data.response == "Failed"){
                        alert("Your file is not the correct format, please upload your resume as a PDF.");
                    } else if (data.response == "Success"){
                        alert("Resume Upload Successful!");
                    } else if (data.response=="Max_Uploads"){
                        alert("You are already at the max number of resume uploads! Please delete an existing resume if you wish to upload a new one.");
                    }
                    $("#card_content").load("/resume")
                },
            });
        });
    });

    // Create resume using resume builder form
    $(function() {
        $('#resume_creation_form').submit(function(event) {

            event.preventDefault();
            var form_data = new FormData($("#resume_creation_form")[0]);

            $.ajax({
                type: 'POST',
                url: '/resume_create',
                data: form_data,
                contentType: false,
                cache: false,
                processData: false,
                success: function(data) {
                    $(".modal-header button").click();
                    if (data.response == "Max_Uploads"){
                        alert("You are already at the max number of resume creations! Please delete an existing resume if you wish to build a new one.");
                    }
                    $("#card_content").load("/resume")
                },
            });
        });
    });

    // Populate edit form with current user's intro info so 
    // that the user can quickly update only relevant fields. 
    $("#edit_resume_modal").on("click", function(){
    
        // populate general contact info
        var fname = document.getElementById("fname_data").textContent;
        $("#res_fname").val(fname);

        var lname = document.getElementById("lname_data").textContent;
        $("#res_lname").val(lname);

        var email = document.getElementById("email_data").textContent;
        $("#res_email").val(email);

        var major = document.getElementById("major_data").textContent;
        $("#res_major").val(major);

        var school = document.getElementById("school_data").textContent;
        console.log(school);
        $("#res_school").val(school);

        var address = document.getElementById("address_data").textContent;
        $("#res_address").val(address);

        var num = document.getElementById("num_data").textContent;
        $("#res_number").val(num);

        var city_state = document.getElementById("city_state_data").textContent;
        $("#city_state").val(city_state);

        var zip = document.getElementById("zip_data").textContent;
        $("#zip").val(zip);

        var gpa = document.getElementById("gpa_data").textContent;
        $("#gpa").val(gpa);

        var obj = document.getElementById("obj_data").textContent;
        $("#objective").val(obj);

        // Populate jobs data in modal
        if( $('#job1').contents().length > 1 ) {
            var job1_title = document.getElementById("job1_title_data").textContent;
            $("#job1_title").val(job1_title);

            var job1_emp = document.getElementById("job1_emp_data").textContent;
            $("#job1_emp").val(job1_emp);

            var job1_dates = document.getElementById("job1_date_data").textContent;
            $("#job1_dates").val(job1_dates);

            var job1_desc = document.getElementById("job1_desc_data").textContent;
            $("#job1_desc").val(job1_desc);
        }

        if( $('#job2').contents().length > 1 ) {
            var job2_title = document.getElementById("job2_title_data").textContent;
            $("#job2_title").val(job2_title);

            var job2_emp = document.getElementById("job2_emp_data").textContent;
            $("#job2_emp").val(job2_emp);

            var job2_dates = document.getElementById("job2_date_data").textContent;
            $("#job2_dates").val(job2_dates);

            var job2_desc = document.getElementById("job2_desc_data").textContent;
            $("#job2_desc").val(job2_desc);
        }

        if( $('#job3').contents().length > 1 ) {
            var job3_title = document.getElementById("job3_title_data").textContent;
            $("#job3_title").val(job3_title);

            var job3_emp = document.getElementById("job3_emp_data").textContent;
            $("#job3_emp").val(job3_emp);

            var job3_dates = document.getElementById("job3_date_data").textContent;
            $("#job3_dates").val(job3_dates);

            var job3_desc = document.getElementById("job3_desc_data").textContent;
            $("#job3_desc").val(job3_desc);
        }

        // Populate project data in modal
        if( $('#proj1').contents().length > 1 ) {
            var proj1_title = document.getElementById("proj1_title_data").textContent;
            $("#proj1_title").val(proj1_title);

            var proj1_desc = document.getElementById("proj1_desc_data").textContent;
            $("#proj1_desc").val(proj1_desc);
        }

        if( $('#proj2').contents().length > 1 ) {

            var proj2_title = document.getElementById("proj2_title_data").textContent;
            $("#proj2_title").val(proj2_title);

            var proj2_desc = document.getElementById("proj2_desc_data").textContent;
            $("#proj2_desc").val(proj2_desc);
        }

        if( $('#proj3').contents().length > 1 ) {

            var proj3_title = document.getElementById("proj3_title_data").textContent;
            $("#proj3_title").val(proj3_title);

            var proj3_desc = document.getElementById("proj3_desc_data").textContent;
            $("#proj3_desc").val(proj3_desc);
        }
        var skillset = document.getElementById("skillset_data").textContent;
        $("#skillset").val(skillset);

    });

    // Edit custom-built resume 
    $(function() {
        $('#resume_edit_btn').click(function() {

            var form_data = new FormData($("#resume_creation_form")[0]);
            var resume_title = document.getElementById("title_data").innerHTML;
            form_data.append("title", resume_title);

            $.ajax({
                type: 'POST',
                url: '/resume_edit',
                data: form_data,
                contentType: false,
                cache: false,
                processData: false,
                success: function(data) {
                    $(".modal-header button").click();
                    location.reload();
                    alert("Update Successful!")
                },
            });
        });
    });

    
    // Delete created resume
    $(function(){
        $(".delete_created_resume_btn").click(function() {

            console.log("Deleting resume...");
            var resume_id = this.name

            var form_data = new FormData();
            form_data.append("resume_key", resume_id)

            $.ajax({
                type: "POST",
                url: "/delete_created_resume",
                contentType: false,
                cache: false,
                processData: false,
                data: form_data,
                success: function(data, status) {
                    console.log("Resume deleted with status: ", status);
                    document.getElementById(resume_id).outerHTML = "";
                },
                error: function(xhr, status) {
                    console.log("Error: ", status);
                }
            });
        });
    });

    $(function(){
        $(".set_default_resume_btn").click(function() {

            console.log("Setting default resume...");
            var resume_id = this.name;
            var res_type = this.getAttribute("res_type");
            console.log(res_type)
            var form_data = new FormData();
            form_data.append("resume_key", resume_id)
            form_data.append("resume_type", res_type)

            $.ajax({
                type: "POST",
                url: "/resume_select_default",
                contentType: false,
                cache: false,
                processData: false,
                data: form_data,
                success: function(data, status) {
                    console.log("Resume set to default with status: ", status);
                    alert("Resume '" + resume_id + "' set as default!")
                },
                error: function(xhr, status) {
                    console.log("Error: ", status);
                }
            });
        });
    });

    $("#get_resume").submit(function(event){

        // Use AJAX to populate resume data. 
        event.preventDefault();

        var $form = $(this),
        url = $form.attr('action');

        var posting = $.post(url);

        /* Put the results in a div */
        posting.done(function(data) {
            $("#card_content").load("/resume")
        });
    });




    /* Introduction Page JS Functionality */

    $(function() {
        $('#profile_pic_upload_btn').click(function() {

            var form_data = new FormData($('#profile_pic_form')[0]);

            $.ajax({
                type: 'POST',
                url: '/upload_profile_pic',
                data: form_data,
                contentType: false,
                cache: false,
                processData: false,
                success: function(data) {
                    if (data.response == "Invalid_Format"){
                        alert("Your file is not the correct format, please upload your picture in a JPEG or PNG format.");
                    } 
                    else if (data.response == "Max_Uploads"){
                        alert("You are already at the max number of uploads! Please delete an existing resume if you wish to upload a new one.");
                    }
                    else if (data.response == "Success"){
                        alert("Profile Picture Upload Successful!");
                    }
                    location.reload();
                },
            });
        });
    });

    $("#edit_intro_modal").on("click", function(){
        // Populate edit form with current user's intro info so 
        // that the user can quickly update only relevant fields. 

        // populate first and last name
        var fname = document.getElementById("fullname").getAttribute("fname");
        $("#fname").val(fname);

        var lname = document.getElementById("fullname").getAttribute("lname");
        $("#lname").val(lname);

        // populate modal link values
        var link1 = document.getElementById("link_1_data").getAttribute("href");
        $("#link_1").val(link1);

        var link1_label = document.getElementById("link_1_data").textContent;
        $("#link1_label").val(link1_label);

        var link2 = document.getElementById("link_2_data").getAttribute("href");
        $("#link_2").val(link2);

        var link2_label = document.getElementById("link_2_data").textContent;
        $("#link2_label").val(link2_label);

        var link3 = document.getElementById("link_3_data").getAttribute("href");
        $("#link_3").val(link3);

        var link3_label = document.getElementById("link_3_data").textContent;
        $("#link3_label").val(link3_label);

        // populat bio, major, and class standing
        var bio = document.getElementById("bio_data").textContent;
        $("#bio").val(bio);

        var major = document.getElementById("major_data").textContent;
        $("#major").val(major);

        var class_standing = document.getElementById("class_standing_data").textContent;
        $("#class_standing").val(class_standing);

    });

});

  // upload mylife
  $(function() {
    $('#mylife_pic_upload_btn').click(function() {

        var form_data = new FormData($('#mylife_pic_form')[0]);

        $.ajax({
            type: 'POST',
            url: '/upload_mylife_pic',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function(data) {
                if (data.response == "Failed"){
                    alert("One or more of your images failed to upload because they were the wrong file type.");
                } 
                else if (data.response == "Success"){
                    alert("Carousel Successfully Built!");
                }
                $("#card_content").load("/my_life")
            },
        });
    });
});