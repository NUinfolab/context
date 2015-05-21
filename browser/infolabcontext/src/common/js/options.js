
KangoAPI.onReady(function() {
    var apps = kango.storage.getItem('applications');
    var appsUl = $('#application-list');
    $.each(apps, function(slug, settings) {
      var checked = settings['active'] ? 'checked' : '';
      appsUl.append('<li><input type="checkbox" name="application-active" value="' + slug + '" ' + checked + '>' + settings['name'] + '</input></li>');
    });

    $('input[name="application-active"]').change(function() {
      var input = $(this);
      apps[input.val()]['active'] = input.prop('checked');
      kango.storage.setItem('applications', apps);
    });
});
