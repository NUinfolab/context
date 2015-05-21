function currentTabNavigate(url) {
    kango.browser.tabs.getCurrent(function(tab) {
        KangoAPI.closeWindow();
        tab.navigate(url);
    });
}

var DEFAULT_APPS = {
  'url-search': {
    name: 'URL Search',
    path: 'url',
    active: true
  },
  'content': {
    name: 'Content',
    path: 'content',
    active: true
  },
  'keywords': {
    name: 'Keywords',
    path: 'keywords',
    active: true
  },
  'entities': {
    name: 'Entities',
    path: 'entities',
    active: true
  },
  'topic': {
    name: 'Topic',
    path: 'topic',
    active: true
  },
  'stakeholders': {
    name: 'Stakeholders',
    path: 'stakeholders',
    active: true
  },
  'stakeholder-tweets': {
    name: 'Stakeholder Tweets',
    path: 'stakeholdertweets',
    active: true
  },
  'reddits': {
    name: 'Reddits',
    path: 'reddits',
    active: true
  },
  'categories': {
    name: 'Categories',
    path: 'categories',
    active: true
  },
  'pundit-tweets': {
    name: 'Pundit Tweets',
    path: 'pundittweets',
    active: true
  }
}

KangoAPI.onReady(function(event) {   
    // Multiple ready events are fired on FF, due to twttr.widgets.load()
    if(KangoAPI._readyFired) {
        return;
    }

    var apps = kango.storage.getItem('applications');
    if (apps === null) {
      apps = DEFAULT_APPS;
      kango.storage.setItem('applications', apps);
    }
    var appsUl = $('#application-links');
    $.each(apps, function(slug, settings) {
      if (settings['active']) {
        appsUl.append('<li><a class="context-link" href="' + settings['path'] + '">' + settings['name'] + '</a></li>');
      }
    });
        
    $('#infolab_link').click(function(event) {
        currentTabNavigate('http://infolab.northwestern.edu');
    });
    
    $('.context-link').click(function() {
      var href = $(this).attr('href');
      var info = kango.getExtensionInfo();
      kango.browser.tabs.getCurrent(function(tab) {
        var url = info.base_url + href + '?url=' + tab.getUrl();
        kango.browser.windows.create({
          url: url, width: 400, modal: true, chrome: true
        });
      });
      return false;
    });

    $('#options-link').click(function() {
      kango.ui.optionsPage.open();
      return false;
    });
});
