Ext.define('devilry.extjshelpers.AssignmentGroupOverview', {
    extend: 'Ext.panel.Panel',
    width: 800,
    height: 600,
    layout: 'border',
    alias: 'widget.examinerfeedback',
    requires: [
        'devilry.extjshelpers.DeliveryInfo',
        'devilry.extjshelpers.StaticFeedbackInfo',
        'devilry.extjshelpers.StaticFeedbackGrid'
    ],

    headingTpl: Ext.create('Ext.XTemplate',
        '<div class="treeheader">',
        '   <div class="level1">{deadline__assignment_group__parentnode__parentnode__parentnode__long_name}</div>',
        '   <div class="level2">{deadline__assignment_group__parentnode__parentnode__long_name}</div>',
        '   <div class="level3">{deadline__assignment_group__parentnode__long_name}</div>',
        '<div>'
    ),

    config: {
        /**
        * @cfg
        * RestfulSimplifiedFileMeta store. __Required__.
        */
        filemetastoreid: undefined,
        deliveryid: undefined,
        deliverymodelname: undefined,
        staticfeedbackstoreid: undefined
    },

    initComponent: function() {
        var me = this;
        //this.centerAreaId = this.id + '-center';
        var staticfeedbackstore = Ext.data.StoreManager.lookup(this.staticfeedbackstoreid);
        this.currentlyShownFeedback = Ext.create('devilry.extjshelpers.StaticFeedbackInfo', {
            store: staticfeedbackstore
        });

        var mainHeader = Ext.create('Ext.Component');
        var deliveryInfo = Ext.create('devilry.extjshelpers.DeliveryInfo', {
            filemetastore: Ext.data.StoreManager.lookup(this.filemetastoreid)
        });


        var createButton = Ext.create('Ext.button.Button', {
            text: 'Modify feedback',
            margin: {top: 20},
            scale: 'large',
            hidden: true,
            listeners: {
                click: function() {
                    var createurl = Ext.String.format('../create-feedback/{0}', me.delivery.id);
                    window.location = createurl;
                }
            }
        });

        Ext.apply(this, {
            items: [{
                region: 'north',
                height: 66,
                xtype: 'container',
                items: [mainHeader]
            }, {
                region: 'center',
                //id: this.centerAreaId,
                //title: 'Feedback',
                //tbar: [{
                    //xtype: 'staticfeedbackhistorymenu',
                    //text: 'hei',
                    //store: staticfeedbackstore
                //}],
                items: [me.currentlyShownFeedback]
            }, {
                region: 'west',
                width: 220,
                xtype: 'panel',
                collapsible: true,   // make collapsible
                titleCollapse: true, // click anywhere on title to collapse.
                split: true,
                items: [deliveryInfo,
                //{
                    //xtype: 'staticfeedbackgrid',
                    //store: staticfeedbackstore,
                    //listeners: {
                        //itemclick: function(view, record) {
                            //me.currentlyShownFeedback.setStaticFeedback(record.data);
                        //}
                    //}
                //},
                createButton]
            }],
        });
        this.callParent(arguments);

        Ext.ModelManager.getModel(this.deliverymodelname).load(this.deliveryid, {
            success: function(deliveryrecord) {
                deliveryInfo.setDelivery(deliveryrecord.data);
                mainHeader.update(me.headingTpl.apply(deliveryrecord.data));
                me.delivery = deliveryrecord.data;
                createButton.show();
            }
        });

        //staticfeedbackstore.load({
            //callback: function(records, operation, success) {
                //me.currentlyShownFeedback.setStaticFeedback(records[0].data);
            //},
        //});
    },

    //setCenterAreaContent: function(content) {
        //var centerArea = Ext.getCmp(this.centerAreaId);
        //centerArea.removeAll();
        //centerArea.add(content);
    //}
});