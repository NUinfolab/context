"use strict";
_kangoLoader.add("kango-ui/options", function(require, exports, module) {
var utils=require("kango/utils"),NotImplementedException=utils.NotImplementedException;function IOptionsPage(){}IOptionsPage.prototype={open:function(){throw new NotImplementedException;}};function getPublicApi(){return utils.createApiWrapper(module.exports,IOptionsPage.prototype)};








var extensionInfo=require("kango/extension_info"),utils=require("kango/utils"),browser=require("kango/browser"),io=require("kango/io"),array=utils.array;function OptionsPage(){}OptionsPage.prototype={open:function(a){var b=io.getExtensionFileUrl(extensionInfo.options_page);"undefined"!=typeof a&&(b+="#"+a);browser.tabs.getAll(function(a){var c=!1;array.forEach(a,function(a){-1!=a.getUrl().indexOf(b)&&(c=!0,a.activate())});c||browser.tabs.create({url:b,focused:!0})});return!0}};
extensionInfo.options_page&&(module.exports=new OptionsPage,module.exports.getPublicApi=getPublicApi);








if(module.exports){var optionsPage=module.exports;safari.extension.settings.addEventListener("change",function(a){"open-options"==a.key&&optionsPage.open()},!1)};

});