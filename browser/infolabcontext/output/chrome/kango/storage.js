"use strict";
_kangoLoader.add("kango/storage", function(require, exports, module) {
var utils=require("kango/utils"),array=utils.array,object=utils.object,EventTarget=utils.EventTarget,NotImplementedException=utils.NotImplementedException;function IStorage(){}IStorage.prototype={setItem:function(a,b){throw new NotImplementedException;},getItem:function(a){throw new NotImplementedException;},removeItem:function(a){throw new NotImplementedException;},getKeys:function(){throw new NotImplementedException;},clear:function(){throw new NotImplementedException;}};
function JSONStorage(a){EventTarget.call(this);this._storageEngine=a}
JSONStorage.prototype=object.extend(EventTarget,{_storageEngine:null,getItem:function(a){a=this._storageEngine.getItem(a);return"undefined"!=typeof a&&null!=a?JSON.parse(a):null},setItem:function(a,b){if("undefined"!=typeof b){var c=JSON.stringify(b);"undefined"!=typeof c&&(this._storageEngine.setItem(a,c),this.fireEvent("setItem",{data:{name:a,value:b}}))}else return this.removeItem(a);return!1},removeItem:function(a){this._storageEngine.removeItem(a);this.fireEvent("removeItem",{data:{name:a}})},
getKeys:function(){return this._storageEngine.getKeys()},getItems:function(){var a={};array.forEach(this.getKeys(),function(b){a[b]=this.getItem(b)},this);return a},clear:function(){this._storageEngine.clear();this.fireEvent("clear")},dispose:function(){this.removeAllEventListeners();"undefined"!=typeof this._storageEngine.dispose&&this._storageEngine.dispose();this._storageEngine=null}});function getPublicApi(){return utils.createApiWrapper(module.exports.storage,IStorage.prototype)};








var utils=require("kango/utils"),array=utils.array,SYSTEM_STORAGE_PREFIX="{772ED927-1623-4E2C-94CC-D5E488E34C5B}_SystemStorage.";function UserStorage(a){this._storageEngine=a}
UserStorage.prototype={getItem:function(a){return this._storageEngine.getItem(a)},setItem:function(a,b){return this._storageEngine.setItem(a,b)},removeItem:function(a){return this._storageEngine.removeItem(a)},clear:function(){array.forEach(this.getKeys(),function(a){this.removeItem(a)},this)},getKeys:function(){return array.filter(this._storageEngine.getKeys(),function(a){return 0!=a.indexOf(SYSTEM_STORAGE_PREFIX)})}};function SystemStorage(a){this._storageEngine=a}
SystemStorage.prototype={getItem:function(a){return this._storageEngine.getItem(SYSTEM_STORAGE_PREFIX+a)},setItem:function(a,b){return this._storageEngine.setItem(SYSTEM_STORAGE_PREFIX+a,b)},removeItem:function(a){return this._storageEngine.removeItem(SYSTEM_STORAGE_PREFIX+a)},clear:function(){array.forEach(this.getKeys(),function(a){this.removeItem(a)},this)},getKeys:function(){return array.filter(this._storageEngine.getKeys(),function(a){return 0==a.indexOf(SYSTEM_STORAGE_PREFIX)})}};








function LocalStorage(){}LocalStorage.prototype={getItem:function(a){return localStorage.getItem(a)},setItem:function(a,b){return localStorage.setItem(a,b)},removeItem:function(a){return localStorage.removeItem(a)},clear:function(){return localStorage.clear()},getKeys:function(){for(var a=localStorage.length,b=Array(a),c=0;c<a;c++)b[c]=localStorage.key(c);return b}};module.exports.storage=new JSONStorage(new UserStorage(new LocalStorage));module.exports.systemStorage=new JSONStorage(new SystemStorage(new LocalStorage));
module.exports.getPublicApi=getPublicApi;

});