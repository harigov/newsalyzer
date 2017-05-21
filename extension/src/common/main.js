// ==UserScript==
// @name ChristmasTree
// @include http://*
// @include https://*
// @require jquery-3.2.1.min.js
// @require artoo-latest.min.js
// ==/UserScript==
var $ = window.$ || artoo.$ || $;
var jQuery = jQuery || $;

var info_btn = $(document.createElement('div')).css({
	position: 'absolute',
	top: '80px',
	left: document.body.clientWidth - 60 + 'px',
	height: '30px',
	width: '30px',
	background: 'rgba(0, 0, 0, 0.6)',
	'background-image': 'info.png',
	'background-size': 'contain',
	'z-index': '2147483647'
}).appendTo(document.body);

var info_bar = $(document.createElement('div')).css({
	position: 'absolute',
	top: '110px',
	height: '500px',
	left: document.body.clientWidth - 330 + 'px',
	width: '300px',
	background: 'rgba(0, 0, 0, 0.6)',
	'z-index': '2147483647',
	'display': 'none',
	'overflow-y': 'scroll'
}).appendTo(document.body);

// This will eventually be coded as a web service
function extract_article() {
	var paragraphs = artoo.scrape('article .story-body-text', {content: 'text'} );
	var article = "";
	for(var p in paragraphs) {
		article += paragraphs[p].content;
	}
	return article;
}

info_btn.click(function() {
	var article = extract_article();
	info_bar.text(article);
	if (info_bar.is(':visible')) {
		info_bar.hide();
	} else {
		info_bar.show();
	}
});