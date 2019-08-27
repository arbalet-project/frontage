/**
 * @fileoverview This file contains all the graphical functions and event manager
 */

let googleStore = "market://details?id=com.arbalet.frontage";
let appleStore = "https://itunes.apple.com/fr/app/arbalet-frontage/id1393183208";
let selectedStore = googleStore;

let liveURL = "http://live.arbalet-project.org";

$('#google-store').on('click', function () {
    selectedStore = googleStore;
    $('#store').fadeIn(200);
    $('.store-popup').fadeIn(200);
})

$('#apple-store').on('click', function () {
    selectedStore = appleStore;
    $('#store').fadeIn(200);
    $('.store-popup').fadeIn(200);
})

$('#go-store').on('click', function () {
    window.open(selectedStore, '_blank');
    $('#store').fadeOut(200);
    $('.store-popup').fadeOut(200);
})

$('#cancel-store').on('click', function () {
    $('#store').fadeOut(200);
    $('.store-popup').fadeOut(200);
})

$('#live').on('click', function () {
    window.open(liveURL, '_blank');
})