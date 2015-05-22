var NotImplementedException=require("kango/utils").NotImplementedException;function LangBase(){}LangBase.prototype={evalInSandbox:function(e,a){throw new NotImplementedException;},evalScriptsInSandbox:function(e,a){for(var b="",c=0;c<a.length;c++){for(var d=0;d<a[c].requires.length;d++)b+=a[c].requires[d].text+"\n\n";b+=a[c].text+"\n\n"}return this.evalInSandbox(e,b)}};








var extensionInfo=require("kango/extension_info"),utils=require("kango/utils"),object=utils.object,array=utils.array,browser=require("kango/browser"),chromeWindows=require("kango/chrome_windows"),io=require("kango/io"),console=require("kango/console");function HTMLSandbox(){this._browserId="kango-background-script-host_"+utils.utils.getDomainFromId(extensionInfo.id);this._frameEventListener=null}
HTMLSandbox.prototype={create:function(a,c,d){var b=chromeWindows.getHiddenWindow(),e=b.document.createElementNS("http://www.w3.org/1999/xhtml","iframe");e.setAttribute("type","chrome");e.setAttribute("id",this._browserId);this._frameEventListener=function(a){var b=a.target.defaultView.wrappedJSObject;b.onunload=function(){d(b)};c(b)};e.addEventListener("DOMContentLoaded",this._frameEventListener,!1);e.setAttribute("src",io.getExtensionFileUrl(a));b.document.documentElement.appendChild(e)},dispose:function(){var a=
chromeWindows.getHiddenWindow().document.getElementById(this._browserId);a.removeEventListener("DOMContentLoaded",this._frameEventListener,!1);a.parentNode.removeChild(a)}};function Lang(){}
Lang.prototype=object.extend(LangBase,{_executeScript:function(a,c){try{null!=a.path?Services.scriptloader.loadSubScript(a.path,c,"UTF-8"):Cu.evalInSandbox(a.text,c,"default",a.path,1)}catch(d){console.reportError(d,a.path)}},exposeObject:function(a,c,d){if(0<=Services.vc.compare(Services.appinfo.platformVersion,"34"))return Cu.cloneInto(a,d,{cloneFunctions:!0});c=c||"r";a.__exposedProps__=a.__exposedProps__||{};for(var b in a)"__exposedProps__"!=b&&a.hasOwnProperty(b)&&(a.__exposedProps__[b]=c,a[b]&&
object.isObject(a[b])&&this.exposeObject(a[b],c,d));return a},createHTMLSandbox:function(a,c,d){var b=new HTMLSandbox;b.create(a,c,d);return b},evalScriptsInSandbox:function(a,c,d){var b=browser.getSandboxForWindow(a,d);array.forEach(c,function(a){array.forEach(a.requires,function(a){this._executeScript(a,b)},this);this._executeScript(a,b)},this)}});module.exports=new Lang;
