var core=require("kango/core"),utils=require("kango/utils"),timer=require("kango/timer"),backgroundScriptEngine=require("kango/backgroundscript_engine"),array=utils.array,func=utils.func;function MessageSource(){this.dispatchMessage=function(a,b){}}function MessageRouterBase(){this._messageQueue=[]}
MessageRouterBase.prototype={_dispatchMessagesFromQueue:function(){0<this._messageQueue.length&&(backgroundScriptEngine.isLoaded()?(array.forEach(this._messageQueue,function(a){core.fireEvent(a.name,a.event)}),this._messageQueue=[]):timer.setTimeout(func.bind(function(){this._dispatchMessagesFromQueue()},this),100))},fireMessageEvent:function(a,b){backgroundScriptEngine.isLoaded()?(this._dispatchMessagesFromQueue(),core.fireEvent("message",b)):(this._messageQueue.push({name:a,event:b}),timer.setTimeout(func.bind(function(){this._dispatchMessagesFromQueue()},
this),100))},dispatchMessage:function(a,b){return this.dispatchMessageEx({name:a,data:b,origin:"background",target:this,source:this})},dispatchMessageEx:function(a){timer.setTimeout(func.bind(function(){this.fireMessageEvent("message",a)},this),1);return!0}};








var utils=require("kango/utils"),object=utils.object;function MessageRouter(){MessageRouterBase.apply(this,arguments)}MessageRouter.prototype=object.extend(MessageRouterBase,{});module.exports=new MessageRouter;
