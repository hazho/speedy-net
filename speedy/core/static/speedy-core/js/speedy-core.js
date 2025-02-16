function init_datepicker() {
    var dobDpElem = this.$("#id_date_of_birth").clone();
    dobDpElem.attr('id', 'id_date_of_birth_dp');
    dobDpElem.attr('name', 'date_of_birth_dp');
    this.$("#id_date_of_birth").after(dobDpElem);
    this.$("#id_date_of_birth").attr('type', 'hidden');
    this.$("#id_date_of_birth").removeAttr('class');
    this.$("#id_date_of_birth").removeAttr('required');
    this.$("#id_date_of_birth_dp").datepicker(datepicker_options);
    var dob = $.datepicker.parseDate('yy-mm-dd', this.$("#id_date_of_birth").val());
    this.$("#id_date_of_birth_dp").datepicker('setDate', dob);
}

var datepicker_options = {
    altField: "#id_date_of_birth",
    altFormat: 'yy-mm-dd',
    changeMonth: true,
    changeYear: true,
    minDate: '-185y+1d',
    maxDate: '+3y+0d',
    yearRange: '-185:+3',
    defaultDate: '+2y+0d'
};

$.datepicker.regional.he = {
    closeText: "סגור",
    prevText: "&#x3C;הקודם",
    nextText: "הבא&#x3E;",
    currentText: "היום",
    monthNames: ["ינואר", "פברואר", "מרץ", "אפריל", "מאי", "יוני", "יולי", "אוגוסט", "ספטמבר", "אוקטובר", "נובמבר", "דצמבר"],
    monthNamesShort: ["ינואר", "פברואר", "מרץ", "אפריל", "מאי", "יוני", "יולי", "אוגוסט", "ספטמבר", "אוקטובר", "נובמבר", "דצמבר"],
    dayNames: ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"],
    dayNamesShort: ["א'", "ב'", "ג'", "ד'", "ה'", "ו'", "שבת"],
    dayNamesMin: ["א'", "ב'", "ג'", "ד'", "ה'", "ו'", "שבת"],
    weekHeader: "Wk",
    dateFormat: "d בMM yy",
    firstDay: 0,
    isRTL: true,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.en = {
    monthNames: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    // monthNamesShort: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    dateFormat: "d MM yy",
    firstDay: 0
};

$.datepicker.setDefaults($.datepicker.regional[$('html').attr('lang')]);

evil.block('@@RegistrationForm', {

    _generateSlug: function () {
        var components = [this.firstNameField.val(), this.lastNameField.val()];
        components = components.filter(function (i) {
            return i
        });
        var slug = components.join('_');
        slug = slug.toLowerCase();
        slug = slug.replace(' ', '_');
        slug = slug.replace(/[^\x00-\x7F]/g, '');
        return slug;
    },

    init: function () {
        this.slugField = this.$('#id_slug');
        this.firstNameField = this.$('#id_first_name');
        this.lastNameField = this.$('#id_last_name');
        this.slugChanged = (this.slugField.val() != this._generateSlug());
        init_datepicker();
    },

    'change on #id_slug': function () {
        this.slugChanged = true;
    },

    'keyup on #id_first_name, #id_last_name': function () {
        if (!this.slugChanged) {
            this.slugField.val(
                this._generateSlug()
            );
        }
    }

});


evil.block('@@ProfileForm', {
    init: init_datepicker
});


evil.block('@@AutoForm', {
    'change on select': function () {
        this.$('form').submit();
    }
});


evil.block('@@MessageList', {
    init: function () {
        var _this = this;
        if (this.block.data('page-number') === 1) {
            window.setInterval(function () {
                _this.poll();
            }, 5000);
        }
    },

    poll: function () {
        var _this = this;
        if (this.block.data('page-number') === 1) {
            if (!((window.localStorage !== null) && (window.localStorage.getItem('logged-in') === 'false'))) {
                var url = this.block.data('poll-url');
                var since = this.$('@message').first().data('timestamp');
                url += '?since=' + since;
                $.ajax(url).done(function (data) {
                    $(data).prependTo(_this.block);
                }).fail(function (jqXHR) {
                    if ((jqXHR.status === 403) && (window.localStorage !== null)) {
                        window.localStorage.setItem('logged-in', 'false');
                    }
                });
            }
        }
    }
});


evil.block('@@Uploader', {

    blankState: function () {
        this.progress.hide();
        this.filename.hide();
        this.browseButton.show();
    },

    boundState: function () {
        this.blankState();
        this.filename.show();
    },

    progressState: function () {
        this.progress.show();
        this.progressBar.width(0);
        this.filename.hide();
        this.browseButton.hide();
    },

    startUpload: function (file) {
        var _this = this;
        this.progressState();
        var data = new FormData();
        data.append('file', file);
        $.ajax({
            url: this.block.data('action'),
            type: 'POST',
            data: data,
            processData: false,
            contentType: false,
            xhr: function () {
                var xhr = $.ajaxSettings.xhr();
                if (xhr.upload) {
                    xhr.upload.addEventListener('progress', function (evt) {
                        var percent = Math.round(evt.loaded / evt.total * 100);
                        _this.progressBar.css('width', percent + '%');
                        if (percent == 100) {
                            _this.progressBar.addClass('active');
                            _this.progress.addClass('progress-striped');
                        } else {
                            _this.progressBar.removeClass('active');
                            _this.progress.removeClass('progress-striped');
                        }
                    }, false);
                }
                return xhr;
            }
        }).done(function (data, textStatus, jqXHR) {
            _this.boundState();
            _this.filename.text(data.files[0].name);
            _this.realInput.val(data.files[0].uuid);
        }).fail(function (jqXHR, textStatus, errorThrown) {
            var data = jqXHR.responseJSON;
            for (var errorField in data) {
                if (data.hasOwnProperty(errorField)) {
                    alert(data[errorField]);
                    _this.blankState();
                    break;
                }
            }
        });
    },

    init: function () {
        if (this.realInput.val()) {
            this.boundState();
        } else {
            this.blankState();
        }
    },

    'click on @browseButton': function (event) {
        event.preventDefault();
        this.fileInput.trigger('click');
    },

    'change on @fileInput': function (event) {
        event.preventDefault();
        files = this.fileInput[0].files;
        if (files.length) {
            this.startUpload(files[0]);
        }
    }

});

window.speedy = {};

window.speedy.setSession = function (domain, key) {
    $.ajax({
        url: '//' + domain + '/set-session/',
        method: 'post',
        data: {
            key: key
        },
        xhrFields: {
            withCredentials: true
        }
    });
};

$(document).ready(function () {
    $(".form-control-danger").addClass("is-invalid"); // A hack to work with django-crispy-forms 1.6.1.

    $('form[method="post"]').submit(function () {
        $(this).find(':input[type="submit"]').prop('disabled', true);
    });
});

var isRTL = $("body").hasClass("bidi-rtl");
if (isRTL) {
    Popper.Defaults.modifiers.preventOverflowRTL = {
        enabled: true,
        order: 301, // preventOverflow order: 300
        fn: (data) => {
            var preventOverflow = data.instance.modifiers.find(modifier => modifier.name == 'preventOverflow');
            var isOverflowLeft = data.popper.width > data.offsets.reference.width + Math.abs(preventOverflow.boundaries.left);
            if (isOverflowLeft) {
                left = Math.floor(preventOverflow.boundaries.left);
                data.styles['left'] = left;
                data.styles['right'] = 'auto';
            } else {
                data.styles['left'] = '';
                data.styles['right'] = '';
            }
            return data;
        }
    };

    Popper.Defaults.modifiers.computeStyleRTL = {
        enabled: true,
        order: 851, // computeStyle order: 850
        fn: (data) => {
            var left = -Math.floor(data.popper.left); // RTL
            var top = Math.floor(data.popper.top);
            data.styles['transform'] = `translate3d(${left}px, ${top}px, 0)`;
            return data;
        }
    };
}

