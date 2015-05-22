"use strict";
_kangoLoader.add("kango/messaging", function(require, exports, module) {
var core=require("kango/core"),utils=require("kango/utils"),timer=require("kango/timer"),backgroundScriptEngine=require("kango/backgroundscript_engine"),array=utils.array,func=utils.func;function MessageSource(){this.dispatchMessage=function(a,b){}}function MessageRouterBase(){this._messageQueue=[]}
MessageRouterBase.prototype={_dispatchMessagesFromQueue:function(){0<this._messageQueue.length&&(backgroundScriptEngine.isLoaded()?(array.forEach(this._messageQueue,function(a){core.fireEvent(a.name,a.event)}),this._messageQueue=[]):timer.setTimeout(func.bind(function(){this._dispatchMessagesFromQueue()},this),100))},fireMessageEvent:function(a,b){backgroundScriptEngine.isLoaded()?(this._dispatchMessagesFromQueue(),core.fireEvent("message",b)):(this._messageQueue.push({name:a,event:b}),timer.setTimeout(func.bind(function(){this._dispatchMessagesFromQueue()},
this),100))},dispatchMessage:function(a,b){return this.dispatchMessageEx({name:a,data:b,origin:"background",target:this,source:this})},dispatchMessageEx:function(a){timer.setTimeout(func.bind(function(){this.fireMessageEvent("message",a)},this),1);return!0}};








var core=require("kango/core"),utils=require("kango/utils"),func=utils.func,object=utils.object,browser=require("kango/browser");function MessageRouter(){MessageRouterBase.call(this);safari.application.addEventListener("message",func.bind(this._onMessage,this),!1)}
MessageRouter.prototype=object.extend(MessageRouterBase,{_onMessage:function(a){if(a.target instanceof SafariBrowserTab){var b={name:a.name,data:a.message,origin:"tab",target:browser.getKangoTab(a.target),source:{dispatchMessage:function(b,c){a.target.page.dispatchMessage(b,c);return!0}}};this.fireMessageEvent("message",b)}}});module.exports=new MessageRouter;

});