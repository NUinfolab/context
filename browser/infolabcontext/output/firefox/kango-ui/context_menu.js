var utils=require("kango/utils"),object=utils.object,EventTarget=utils.EventTarget,IEventTarget=utils.IEventTarget;function ContextMenuItemBase(){EventTarget.call(this)}ContextMenuItemBase.prototype=object.extend(EventTarget,{event:{CLICK:"click"}});function getPublicApi(){return utils.createApiWrapper(module.exports,ContextMenuItemBase.prototype,IEventTarget.prototype)};








var extensionInfo=require("kango/extension_info"),utils=require("kango/utils"),object=utils.object,func=utils.func,array=utils.array,chromeWindows=require("kango/chrome_windows"),io=require("kango/io");function ContextMenuItem(a){ContextMenuItemBase.apply(this,arguments);this._id="kango-"+utils.utils.getDomainFromId(extensionInfo.id)+"-menu-item1";this.init(a)}
ContextMenuItem.prototype=object.extend(ContextMenuItemBase,{init:function(a){array.forEach(chromeWindows.getLoadedChromeWindows(),function(b){this.addItem(b,this._id,a.caption,a.context||"all")},this);chromeWindows.addEventListener(chromeWindows.event.WINDOW_LOAD,func.bind(function(b){this.addItem(b.window,this._id,a.caption,a.context||"all")},this));chromeWindows.addEventListener(chromeWindows.event.WINDOW_UNLOAD,func.bind(function(a){this.removeItem(a.window,this._id)},this))},dispose:function(){this.removeAllEventListeners();
array.forEach(chromeWindows.getLoadedChromeWindows(),function(a){this.removeItem(a,this._id)},this)},addItem:function(a,b,d,h){var e=a.document,f=e.getElementById("contentAreaContextMenu"),c=e.createElement("menuitem");c.setAttribute("id",b);c.setAttribute("label",d);c.setAttribute("class","menuitem-iconic");c.setAttribute("image",io.getExtensionFileUrl("icons/button.png"));c.addEventListener("command",func.bind(function(a){var b=e.popupNode;this.fireEvent(this.event.CLICK,{srcUrl:b.src,linkUrl:b.href});
a.preventDefault()},this),!1);f.appendChild(c);var g=function(){var c=e.getElementById(b);null!=c&&"image"==h&&(c.hidden=!a.gContextMenu.onImage)};f.addEventListener("popupshowing",g,!1);chromeWindows.registerContainerUnloader(function(){f.removeEventListener("popupshowing",g,!1)},a)},removeItem:function(a,b){var d=a.document.getElementById(b);null!=d&&d.parentNode.removeChild(d)}});
extensionInfo.context_menu_item&&(module.exports=new ContextMenuItem(extensionInfo.context_menu_item),module.exports.getPublicApi=getPublicApi);
