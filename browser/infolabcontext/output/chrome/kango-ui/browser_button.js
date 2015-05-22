"use strict";
_kangoLoader.add("kango-ui/browser_button", function(require, exports, module) {
var utils=require("kango/utils"),object=utils.object,EventTarget=utils.EventTarget,IEventTarget=utils.IEventTarget,NotImplementedException=utils.NotImplementedException;function BrowserButtonBase(a){EventTarget.call(this);this._details=a}
BrowserButtonBase.prototype=object.extend(EventTarget,{_details:null,event:{COMMAND:"command",POPUP_DOCUMENT_COMPLETE:"PopupDocumentComplete"},setTooltipText:function(a){throw new NotImplementedException;},setCaption:function(a){throw new NotImplementedException;},setIcon:function(a){throw new NotImplementedException;},setBadgeValue:function(a){throw new NotImplementedException;},setBadgeBackgroundColor:function(a){throw new NotImplementedException;},setPopup:function(a){throw new NotImplementedException;
},setContextMenu:function(){throw new NotImplementedException;}});function getPublicApi(){return utils.createApiWrapper(module.exports,BrowserButtonBase.prototype,IEventTarget.prototype)};








var extensionInfo=require("kango/extension_info"),utils=require("kango/utils"),object=utils.object,func=utils.func,io=require("kango/io");function BrowserButton(a){BrowserButtonBase.call(this,a);this._popupDetails=null;chrome.browserAction.onClicked.addListener(func.bind(this._onClicked,this));this._initDetails(a)}
BrowserButton.prototype=object.extend(BrowserButtonBase,{_onClicked:function(){return this.fireEvent(this.event.COMMAND)},_initDetails:function(a){object.isObject(a)&&(object.isString(a.icon)&&this.setIcon(a.icon),object.isString(a.caption)&&this.setCaption(a.caption),object.isString(a.tooltipText)&&this.setTooltipText(a.tooltipText),object.isObject(a.popup)&&this.setPopup(a.popup))},setTooltipText:function(a){chrome.browserAction.setTitle({title:a.toString()})},setCaption:function(a){},setIcon:function(a){chrome.browserAction.setIcon({path:io.getFileUrl(a)})},
setBadgeValue:function(a){chrome.browserAction.setBadgeText({text:null!=a&&0!=a?a.toString():""})},setBadgeBackgroundColor:function(a){chrome.browserAction.setBadgeBackgroundColor({color:a})},setPopup:function(a){this._popupDetails=a;var b="";a&&a.url&&(b=a.url);chrome.browserAction.setPopup({popup:b})},getPopupDetails:function(){return this._popupDetails},setContextMenu:function(){}});
extensionInfo.browser_button&&(module.exports=new BrowserButton(extensionInfo.browser_button),module.exports.getPublicApi=getPublicApi);

});