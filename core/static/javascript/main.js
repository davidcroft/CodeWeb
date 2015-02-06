jQuery.expr[':'].regex = function(elem, index, match) {
    var matchParams = match[3].split(','),
        validLabels = /^(data|css):/,
        attr = {
            method: matchParams[0].match(validLabels) ? 
                        matchParams[0].split(':')[0] : 'attr',
            property: matchParams.shift().replace(validLabels,'')
        },
        regexFlags = 'ig',
        regex = new RegExp(matchParams.join('').replace(/^\s+|\s+$/g,''), regexFlags);
    return regex.test(jQuery(elem)[attr.method](attr.property));
}

/* write you javascript here */
$(document).ready(function(){
  $('.carousel').carousel({
    interval: 3000
    
  });
});

function scrolltosection(i){
    switch(i){
        case "Profile": $('html, body').animate({
            scrollTop: $("#Profile").offset().top
        }, 1000);break;
        case "Projects": $('html, body').animate({
            scrollTop: $("#Projects").offset().top
        }, 1000);break;
        case "Papers": $('html, body').animate({
            scrollTop: $("#Papers").offset().top
        }, 1000);break;
        case "Posts": $('html, body').animate({
            scrollTop: $("#Posts").offset().top
        }, 1000);break;

        case "Slideshow": $('html, body').animate({
            scrollTop: $("#Slideshow").offset().top
        }, 1000);break;
        case "News": $('html, body').animate({
            scrollTop: $("#News").offset().top
        }, 1000);break;
        case "About": $('html, body').animate({
            scrollTop: $("#About").offset().top
        }, 1000);break;
        case "Admission": $('html, body').animate({
            scrollTop: $("#Admission").offset().top
        }, 1000);break;
        case "AdminProfile": $('html, body').animate({
            scrollTop: $("#AdminProfile").offset().top
        }, 1000);break;
        
        default:break;
    }
}

function addItem(selector, index) {
    for (var i = 1; i < 4; i++) {
        if (i == index) {
            $(selector + " tr").eq(index).css("display", "inline");
        } else {
            $(selector + " tr").eq(i).css("display", "none");
        }
    }
}

function addItemForm(selector) {
    var type = 'form';
    // Part of the code is adapted from https://stackoverflow.com/questions/501719/dynamically-adding-a-form-to-a-django-formset-with-ajax
    var newElement = $(selector).clone(true);
    var total = $('#id_' + type + '-TOTAL_FORMS').val();
    
    newElement.find('tr').each(function(index) {
        if (index != 0) {
            $(this).css('display', 'none');
        }
    });
    newElement.find(':input').each(function() {
        var name = $(this).attr('name').replace('-' + (total-1) + '-','-' + total + '-');
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
    });
    newElement.find('label').each(function() {
        var newFor = $(this).attr('for').replace('-' + (total-1) + '-','-' + total + '-');
        $(this).attr('for', newFor);
    });
    total++;
    $('#id_' + type + '-TOTAL_FORMS').val(total);
    $(selector).after(newElement);
}

function removeItemForm(selector) {
    var type = 'form'
    var total = $('#id_' + type + '-TOTAL_FORMS').val();
    $('#id_' + type + '-TOTAL_FORMS').val(total-1);
    $(selector).remove();
}

$('#profile-picture').change(function() {
    //console.log("enter onchange"); 
    var imageFiles = document.getElementById('profile-picture').files //FileList object
    var files = event.target.files;
    var output = document.getElementById("profile-images");

    var file = files[0];
    //Only pics
    if(!file.type.match('image'))
      return;
    var picReader = new FileReader();
    picReader.addEventListener("load",function(event){
        var picFile = event.target;
        var div = document.createElement("div");
        div.innerHTML = "<img src='" + picFile.result + "'" + "width=100%/>";
        var profile_image = document.getElementById("profile-images");
        while (profile_image.hasChildNodes()) {
            profile_image.removeChild(profile_image.firstChild);
        }
        output.appendChild(div);
    });
    
    //Read the image
    picReader.readAsDataURL(file);
    
    });

$('#newSlide-picture').change(function() {
    //console.log("enter onchange"); 
    var imageFiles = document.getElementById('newSlide-picture').files //FileList object
    var files = event.target.files;
    var output = document.getElementById("newSlide-images");
    var file = files[0];
    //Only pics
    if(!file.type.match('image'))
      return;
    var picReader = new FileReader();
    picReader.addEventListener("load",function(event){
        var picFile = event.target;
        var div = document.createElement("div");
        div.innerHTML = "<img src='" + picFile.result + "'" + "width=100%/>";
        var newSlide_image = document.getElementById("newSlide-images");
        while (newSlide_image.hasChildNodes()) {
            newSlide_image.removeChild(newSlide_image.firstChild);
        }
        output.appendChild(div);
    });
    //Read the image
    picReader.readAsDataURL(file);
    });

var maxlength = 300;
$('p.limitText').text(function (_, text) {
    return $.trim(text).substring(0, maxlength);
});

$(function() {
    $('.jcarousel').jcarousel();
});
