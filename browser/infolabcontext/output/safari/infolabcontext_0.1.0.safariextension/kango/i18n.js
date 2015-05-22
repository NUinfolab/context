"use strict";
_kangoLoader.add("kango/i18n", function(require, exports, module) {
var extensionInfo=require("kango/extension_info"),utils=require("kango/utils"),io=require("kango/io"),string=utils.string;function InternationalizationBase(){this._messages={};this._currentLocale=this._defaultLocale="en";this._loadLocales(this.getApplicationLocale())}
InternationalizationBase.prototype={_loadLocales:function(a){extensionInfo.locales&&(this._defaultLocale=extensionInfo.default_locale||"en",this._currentLocale=a?a.slice(0,2).toLowerCase():this._defaultLocale,this._messages[this._currentLocale]=this._getLocaleMessages(this._currentLocale),this._currentLocale!=this._defaultLocale&&(this._messages[this._defaultLocale]=this._getLocaleMessages(this._defaultLocale)))},_getLocaleMessages:function(a){return(a=io.getExtensionFileContents("locales/"+a+".json"))?
JSON.parse(a):null},getApplicationLocale:function(){return this._defaultLocale},getCurrentLocale:function(){return this._currentLocale},getMessages:function(){return(this._messages[this._currentLocale]?this._messages[this._currentLocale]:this._messages[this._defaultLocale])||{}},getMessage:function(a){var b=this.getMessages(),b=b[a]?b[a]:a;return 1<arguments.length?string.format.apply(string,[b].concat(Array.prototype.slice.call(arguments,1))):b}};
function getPublicApi(){return utils.createApiWrapper(module.exports,InternationalizationBase.prototype)};








var utils=require("kango/utils"),object=utils.object;function Internationalization(){InternationalizationBase.call(this)}Internationalization.prototype=object.extend(InternationalizationBase,{getApplicationLocale:function(){return window.navigator.language||null}});module.exports=new Internationalization;module.exports.getPublicApi=getPublicApi;

});