openerp.document_digital_signature = function (instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    
    instance.web.document_digital_signature = instance.web.document_digital_signature || {};

    instance.web.views.add('form_document_wait_sign', 'instance.web.document_digital_signature.WaitSignFormView');
    instance.web.document_digital_signature.WaitSignFormView = instance.web.FormView.extend({
        init: function() {
        	//console.log("Initialization");
            this.origin = null;
            var self = this;
            this._super.apply(this, arguments);
        },
        do_show: function(record){
            var self = this;
        	//console.log("Start Timeout");
            setTimeout(function() {self._wait_for_sign();}, 5000);
        	//console.log("Timeout Started");
            self.origin = self.get("attachment_id");
            return this._super(record);
        },
        destroy: function() {
            var self = this;
        	//console.log("Destroy");
        	clearTimeout(self._waitsign);
        },
    	_wait_for_sign: function() {
            var self = this;
        	//console.log("Attendi..");
        	var dialog = $('.ui-dialog');
        	var dialog_footer = $('.ui-dialog footer[states="choose"]').hasClass("oe_form_invisible");
        	if (dialog.length == 0 || dialog_footer == false) {
        		// if not dialog, and footer choose is visible
        		// stop interval
        		return false; 
        	}
        	id = this.dataset.context["attachment_id"]
            new instance.web.Model("ir.attachment").call("is_signed", [[id]]).then(function(res) {
            	if(res == false){
            		//console.log('Non firmato')
            		self._waitsign = setTimeout(function() {self._wait_for_sign();}, 3000);
            	}
            	else {
            		self.$el.find(".oe_signature").html("<div><h1>Documento Firmato Correttamente!</h1></div>")
            		//console.log('Firmato!')
            	}
            });
    	},
    })
   
};