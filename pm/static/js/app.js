var page = {
	init: function ($) {
    	// load initial search for default page
    	if ($('.stream-loading-graphic').length) {
    	    var _get = window.location.search.replace('?q=', '');
    		page.search(_get);
    	}

        // click add button
        $('.mdi-content-add').on('click', function() {
            var $add_card = $('.add-card');
            $add_card.find('.mdi-navigation-close').unbind('click');
			
            var _scrolltop = $(window).scrollTop();
            // add button click so relocate to top of visible list
            $('.card:visible').each(function(){
                if ($(this).offset().top > _scrolltop) {
                    $add_card.remove();
                    $(this).before($add_card);
                    $add_card.find('.datepicker').pickadate({
                        selectMonths: true,
                        selectYears: 5
                    });
                    return false;
                }
            });
			
            $add_card.slideToggle(function () {
            	$(this).find('select').show();
            }).find('.mdi-navigation-close').on('click', function () {
                $add_card.slideToggle();
            });
        });

    	// click search button
        $('.mdi-action-search').on('click', function () {
            var $search_card = $('.search-card');
            $search_card.find('.mdi-navigation-close, .mdi-content-filter-list').unbind('click');

            var _scrolltop = $(window).scrollTop();
            // add button click so relocate to top of visible list
            $('.card:visible').each(function () {
                if ($(this).offset().top > _scrolltop) {
                    $search_card.remove();
                    $(this).before($search_card);
                    $search_card.find('.datepicker').pickadate({
                        selectMonths: true,
                        selectYears: 5
                    });
                    return false;
                }
            });

            $search_card.slideToggle(function () {
                $(this).find('select').show();
            }).find('.mdi-navigation-close').on('click', function () {
                $search_card.slideToggle();
            });

            $search_card.on('click', '.mdi-content-filter-list', function () {
                $search_card.find('p').slideToggle();
            }).on('change', '.filter_select', function () {
                var _val = $(this).val(),
                    _q_input = $search_card.find('[name=q]');

                var _current_val = _q_input.val();
                if (_current_val) _current_val = _current_val+',';
                _q_input.val(_current_val+_val);
            });
        });

		// hash change / hash link click
        $(window).on('hashchange', function () {
        	var _id = document.location.hash.replace('#task:', '');
        	if (_id) page.get_card(_id);
        });

    	// tag stuff
        $('.tag-card').on('click', '.activator', function () {
        	$(this).parents('.tag-card').animate({ 'height': '240px' }).addClass('z-depth-3');
        }).on('click', '.mdi-navigation-close', function() {
        	$(this).parents('.tag-card').removeAttr('style').removeClass('z-depth-3');
        });

		// notifications
        $('.js-dismiss').click(function (e) {
        	// animation

        	// ping backend

        });
	},
	select_card: function ($card) {
		// focus on card
		var $prgrs = $card.find('.progress'),
			$slug = $card.find('.card-slug');

		// show loader
		$prgrs.show();

		// load data if necessary
		if (!$card.hasClass('card-loaded')) {
			var _id = $card.attr('data-id');
			$.get(encodeURIComponent(_id) + '/', function (d) {
				// insert before the progress bar
				$prgrs.before(d);
				$card.find('select').show();

				// set data & class flag
				$card.addClass('card-loaded');
				var $card_content = $slug.next('.card-content');
				$card_content.slideDown();
				$slug.slideUp(300);

				// set shadow class & hide loader
				$card.addClass('z-depth-3').addClass('focused');
				$prgrs.hide();
			});
		} else {
			$card.find('.card-content').slideDown();
			$slug.slideUp(300);

			// set shadow class & hide loader
			$card.addClass('z-depth-3');
			$prgrs.hide();
		}

		// scroll to selected
		$('html, body').animate({
			'scrollTop': $card.offset().top - 80
		}, 500);
	},
    search: function (q) {
    	var _ldng_grphc = $('.stream-loading-graphic'),
    		_strm_container = $('.stream-container');
    	_strm_container.empty();
    	_ldng_grphc.show();

    	if (q === undefined) q = '';

    	$.get('search/?q=' + encodeURIComponent(q), function (d) {
    		_ldng_grphc.hide();
    		_strm_container.html(d)

    		// register card events for items that have been added
    		$('.container').on('click', '.card .card-slug', function () {
    			page.select_card($(this).parent());
    		}).on('click', '.unfocus-card', function () {
    			// un-focus on card
    			$card = $(this).parents('.card');
    			$card.find('.card-content').slideUp(300);
    			$card.find('.card-slug').slideDown(300);
    			$card.removeClass('z-depth-3');
    		}).on('submit', '.add-card form', function (e) {
    			e.preventDefault();

    			if (!$(this).find('.btn').hasClass('disabled')) {
    				$(this).find('.btn').addClass('disabled');

    				var _url = $(this).attr('action'),
						_data = $(this).serialize(),
    					_container = $(this).parents('.add-card'),
						_this = $(this);

    				$.post(_url, _data, function (d) {
    					_container.after(d);
    					_this.find('input, textarea').val('');
    				});
    			}
    		}).on('submit', '.js-edit-card form', function (e) {
    			e.preventDefault();
    			var _this = $(this),
					_action = $(this).attr('action'),
    				_data = $(this).serialize();

    			$.post(_action, _data, function (d) {
    				var _card = _this.parents('.card');
    				_card.find('.card-content, .card-reveal').remove();
    				_card.find('.card-slug').after(d);
    				_card.find('.card-content').show();
    			});
    		}).on('focusin', '.add-comment textarea', function () {
    			// add comment init
    			var _this = $(this);
    			_this.prev('label').fadeOut();
    			_this.next('input[type=submit]').fadeIn();
    		}).on('submit', '.add-comment form', function (e) {
    			e.preventDefault();

    			if (!$(this).find('.btn').hasClass('disabled')) {
    				$(this).find('.btn').addClass('disabled');

    				var _url = $(this).attr('action'),
						_data = $(this).serialize(),
    					_container = $(this).parents('.collection');

    				$.post(_url, _data, function (d) {
    					_container.replaceWith(d);
    				});
    			}
    		});

    		// init date pickers
    		$('.datepicker').pickadate({
    			selectMonths: true,
    			selectYears: 5
    		});

    		// load selected if specified
    		var _id = document.location.hash.replace('#task:', '');
    		if (_id) page.get_card(_id);
    	});
    },
    'get_card': function (_id) {
    	var $cards = $('.card'),
    		_found = false;

    	for (var i = 0; i < $cards.length; ++i) {
    		if ($($cards[i]).attr('data-id') == _id) {
    			page.select_card($($cards[i]));
    			_found = true;
    		}
    	}

    	if (!_found) {
    		var $add_card = $('.add-card');
    		$add_card.after('<div class="card" data-id="' + _id + '"><div class="card-slug"></div><div class="progress"><div class="indeterminate"></div></div></div>');
    		page.select_card($add_card.next());
    	}
    }
}

$(document).ready(function(){
    page.init($);
});
