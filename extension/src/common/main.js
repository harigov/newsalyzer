// ==UserScript==
// @name Newsalyzer
// @include http://*
// @include https://*
// @require jquery-1.9.1.min.js
// ==/UserScript==
var $ = window.$ || $;
var jQuery = jQuery || $;

// just in case if a website is doing something crazy
if ($) {
    // make sure that none of our code executes till the page is loaded
    $(function() {
      $('<link>')
      .attr('rel',"stylesheet")
      .attr('href',"https://netdna.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css")
      .appendTo($('head'));
      
      var info_btn = $('<div>').css({
                                    position: 'absolute',
                                    top: '80px',
                                    left: document.body.clientWidth - 70 + 'px',
                                    height: '40px',
                                    width: '40px',
                                    color: 'aqua',
                                    'text-align': 'center',
                                    background: 'rgba(255, 255, 255, 0.85)',
                                    'border-style': 'solid',
                                    'border-color': 'black',
                                    'border-width': '1px',
                                    'box-shadow': '3px 3px 3px rgba(0, 0, 0, 0.3)',
                                    'background-size': 'contain',
                                    'z-index': '2147483647',
                                    display: 'hidden'
                                    }).appendTo(document.body);
      $('<img>').attr('src', kango.io.getResourceUrl('icons/info.png')).css({ 'height': '36px', 'margin-top': '2px' }).appendTo(info_btn);
      
      var info_bar = $('<div>').css({
                                    position: 'absolute',
                                    top: '120px',
                                    height: '500px',
                                    left: document.body.clientWidth - 330 + 'px',
                                    width: '300px',
                                    background: 'rgba(255, 255, 255, 0.85)',
                                    'border-style': 'solid',
                                    'border-color': 'black',
                                    'border-width': '1px',
                                    'box-shadow': '3px 3px 3px rgba(0, 0, 0, 0.3)',
                                    'z-index': '2147483647',
                                    'display': 'none',
                                    'overflow-y': 'scroll'
                                    }).appendTo(document.body);
      
      var info_container = $('<div>').css({
                                          margin: '15px'
                                          }).appendTo(info_bar);
      
      let sentiment_container_css = {
      'overflow-y': 'scroll',
      height: '200px',
      width: '100%'
      }
      
      let header_css = {
      'text-align': 'center',
      'margin-bottom': '10px',
      'font-size': '16px',
      'font-family': 'Arial, Helvetica, sans-serif'
      };
      
      let read_time_css = {
      'text-align': 'center',
      'margin-bottom': '10px',
      'font-size': '13px',
      'font-family': 'Arial, Helvetica, sans-serif'
      };
      
      let entity_icon_css = {
      'font-size': '12px',
      color: 'white',
      'text-align': 'left',
      'padding-left': '5px'
      };
      
      let entity_name_css = {
      color: 'white',
      'font-size': '12px',
      'font-family': 'Arial, Helvetica, sans-serif',
      'text-align': 'left',
      'padding-top': '2px'
      };
      
      let sentiment_label_css = {
      'font-family': 'Arial, Helvetica, sans-serif',
      'font-size': '10px'
      }
      
      function get_entity_icon(entity_type) {
      if (entity_type==='PERSON') {
      return 'fa fa-user';
      } else if (entity_type==='ORGANIZATION') {
      return 'fa fa-sitemap';
      } else if (entity_type==='LOCATION') {
      return 'fa fa-globe';
      }
      }
      
      let positive_color = 'rgba(2, 39, 65, 1)';
      let negative_color = 'rgba(19, 122, 212, 1)';
      
      info_btn.click(function() {
                     if (info_bar.is(':visible')) {
                     info_bar.hide();
                     } else {
                     info_bar.show();
                     }
                     });
      
      if (!info_bar.already_fetched) {
      let url = window.location.href.split('?')[0];
      url = encodeURIComponent(url);
      $.ajax('https://api.newsalyzer.org/get-sentiment?url='+url, {
             'contentType': 'text',
             'processData': false,
             'type': 'GET',
             'success': function(data, textStatus, jqxhr) {
             $('<div>').text('Newsalyzer Analysis').css(header_css).appendTo(info_container);
             let jsonData = JSON.parse(data);
             let read_time_div = $('<div>').appendTo(info_container);
             $('<span>').css(read_time_css).text('Time to read: ' + (json_data.word_count * 1.0 / 250) + ' mins').appendTo(read_time_div);
             let table = $('<table>');
             let sentiment_container = $('<div>').css(sentiment_container_css).appendTo(info_container);
             let labels_div = $('<div>').attr('class', 'row').appendTo(sentiment_container);
             $('<span>').text('Negative Sentiment').css({float: 'left'}).css(sentiment_label_css).appendTo(labels_div);
             $('<span>').text('Positive Sentiment').css({float: 'right'}).css(sentiment_label_css).appendTo(labels_div);
             table.appendTo(sentiment_container);
             for(let entity of jsonData.sentiment.entities) {
             let entity_icon = get_entity_icon(entity.type);
             if (entity_icon) {
             let tr = $('<tr>');
             let sentiment_point = 50 + entity.sentiment * 50;
             let color_text = negative_color + ' 0%, ';
             color_text += negative_color + ' ' + (sentiment_point - 5) +'%, ';
             color_text += positive_color + ' ' + (sentiment_point + 5) + '%, ';
             color_text += positive_color + ' 100%';
             let entity_value_css = {
             background: '-moz-linear-gradient(left, ' + color_text + ')', /* FF3.6-15 */
             background: '-webkit-linear-gradient(left, ' + color_text + ')', /* Chrome10-25,Safari5.1-6 */
             background: 'linear-gradient(to right, ' + color_text + ')',
             'margin-top': '2px',
             'margin-bottom': '2px',
             'border-radius': '2px',
             'border-color': 'rgba(255, 255, 255, 0.85)',
             'border-style': 'solid',
             height: '16px',
             width: '100%'
             }
             tr.css(entity_value_css);
             let icon_td = $('<td>').css(entity_icon_css).appendTo(tr);
             $('<i>').attr('class',entity_icon).appendTo(icon_td);
             $('<td>').css(entity_name_css).text(entity.name).appendTo(tr);
             // $('<td>').text(entity.sentiment).appendTo(tr);
             tr.appendTo(table);
             }
             }
             
             info_btn.show();
             info_bar.already_fetched = true;
             },
             'error': function(err) {
             info_btn.hide();
             console.log('Failed to fetch sentiment data for the article');
             }
             }); 
      }
      });
}