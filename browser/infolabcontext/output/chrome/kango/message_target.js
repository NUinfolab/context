"use strict";
_kangoLoader.add("kango/message_target", function(require, exports, module) {
function MessageTargetModule(g){var a={},h=this.addMessageListener=function(d,c){if("undefined"!=typeof c.call&&"undefined"!=typeof c.apply){a[d]=a[d]||[];for(var b=0;b<a[d].length;b++)if(a[d][b]==c)return!1;a[d].push(c);return!0}return!1};this.removeMessageListener=function(d,c){if("undefined"!=typeof a[d])for(var b=0;b<a[d].length;b++)if(a[d][b]==c)return a[d].splice(b,1),!0;return!1};this.removeAllMessageListeners=function(){a={}};g("message",function(d){var c=d.name;if("undefined"!=typeof a[c])for(var b=
0;b<a[c].length;b++){var e=!1;if("unknown"==typeof a[c][b].call)e=!0;else try{a[c][b](d)}catch(f){if(-2146828218==f.number||-2146823277==f.number)e=!0;else throw f;}e&&(a[c].splice(b,1),b--)}});this.onMessage=function(a,c,b){h(a,function(a){c(a.data,function(b,c){a.source.dispatchMessage(b,c)})})}}"undefined"!=typeof module&&(module.exports=MessageTargetModule);

});