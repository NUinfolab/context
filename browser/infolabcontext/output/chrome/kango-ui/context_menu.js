"use strict";
_kangoLoader.add("kango-ui/context_menu", function(require, exports, module) {
var utils=require("kango/utils"),object=utils.object,EventTarget=utils.EventTarget,IEventTarget=utils.IEventTarget;function ContextMenuItemBase(){EventTarget.call(this)}ContextMenuItemBase.prototype=object.extend(EventTarget,{event:{CLICK:"click"}});function getPublicApi(){return utils.createApiWrapper(module.exports,ContextMenuItemBase.prototype,IEventTarget.prototype)};








var extensionInfo=require("kango/extension_info"),utils=require("kango/utils"),func=utils.func,object=utils.object;function ContextMenuItem(a){ContextMenuItemBase.apply(this,arguments);this.init(a)}ContextMenuItem.prototype=object.extend(ContextMenuItemBase,{init:function(a){this.addItem("item1",a.caption,a.context||"all")},addItem:function(a,b,c){a={title:b,contexts:[c]};a.onclick=func.bind(function(a,b){this.fireEvent(this.event.CLICK,{srcUrl:a.srcUrl,linkUrl:a.linkUrl})},this);return chrome.contextMenus.create(a)}});
extensionInfo.context_menu_item&&(module.exports=new ContextMenuItem(extensionInfo.context_menu_item),module.exports.getPublicApi=getPublicApi);

});