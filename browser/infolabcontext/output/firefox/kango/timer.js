var utils=require("kango/utils"),NotImplementedException=utils.NotImplementedException;function ITimer(){}ITimer.prototype={setInterval:function(a,b){return new NotImplementedException},clearInterval:function(a){return new NotImplementedException},setTimeout:function(a,b){return new NotImplementedException},clearTimeout:function(a){return new NotImplementedException}};function getPublicApi(){return utils.createApiWrapper(module.exports,ITimer.prototype)};








var utils=require("kango/utils"),object=utils.object,array=utils.array,func=utils.func;function Timer(){this._timers={};this._lastId=0}
Timer.prototype={dispose:function(){var a=object.getKeys(this._timers);array.forEach(a,function(a){this._clearTimer(a)},this)},_setTimer:function(a,b,d){var e=Cc["@mozilla.org/timer;1"].createInstance(Ci.nsITimer),c=++this._lastId;this._timers[c]=e;e.initWithCallback({notify:func.bind(function(){d==Ci.nsITimer.TYPE_ONE_SHOT&&(this._clearTimer(c),a())},this)},b,d);return c},_clearTimer:function(a){if("undefined"!=typeof this._timers[a]){var b=this._timers[a];delete this._timers[a];b.cancel()}},setInterval:function(a,
b){return this._setTimer(a,b,Ci.nsITimer.TYPE_REPEATING_SLACK)},clearInterval:function(a){return this._clearTimer(a)},setTimeout:function(a,b){return this._setTimer(a,b,Ci.nsITimer.TYPE_ONE_SHOT)},clearTimeout:function(a){this._clearTimer(a)}};module.exports=new Timer;module.exports.getPublicApi=getPublicApi;
