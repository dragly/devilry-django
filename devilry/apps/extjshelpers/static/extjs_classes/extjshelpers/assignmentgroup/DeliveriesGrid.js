Ext.define('devilry.extjshelpers.assignmentgroup.DeliveriesGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.deliveriesgrid',
    cls: 'widget-deliveriesgrid selectable-grid',
    hideHeaders: true, // Hide column header

    rowTpl: Ext.create('Ext.XTemplate',
        '<span class="delivery_number">{delivery.number}:</span> ',
        '<span class="time_of_delivery">{delivery.time_of_delivery:date}</span>',
        '<tpl if="delivery.time_of_delivery &gt; deadline__deadline">',
        '   <span class="after-deadline">(After deadline)</span>',
        '</tpl>',
        '<tpl if="feedback">',
        '   <span class="has-feedback">({feedback.grade})</span>',
        '</tpl>'
    ),

    config: {
        /**
         * @cfg
         * A {@link devilry.extjshelpers.SingleRecordContainer} for Delivery.
         * The record is changed when a user selects a delivery.
         */
        delivery_recordcontainer: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {

        var me = this;
        Ext.apply(this, {
            columns: [{
                header: 'Data',
                dataIndex: 'id',
                flex: 1,
                renderer: function(value, metaData, deliveryrecord) {
                    //console.log(deliveryrecord.data);
                    var staticfeedbackStore = deliveryrecord.staticfeedbacks();
                    return this.rowTpl.apply({
                        delivery: deliveryrecord.data,
                        feedback: staticfeedbackStore.count() > 0? staticfeedbackStore.data.items[0].data: undefined
                    });
                }
            }],
            listeners: {
                scope: this,
                itemmouseup: this.onSelectDelivery
            }
        });

        this.store.on('load', this.onLoadStore, this);

        this.callParent(arguments);
    },

    /**
     * @private
     * Make sure we show pager if needed.
     */
    onLoadStore: function() {
        if(this.store.count() < this.store.getTotalCount()) {
            this.addDocked({
                xtype: 'pagingtoolbar',
                store: this.store,
                dock: 'bottom',
                displayInfo: false
            });
        };
    },

    /**
     * @private
     */
    onSelectDelivery: function(grid, deliveryRecord) {
        //console.log('selected', deliveryRecord);
        this.delivery_recordcontainer.setRecord(deliveryRecord);
    }
});