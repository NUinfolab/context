(function(e){var f=function(c){var a=c("kango/core").createApiInstance("popup");"undefined"!=typeof window.addEventListener?window.addEventListener("unload",function(){a.clear()},!1):window.attachEvent("onunload",function(){a.clear()});return a.obj};e.KangoAPI=new function(){var c=[],a=!1;this.onReady=function(b){a?b():c.push(b)};this.closeWindow=function(){};this.resizeWindow=function(b,a){};this.getBackgroundPage=function(){};this._fireReady=function(){if(KangoAPI.getBackgroundPage()){var b=KangoAPI._require("kango/utils").object;
b.forEach(f(KangoAPI._require),function(a,b){window[b]=a})}for(var d=0;d<c.length;d++)c[d]();a=!0;delete this._fireReady;delete this._require;b&&b.freeze(this)}}})(window);








window.addEventListener("DOMContentLoaded",function(){var a=window.__kango_require;delete window.__kango_require;var c=window.__kango_optionsPageMode;delete window.__kango_optionsPageMode;KangoAPI.getBackgroundPage=function(){return a("kango/backgroundscript_engine").getDOMWindow()};KangoAPI._require=function(b){return a(b)};KangoAPI.closeWindow=function(){c?a("kango-ui/options").close():a("kango-ui/browser_button").closePopup()};KangoAPI.resizeWindow=function(b,d){c||a("kango-ui/browser_button").resizePopup(b,
d)};KangoAPI._fireReady()},!1);
