kango.MessageRouterBase=function(){this._messageQueue=[]};
kango.MessageRouterBase.prototype={_messageQueue:null,_dispatchMessagesFromQueue:function(){0<this._messageQueue.length&&(kango.backgroundScript.isLoaded()?(kango.array.forEach(this._messageQueue,function(a){kango.fireEvent(a.name,a.event)}),this._messageQueue=[]):kango.timer.setTimeout(kango.func.bind(function(){this._dispatchMessagesFromQueue()},this),100))},fireMessageEvent:function(a,b){kango.backgroundScript.isLoaded()?(this._dispatchMessagesFromQueue(),kango.fireEvent(kango.event.MESSAGE,b)):
(this._messageQueue.push({name:a,event:b}),kango.timer.setTimeout(kango.func.bind(function(){this._dispatchMessagesFromQueue()},this),100))},dispatchMessage:function(a,b){return this.dispatchMessageEx({name:a,data:b,origin:"background",target:kango,source:kango})},dispatchMessageEx:function(a){kango.timer.setTimeout(kango.func.bind(function(){this.fireMessageEvent(kango.event.MESSAGE,a)},this),1);return!0}};
kango.registerModule(function(a){var b=new kango.MessageRouter;a.dispatchMessage=function(a,c){return b.dispatchMessage(a,c)};a.dispatchMessageEx=function(a){return b.dispatchMessageEx(a)};this.dispose=function(){a.dispatchMessage=null;b=a.dispatchMessageEx=null}});








kango.MessageRouter=function(){this.superclass.apply(this,arguments)};kango.MessageRouter.prototype=kango.oop.extend(kango.MessageRouterBase,{});
