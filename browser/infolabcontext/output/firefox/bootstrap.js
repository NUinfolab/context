var Cc = Components.classes;
var Ci = Components.interfaces;
var Cu = Components.utils;
var Cm = Components.manager;
var Cr = Components.results;

Cu['import']('resource://gre/modules/Services.jsm');
Cu['import']('resource://gre/modules/AddonManager.jsm');
Cu['import']('resource://gre/modules/FileUtils.jsm');

function log(str) {
    Services.console.logStringMessage(str)
}

var extensionContext = {

    XHTML_NS: 'http://www.w3.org/1999/xhtml',

    XMLHttpRequest: function() {
        return Cc['@mozilla.org/xmlextras/xmlhttprequest;1'].createInstance(Ci.nsIXMLHttpRequest);
    },

    alert: function(str) {
        Services.prompt.alert(null, 'Kango', str);
    },

    log: log
};

function getExtensionInfo(data) {
    var req = Cc['@mozilla.org/xmlextras/xmlhttprequest;1'].createInstance(Ci.nsIXMLHttpRequest);
    req.open('GET', data.resourceURI.spec + 'extension_info.json', false);
    req.overrideMimeType('text/plain');
    req.send(null);
    return JSON.parse(req.responseText);
}

function loadModules(addon, context, info) {
    var modules = [
        'kango/base.js',
        'kango/utils.js',
        'kango/kango.js',
        'kango/console.js',
        'kango/timer.js',
        'kango/lang.js',
        'kango/chrome_windows.js',
        'kango/messaging.js',
        'kango/io.js',
        'kango/xhr.js',
        'kango/storage.js',
        'kango/browser.js',
        'kango/i18n.js',
        'kango/userscript_engine.js',
        'kango/userscript_client.js',
        'kango/invoke_async.js',
        'kango/message_target.js',
        'kango/backgroundscript_engine.js',
        'kango-ui/ui_base.js',
        'kango-ui/browser_button.js',
        'kango-ui/options.js',
        'kango-ui/context_menu.js',
        'kango-ui/notifications.js',
        'kango/legacy.js'
    ];

    if (typeof info.modules != 'undefined') {
        modules = modules.concat(info.modules);
    }

    for (var i = 0; i < modules.length; i++) {
        Services.scriptloader.loadSubScript(addon.getResourceURI(modules[i]).spec, context, 'UTF-8');
    }
}

function init(startupData) {
    AddonManager.getAddonByID(startupData.id, function(addon) {
        var info = getExtensionInfo(startupData);
        loadModules(addon, extensionContext, info);
        extensionContext.kango.__installPath = startupData.installPath;
        extensionContext.kango.init(info);
    });
}

// bootstrap.js required exports

function install(data, reason) {
}

function uninstall(data, reason) {
    if (reason == ADDON_UNINSTALL) {
        var info = getExtensionInfo(data);

        var context = {
            kango: {
                getExtensionInfo: function() {
                    return info;
                },

                registerModule: function() {
                },

                getDefaultModuleRegistrar: function() {
                }
            }
        };

        var modules = [
            'kango/utils.js',
            'kango/storage.js',
            'kango/uninstall.js'
        ];

        for (var i = 0; i < modules.length; i++) {
            Services.scriptloader.loadSubScript(data.resourceURI.spec + modules[i], context, 'UTF-8');
        }
    }
}

function startup(startupData, reason) {
    if (Services.vc.compare(Services.appinfo.platformVersion, '10.0') < 0) {
        Cm.addBootstrappedManifestLocation(startupData.installPath);
    }

    var hiddenWindowReady = true;
    try {
        var hiddenDOMWindow = (Services.appShell || Cc['@mozilla.org/appshell/appShellService;1'].getService(Ci.nsIAppShellService)).hiddenDOMWindow;
    }
    catch (e) {
        hiddenWindowReady = false;
    }
    if (hiddenWindowReady) {
        init(startupData);
    } else {
        var onFinalUiStartup = function(subject, topic, data) {
            Services.obs.removeObserver(onFinalUiStartup, 'final-ui-startup', false);
            init(startupData);
        };
        Services.obs.addObserver(onFinalUiStartup, 'final-ui-startup', false);
    }
}

function shutdown(data, reason) {
    if (reason != APP_SHUTDOWN) {
        extensionContext.kango.dispose();
        extensionContext = null;
        if (Services.vc.compare(Services.appinfo.platformVersion, '10.0') < 0) {
            Cm.removeBootstrappedManifestLocation(data.installPath);
        }
    }
}