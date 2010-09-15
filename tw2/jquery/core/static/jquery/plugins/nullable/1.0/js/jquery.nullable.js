/*!
 * jQuery nullable plugin v1.0
 * http://bitbucket.org/josephtate/
 *
 * Released: 2009-12-03
 * Version: 1.0
 *
 * Copyright (c) 2009 Joseph Tate, MVP
 * Dual licensed under the MIT and GPL licenses.
 * http://docs.jquery.com/License
 */
(function($) {
	$.nullable = {
        css_class: 'nullable',
        checked_class: 'chk_on'
	};

    $.toggle_null = function(elem, selector, checked_class) {
        if (jQuery(elem).hasClass(checked_class)) {
            jQuery(selector + '[name=' + elem.name + ']').removeClass(checked_class);
            jQuery(elem).attr('checked', null);
        }
        else {
            jQuery(selector + '[name=' + elem.name + ']').removeClass(checked_class);
            jQuery(elem).addClass(checked_class).attr('checked', 'checked');
        }
    };

	$.fn.nullable = function(selector, checked_class) {
        if (! selector) {
            selector = '.' + $.nullable.css_class;
        }
        if (! checked_class) {
            checked_class = $.nullable.checked_class;
        }
        $(this).find(selector).click(function(evt) {
            $.toggle_null(this, selector, checked_class);    
        });
        // Mark all the currently marked items with the class
        $(this).find(selector).filter(':checked').addClass(checked_class);
        return this;
	};
})(jQuery);

//Automatically register the default
jQuery(document).ready(function(evt) {
    jQuery(document).nullable();
});
