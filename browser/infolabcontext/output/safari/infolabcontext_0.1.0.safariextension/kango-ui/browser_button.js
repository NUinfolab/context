"use strict";
_kangoLoader.add("kango-ui/browser_button", function(require, exports, module) {
var utils=require("kango/utils"),object=utils.object,EventTarget=utils.EventTarget,IEventTarget=utils.IEventTarget,NotImplementedException=utils.NotImplementedException;function BrowserButtonBase(a){EventTarget.call(this);this._details=a}
BrowserButtonBase.prototype=object.extend(EventTarget,{_details:null,event:{COMMAND:"command",POPUP_DOCUMENT_COMPLETE:"PopupDocumentComplete"},setTooltipText:function(a){throw new NotImplementedException;},setCaption:function(a){throw new NotImplementedException;},setIcon:function(a){throw new NotImplementedException;},setBadgeValue:function(a){throw new NotImplementedException;},setBadgeBackgroundColor:function(a){throw new NotImplementedException;},setPopup:function(a){throw new NotImplementedException;
},setContextMenu:function(){throw new NotImplementedException;}});function getPublicApi(){return utils.createApiWrapper(module.exports,BrowserButtonBase.prototype,IEventTarget.prototype)};








var extensionInfo=require("kango/extension_info"),utils=require("kango/utils"),object=utils.object,func=utils.func,io=require("kango/io");
function BrowserButton(a){BrowserButtonBase.call(this,a);this._icon=a.icon||null;this._tooltipText=a.tooltipText||"";this._popupDetails=a.popup||null;this._badgeValue=0;this._popover=null;safari.application.addEventListener("command",func.bind(function(a){a.command==this._commandName&&this.fireEvent(this.event.COMMAND)},this),!0);safari.application.addEventListener("popover",func.bind(function(a){a=a.target;a.identifier==this._popoverId&&(a.width=this._popupDetails.width,a.height=this._popupDetails.height,
a.contentWindow.location.reload())},this),!0);a=this._getButton();null!=a&&this._initButton(a);safari.application.addEventListener("validate",func.bind(function(a){if(a.target instanceof SafariExtensionToolbarItem){a=safari.extension.toolbarItems;for(var c=0;c<a.length;c++)this._initButton(a[c])}},this),!0)}
BrowserButton.prototype=object.extend(BrowserButtonBase,{_id:"kango-ui-button",_popoverId:"kango-ui-popup",_commandName:"KangoButtonCommand",_getButton:function(){for(var a=safari.extension.toolbarItems,b=0;b<a.length;b++)if(a[b].identifier==this._id)return a[b];return null},_initButton:function(a){null!=this._icon&&this._setIcon(a,this._icon);""!=this._tooltipText&&this._setTooltipText(a,this._tooltipText);0!=this._badgeValue&&this._setBadgeValue(a,this._badgeValue);null!=this._popupDetails?null==
this._popover?this._setPopup(a,this._popupDetails):(a.popover=this._popover,a.command=null):(a.command=this._commandName,a.popover=null)},_removePopup:function(a){a.popover=this._popover=null;safari.extension.removePopover(this._popoverId);a.command=this._commandName},_setPopup:function(a,b){if(null!=b&&object.isString(b.url)){var c="",d=b.height,e=b.width;null!=b&&object.isString(b.url)&&(c=b.url);this._removePopup(a);a.popover=this._popover=safari.extension.createPopover(this._popoverId,safari.extension.baseURI+
c,e,d);a.command=null;a.popover.width=b.width;a.popover.height=d}else this._removePopup(a)},_setTooltipText:function(a,b){a.toolTip=b.replace(/\n/g,"; ").replace(/\r/g,"")},_setIcon:function(a,b){a.image=safari.extension.baseURI+b},_setBadgeValue:function(a,b){a.badge=parseInt(b,10)},setTooltipText:function(a){this._tooltipText=a;var b=this._getButton();null!=b&&this._setTooltipText(b,a)},setCaption:function(a){},setIcon:function(a){this._icon=a;var b=this._getButton();null!=b&&this._setIcon(b,a)},
setBadgeValue:function(a){this._badgeValue=a;var b=this._getButton();null!=b&&null!=a&&this._setBadgeValue(b,a)},setBadgeBackgroundColor:function(a){},setPopup:function(a){this._popupDetails=a;var b=this._getButton();if(null!=b)if(b.popover&&b.popover.visible){var c=this;timer.setTimeout(function(){c.setPopup(c._popupDetails)},100)}else this._setPopup(b,a)},closePopup:function(){var a=this._getButton();null!=a&&null!=a.popover&&a.popover.hide()},getPopupDetails:function(){return this._popupDetails},
setContextMenu:function(){}});extensionInfo.browser_button&&(module.exports=new BrowserButton(extensionInfo.browser_button),module.exports.getPublicApi=getPublicApi);

});