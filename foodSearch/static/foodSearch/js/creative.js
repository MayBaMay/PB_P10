function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


 (function($) {
  "use strict"; // Start of use strict

  // Smooth scrolling using jQuery easing
  $('a.js-scroll-trigger[href*="#"]:not([href="#"])').click(function() {
    if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
      let target = $(this.hash);
      target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
      if (target.length) {
        $('html, body').animate({
          scrollTop: (target.offset().top - 72)
        }, 1000, "easeInOutExpo");
        return false;
      }
    }
  });

  // Closes responsive menu when a scroll trigger link is clicked
  $('.js-scroll-trigger').click(function() {
    $('.navbar-collapse').collapse('hide');
  });

  // Activate scrollspy to add active class to navbar items on scroll
  $('body').scrollspy({
    target: '#mainNav',
    offset: 75
  });

  // Collapse Navbar
  let navbarCollapse = function() {
    if ($("#mainNav").offset().top > 100) {
      $("#mainNav").addClass("navbar-scrolled");
    } else {
      $("#mainNav").removeClass("navbar-scrolled");
    }
  };
  // Collapse now if page is not at top
  navbarCollapse();
  // Collapse the navbar when page is scrolled
  $(window).scroll(navbarCollapse);

  // Magnific popup calls
  $('#portfolio').magnificPopup({
    delegate: 'a',
    type: 'image',
    tLoading: 'Loading image #%curr%...',
    mainClass: 'mfp-img-mobile',
    gallery: {
      enabled: true,
      navigateByImgClick: true,
      preload: [0, 1]
    },
    image: {
      tError: '<a href="%url%">The image #%curr%</a> could not be loaded.'
    }
  });

  // show modalLogIn
  $('.connection').click(function(){
    // hide other modals
    $('#modalNotConnected').modal('hide');
    $('#modalRegister').modal('hide');
    // reset modalLogIn
    let loginform = $('#loginform').attr('id');
    document.getElementById(loginform).reset();
    $('.no-user-error').css('display', 'none');
    $('.password-error').css('display', 'none');
    // show modalLogIn
    $('#modalLogIn').modal('show');
  });

  // submit modal login
  $('#loginform').submit(function(e){
    let formId = $(this).attr('id');
    let submitBtn = $(this).find('input[type=submit]');
    $('.no-user-error').css('display', 'none');
    $('.password-error').css('display', 'none');
    e.preventDefault();
    $.ajax({
      url: "/login/", // the file to call
      type: "POST", // GET or POST
      data: $(this).serialize(), // get the form data
      success: function(data){
        let login_response = jQuery.parseJSON(data);
        // console.log(login_response);
        if (login_response.user == "success"){
          document.location.reload(true);
          $('#modalLogIn').modal('hide');
        }
        else if (login_response.user == "password wrong") {
          $('.password-error').css('display', 'block');
          submitBtn.prop('disabled', false);
          hideLoader();
           }
        else{
          $('.no-user-error').css('display', 'block');
          document.getElementById(formId).reset();
          hideLoader();
        }
      }
    })
  });

  $('#disconnection').click(function(){
    $('#modalLogOut').modal('show');
  });

  $('#registration').click(function(){
    $('#modalLogIn').modal('hide');
    let formId = $('#registerForm').attr('id');
    document.getElementById(formId).reset();
    $('#username-error').css('display', 'none');
    $('#modalRegister').modal('show');
  });

  $('#registerForm').submit(function(e){
    let formId = $(this).attr('id');
    let submitBtn = $(this).find('input[type=submit]');
    $('#username-error').css('display', 'none');
    e.preventDefault();
    $.ajax({
      url: "/register/", // the file to call
      type: "POST", // GET or POST
      data: $(this).serialize(), // get the form data
      success: function(data){
        let register_response = jQuery.parseJSON(data);
        // console.log(register_response);
        if (register_response.user == "success"){
          document.location.reload(true);
          $('#modalRegister').modal('hide');
          initLoader();
        }
        else if (register_response.user == "already in DB") {
          $('#username-error').css('display', 'block');
          submitBtn.prop('disabled', false);
           }
        else{
          $('.no-user-error').css('display', 'block');
        }
      }
    })
  });

  $('.NotConnected').click(function(){
    console.log('notconnected');
    $('#modalNotConnected').modal('show');
  });

  // SAVE FAVORITE
  $('.favoriteForm').submit(function(e){
    let form = $(this);
    let wachlist = $(this).hasClass("wachlist");
    let fav = $(this).children('input[name$="favorite"]');
    e.preventDefault();
    $.ajax({
      url: "/load_favorite/", // the file to call
      type: "POST", // GET or POST
      data: $(this).serialize(),
    })
      .done(function(data) {
        var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
        let favorite_response = jQuery.parseJSON(data);
        let submit = form.find('button');
        if (wachlist){
          form.parent(".row").parent(".prodbox").remove();
        }
        else{
          if(favorite_response.favorite == "saved"){
          submit.html("<span class='fas fa-floppy-o'></span> Retirer ce produit de mes favoris");
          fav.val("saved");
          }
        else{
          submit.html("<span class='fas fa-floppy-o'></span> Sauvegarder");
          fav.val("unsaved");
          }
        }

    })
  });

  $('.return').on('click', function(e){
    window.location.replace(document.referrer);
  })

  $('.load').on('click', function(e){
    initLoader();
  });

  $('.searchForm').on('submit', function(e){
    initLoader();
  });

})(jQuery); // End of use strict

function createLoader(){
  return $(`<svg width="72" height="72" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><style>.spinner{animation:1s linear infinite opacity-svg;transform-origin:50%}@keyframes opacity-svg{0%{opacity:1}to{opacity:0}}.spinnerN1{transform:rotate(0deg) translateY(-30px);animation-delay:0}.spinnerN2{transform:rotate(30deg) translateY(-30px);animation-delay:.08333333333333333s}.spinnerN3{transform:rotate(60deg) translateY(-30px);animation-delay:.16666666666666666s}.spinnerN4{transform:rotate(90deg) translateY(-30px);animation-delay:.25s}.spinnerN5{transform:rotate(120deg) translateY(-30px);animation-delay:.3333333333333333s}.spinnerN6{transform:rotate(150deg) translateY(-30px);animation-delay:.4166666666666667s}.spinnerN7{transform:rotate(180deg) translateY(-30px);animation-delay:.5s}.spinnerN8{transform:rotate(210deg) translateY(-30px);animation-delay:.5833333333333334s}.spinnerN9{transform:rotate(240deg) translateY(-30px);animation-delay:.6666666666666666s}.spinnerN10{transform:rotate(270deg) translateY(-30px);animation-delay:.75s}.spinnerN11{transform:rotate(300deg) translateY(-30px);animation-delay:.8333333333333334s}.spinnerN12{transform:rotate(330deg) translateY(-30px);animation-delay:.9166666666666666s}</style><path fill="none" d="M0 0h100v100H0z"/><rect x="46.5" y="40" width="7" height="20" rx="5" ry="5" fill="#c9c7c7" class="spinner spinnerN1"/><rect x="46.5" y="40" width="7" height="20" rx="5" ry="5" fill="#c9c7c7" class="spinner spinnerN2"/><rect x="46.5" y="40" width="7" height="20" rx="5" ry="5" fill="#c9c7c7" class="spinner spinnerN3"/><rect x="46.5" y="40" width="7" height="20" rx="5" ry="5" fill="#c9c7c7" class="spinner spinnerN4"/><rect x="46.5" y="40" width="7" height="20" rx="5" ry="5" fill="#c9c7c7" class="spinner spinnerN5"/><rect x="46.5" y="40" width="7" height="20" rx="5" ry="5" fill="#c9c7c7" class="spinner spinnerN6"/><rect x="46.5" y="40" width="7" height="20" rx="5" ry="5" fill="#c9c7c7" class="spinner spinnerN7"/><rect x="46.5" y="40" width="7" height="20" rx="5" ry="5" fill="#c9c7c7" class="spinner spinnerN8"/><rect x="46.5" y="40" width="7" height="20" rx="5" ry="5" fill="#c9c7c7" class="spinner spinnerN9"/><rect x="46.5" y="40" width="7" height="20" rx="5" ry="5" fill="#c9c7c7" class="spinner spinnerN10"/><rect x="46.5" y="40" width="7" height="20" rx="5" ry="5" fill="#c9c7c7" class="spinner spinnerN11"/><rect x="46.5" y="40" width="7" height="20" rx="5" ry="5" fill="#c9c7c7" class="spinner spinnerN12"/></svg>`);
}

function initLoader(){
  let borderLoader = $('<div id="borderLoader"></div>');
  let loader = $('<div id="loader"></div>');
  loader.append(createLoader());
  borderLoader.append(loader);
  $('body').append(borderLoader);
}

function hideLoader(){
  let borderLoader = $('<div id="borderLoader"></div>');
  borderLoader.remove();
}
