// ==UserScript==
// @name ChristmasTree
// @include http://*
// @include https://*
// @require jquery-1.9.1.min.js
// @require artoo-latest.min.js
// ==/UserScript==
var $ = window.$ || artoo.$ || $;
var jQuery = jQuery || $;

$('<link>')
	.attr('rel',"stylesheet")
	.attr('href',"https://netdna.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css")
	.appendTo($('head'));

var info_btn = $('<div>').css({
	position: 'absolute',
	top: '80px',
	left: document.body.clientWidth - 60 + 'px',
	height: '30px',
	width: '30px',
	background: 'rgba(0, 0, 0, 0.85)',
	'background-image': 'info.png',
	'background-size': 'contain',
	'z-index': '2147483647'
}).appendTo(document.body);

var info_bar = $('<div>').css({
	position: 'absolute',
	top: '110px',
	height: '500px',
	left: document.body.clientWidth - 330 + 'px',
	width: '300px',
	background: 'rgba(0, 0, 0, 0.85)',
	'z-index': '2147483647',
	'display': 'none',
	'overflow-y': 'scroll'
}).appendTo(document.body);

var info_container = $('<div>').css({
	margin: '15px'
}).appendTo(info_bar);

// This will eventually be coded as a web service
function extract_article() {
	var paragraphs = artoo.scrape('article .story-body-text', {content: 'text'} );
	var article = "";
	for(var p in paragraphs) {
		article += paragraphs[p].content;
	}
	return article;
}

let entity_header_css = {
	color: 'white',
	'text-align': 'left',
	margin: '2px'
};

let entity_icon_css = {
	color: 'yellow',
	'text-align': 'left'
};

let entity_name_css = {
	color: 'white',
	'text-align': 'left'
};

function get_entity_icon(entity_type) {
	if (entity_type==='PERSON') {
		return 'fa fa-user';
	} else if (entity_type==='ORGANIZATION') {
		return 'fa fa-sitemap';
	} else if (entity_type==='LOCATION') {
		return 'fa fa-globe';
	}
}

let positive_color = 'rgba(0, 255, 0, 1)';
let negative_color = 'rgba(255, 0, 0, 1)';
let marker_color = 'rgba(25, 255, 255, 1)';

info_btn.click(function() {
	if (!info_bar.already_fetched) {
		var article = extract_article();
		$.ajax('https://api.newsalyzer.org/get-sentiment', {
			'data': article,
			'contentType': 'text',
			'processData': false,
			'type': 'POST',
			'success': function(data, textStatus, jqxhr) {
				let jsonData = JSON.parse(data);
				let table = $('<table>');
				table.appendTo(info_container);
				let header = $('<tr>');
				$('<th>').css(entity_header_css).text('').appendTo(header);
				$('<th>').css(entity_header_css).text('Entity').appendTo(header);
				$('<th>').css(entity_header_css).text('Sentiment').appendTo(header);
				header.appendTo(table);
				for(let entity of jsonData.entities) {
					let entity_icon = get_entity_icon(entity.type);
					if (entity_icon) {
						let tr = $('<tr>');
						let icon_td = $('<td>').css(entity_icon_css).appendTo(tr);
						$('<i>').attr('class',entity_icon).appendTo(icon_td);
						$('<td>').css(entity_name_css).text(entity.name).appendTo(tr);
						let sentiment_td = $('<td>').appendTo(tr);
						let sentiment_point = 50 + entity.sentiment * 50;
						let color_text = negative_color + ' 0%, ';
						color_text += marker_color + ' ' + sentiment_point +'%, ';
						color_text += marker_color + ' ' + (sentiment_point + 1) + '%, ';
						color_text += positive_color + ' 100%';
						let entity_value_css = {
							background: '-moz-linear-gradient(left, ' + color_text + ')', /* FF3.6-15 */
							background: '-webkit-linear-gradient(left, ' + color_text + ')', /* Chrome10-25,Safari5.1-6 */
							background: 'linear-gradient(to right, ' + color_text + ')',
							'margin-top': '2px',
							'margin-bottom': '2px',
							'border-radius': '2px',
							height: '16px',
							width: '100%'
						}
						$('<div>').attr('title', 'Sentiment Score: ' + entity.sentiment).css(entity_value_css).appendTo(sentiment_td);
						tr.appendTo(table);
					}
				}

				info_bar.already_fetched = true;
			}
		}); 
	}
	if (info_bar.is(':visible')) {
		info_bar.hide();
	} else {
		info_bar.show();
	}
});