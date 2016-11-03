odoo.define('pos_customer_screen.pos_customer_screen', function (require) {
"use strict";


var pos_model = require('point_of_sale.models');
var Model   = require('web.Model');
var screens = require('point_of_sale.screens');
var chrome = require('point_of_sale.chrome');
var PosBaseWidget = require('point_of_sale.BaseWidget');
var core = require('web.core');


var _t = core._t;

    var ProxyScreenDisplay = PosBaseWidget.extend({
        template: 'ProxyScreenDisplay',
        start: function(){
            $(".customer_display_icon").click(function(){
                var status_code = new Model('screen.notification.msg');
                function createRequest(){
                    status_code.call('check_status',[]).then(
                        function(result) {
                            if(result){
                                $(".customer_display_icon").css('color','green');
                            }
                            else{
                                $(".customer_display_icon").css('color','red');
                            } 
                    });
                }
            });
            var status_code = new Model('screen.notification.msg');
            function createRequest(){
                status_code.call('check_status',[]).then(
                    function(result) {
                        if(result){
                            $(".customer_display_icon").css('color','green');
                        }
                        else{
                            $(".customer_display_icon").css('color','red');
                        } 
                     setTimeout(function(){ createRequest(); }, 10000);
                 });
            }
            createRequest();
        },

    });
    var chrome_obj = chrome.Chrome.prototype
    chrome_obj.widgets.push({
            'name':   'ProxyScreenDisplay',
            'widget': ProxyScreenDisplay,
            'append':  '.pos-rightheader',
    });


    screens.PaymentScreenWidget.include({
        click_delete_paymentline: function(cid){
            this._super(cid);
            var self  = this;
            self.pos.get('selectedOrder').mirror_image_data();
        },
        click_paymentline: function(cid){
            this._super(cid);
            var self  = this;
            self.pos.get('selectedOrder').mirror_image_data();
        },
        click_numpad: function(button) {
            this._super(button);
            var self  = this;
            self.pos.get('selectedOrder').mirror_image_data();
        },
    });

    screens.ReceiptScreenWidget.include({
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.next').click(function(){
               self.pos.get('selectedOrder').mirror_image_data();
            });
        },
    });
    
    chrome.OrderSelectorWidget.include({
        renderElement: function(){
            var self = this;
            this._super();
            this.$('.order-button.select-order').click(function(event){
                self.pos.get('selectedOrder').mirror_image_data();
            });
            this.$('.neworder-button').click(function(event){
                self.pos.get('selectedOrder').mirror_image_data();
            });
            this.$('.deleteorder-button').click(function(event){
                self.pos.get('selectedOrder').mirror_image_data();
            });
        },
        deleteorder_click_handler: function(event, $el) {
            var self  = this;
            var order = this.pos.get_order(); 
            if (!order) {
                return;
            } else if ( !order.is_empty() ){
                this.gui.show_popup('confirm',{
                    'title': _t('Destroy Current Order ?'),
                    'body': _t('You will lose any data associated with the current order'),
                    confirm: function(){
                        self.pos.delete_current_order();
                        self.pos.get('selectedOrder').mirror_image_data();
                    },
                });
            } else {
                this.pos.delete_current_order();
                self.pos.get('selectedOrder').mirror_image_data();
            }
        },
    });

var _modelproto = pos_model.Order.prototype;
pos_model.Order = pos_model.Order.extend({
        add_product:function(product, options){
            var self = this;
            _modelproto.add_product.call(this,product, options);
            self.mirror_image_data();           
        },
        mirror_image_data:function(){
            var self = this;
            var selectedOrder = self.pos.get('selectedOrder');
            var payment_lines = selectedOrder['paymentlines'];
            var paymentLines = [];
            (payment_lines).each(_.bind(function(item){
                var payment_info = [item.name,item.amount]
                return paymentLines.push(payment_info);
            }, this));
            var paidTotal = selectedOrder.get_total_paid();
            var dueTotal = selectedOrder.get_total_with_tax();
            var remaining = dueTotal > paidTotal ? dueTotal - paidTotal : 0;
            var change = paidTotal > dueTotal ? paidTotal - dueTotal : 0;
            paymentLines.push([paidTotal, remaining, change]);
            var currentOrderLines = selectedOrder['orderlines'];
            var orderLines = [];
            (currentOrderLines).each(_.bind( function(item){
                var t = item.export_as_JSON();
                var product = self.pos.db.get_product_by_id(t.product_id);
                var pro_info = [product.display_name,t.price_unit,t.qty,product.uom_id[1],t.discount];
                return orderLines.push(pro_info);
            }, this));
            orderLines.push([selectedOrder.get_total_tax(),selectedOrder.get_total_with_tax()]);
            var customer_id = selectedOrder.get_client() && selectedOrder.get_client().id || '';
            var pos_mirror = new Model('mirror.image.order');
            pos_mirror.call('create_pos_data',[orderLines,selectedOrder.uid,self.pos.user.id,self.pos.currency.symbol,self.pos.config.id,paymentLines]).then(
                   function(result) { });
        }
    });  
    
    screens.NumpadWidget.include({

        start: function() {
            var self = this;
            this._super(); 
            this.$(".input-button").click(function(){
                self.pos.get('selectedOrder').mirror_image_data(); 
            });
        },
    });
});

