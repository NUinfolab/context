var utils=require("kango/utils"),NotImplementedException=utils.NotImplementedException;function IOptionsPage(){}IOptionsPage.prototype={open:function(){throw new NotImplementedException;}};function getPublicApi(){return utils.createApiWrapper(module.exports,IOptionsPage.prototype)};








var extensionInfo=require("kango/extension_info"),utils=require("kango/utils"),browser=require("kango/browser"),io=require("kango/io"),chromeWindows=require("kango/chrome_windows"),array=utils.array;function OptionsPage(){var b=this._optionsUrl=io.getExtensionFileUrl(extensionInfo.options_page).toLowerCase();browser.addEventListener("DocumentLoaded",function(a){0==a.url.toLowerCase().indexOf(b)&&(a.window.__kango_require=require,a.window.__kango_optionsPageMode=!0)})}
OptionsPage.prototype={dispose:function(){this.close()},open:function(b){if(""!=this._optionsUrl){var a=this._optionsUrl;"undefined"!=typeof b&&(a+="#"+b);browser.tabs.create({url:a,focused:!0,reuse:!0});return!0}return!1},close:function(){var b=this._optionsUrl;if(""!=b)for(var a=chromeWindows.getMostRecentChromeWindow().gBrowser,c=0;c<a.browsers.length;c++)if(0==a.getBrowserAtIndex(c).currentURI.spec.indexOf(b)){a.removeTab(a.tabContainer.childNodes[c]);break}}};
extensionInfo.options_page&&(module.exports=new OptionsPage,module.exports.getPublicApi=getPublicApi);
