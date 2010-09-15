/*!
 * jQuery switchView Plugin v1.2
 * http://jdsharp.com/jquery-plugins/switchview/
 *
 * Released: 2009-11-20
 * Version: 1.2
 *
 * Copyright (c) 2009 Jonathan Sharp, Out West Media LLC.
 * Dual licensed under the MIT and GPL licenses.
 * http://docs.jquery.com/License
 */
/*
 * .view-hidden { display: none; }
 */
(function($) {
	$.switchView = {
		hidden: 'view-hidden',
		prefix: 'view-on-',
		group: 	'view-group-'
	};
	function undash(str) {
		return 	$.map(str.split('-'), function(v, i) {
					return ( i > 0 ? v.substr(0, 1).toUpperCase() + v.substr(1).toLowerCase() : v.toLowerCase() );
				}).join('');
	}
	function dashed(str) {
		return str.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase();
	}
	$.fn.switchView = function(view) {
		var group = '';
		if ( view.indexOf('.') > -1 ) {
			// We have a group also associated with this:
			var parts = view.split('.');
			group = dashed(parts[0]);
			view = parts[1];
		}
	
		var elements = [];
		if ( group == '' ) {
			$(this).find('[class*=' + $.switchView.prefix + ']').each(function() {
				if ( !$(this).is('[class*=' + $.switchView.group + ']') ) {
					if ( $(this).parents('[class*=' + $.switchView.group + ']').length == 0 ) {
						elements.push( this );
					}
				}
			});
		} else {
			// There are two scenarios here
			// The first case is a "view-group-{foo} view-on-{bar}"
			// The second case is "view-group-{foo}" -> child "view-on-{bar}"
			$(this).find('.' + $.switchView.group + group).each(function() {
				if ( $(this).is('[class*=' + $.switchView.prefix + ']') ) {
					elements.push( this );
				} else {
					$(this).find('[class*=' + $.switchView.prefix + ']').each(function() {
						elements.push( this );
					});
				}
			});
		}
		
		view = dashed(view);
		var show = [];
		var reg = new RegExp('(^|\\s+)' + $.switchView.prefix + view + '(\\s+|$)');
		$(elements).filter(function() {
			return !( reg.test(this.className) && show.push(this) );
		})
		.addClass( $.switchView.hidden );
		$(show).removeClass( $.switchView.hidden );
		$(document).trigger('switchview', [ undash(view), $.switchView.prefix + view, 
											undash(group), ( group != '' ? $.switchView.group + group : '' ) ]);
		return this;
	};
})(jQuery);