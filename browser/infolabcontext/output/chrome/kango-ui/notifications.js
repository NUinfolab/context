"use strict";
_kangoLoader.add("kango-ui/notifications", function(require, exports, module) {
var utils=require("kango/utils"),object=utils.object,EventTarget=utils.EventTarget,NotImplementedException=utils.NotImplementedException;function INotifications(){}INotifications.prototype={show:function(a,b,c,d){throw new NotImplementedException;}};function getPublicApi(){return utils.createApiWrapper(module.exports,INotifications.prototype)};








var utils=require("kango/utils"),func=utils.func;function Notifications(){this._clickCallbacks={};this._lastId=0;"undefined"!=typeof chrome.notifications&&chrome.notifications.onClicked.addListener(func.bind(function(a){this._fireNotificationEvent(a)},this))}
Notifications.prototype={_fireNotificationEvent:function(a){if(this._clickCallbacks[a])this._clickCallbacks[a]()},_getNextId:function(){return(++this._lastId).toString()},show:function(a,d,e,b){var c=this._getNextId();chrome.notifications.create(c,{type:"basic",iconUrl:e||"",title:a,message:d},function(){});b&&(this._clickCallbacks[c]=b)}};module.exports=new Notifications;module.exports.getPublicApi=getPublicApi;

});