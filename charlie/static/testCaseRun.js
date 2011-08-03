function loadForm(comboData) {
    form = new Ext.form.FormPanel({
        hidden: true,
        headers: {
            'Content-type': 'multipart/form-data'
        },
        fileUpload: true,
        id: 'tcForm',
        addStep: function() {
            var numField = form.steps.items.getCount();
            form.steps.add(new Ext.form.CompositeField({
                xtype: 'compositefield',
                fieldLabel: numField,
                ref: 'step' + numField,
                id: 'compositefield_step' + numField,
                msgTarget: 'under',
                items: [{
                    xtype: 'hidden',
                    ref: 'sid',
                    name: 'sid' + numField,
                }, {
                    xtype: 'displayfield',
                    ref: 'action',
                    name: 'action' + numField,
                    width: 280,
                }, {
                    xtype: 'displayfield',
                    ref: 'expected',
                    name: 'expected' + numField,
                    width: 280,
                }, {
                    xtype: 'displayfield',
                    ref: 'scrot_url',
                    value: '',
                    width: 80,
                }, {
                    xtype: 'displayfield',
                    ref: 'status',
                    value: '<a class="" href="#" onClick="setStatus(' + numField + ', true)">OK</a> | <a class="" href="#" onClick="setStatus(' + numField + ', false)">KO</a>',
                    width: 60,
                }, {
                    xtype: 'displayfield',
                    ref: 'jiras',
                    html: '',
                    width: 130,
                }, {
                    xtype: 'textarea',
                    ref: 'comments',
                    width: 200,
                    stepNum: numField,
                    listeners: {
                        'change': function(myField, newValue, oldValue) {
                            var mySid = Ext.getCmp('compositefield_step' + myField.stepNum).sid.getValue();
                            Ext.Ajax.request({
                                method: 'POST',
                                url: '/test_manager/do_test/',
                                params: {
                                    'csrfmiddlewaretoken': csrf_token,
                                    'action': 'addcomment',
                                    'sid': mySid,
                                    'comment': newValue,
                                },
                                success: function(response, opts) {
                                    var result = Ext.util.JSON.decode(response.responseText);
                                    if(!result.success) {
                                        Ext.Msg.alert('Error', result.errorMessage);
                                    }
                                },
                                failure: function(response, opts) {
                                    Ext.Msg.alert('Error', 'Could not edit the comment for this step');
                                },
                            });
                        },
                    },
                }],
            }));
            form.doLayout();
        },
        title: 'Test case',
        autoHeight: true,
        autoWidth: true,
        bodyStyle: 'padding: 5px',
        defaults: {
            autoScroll: true,
            anchor: '0',
        },
        items: [
            {
                xtype: 'displayfield',
                name: 'title',
                ref: 'tctitle',
                fieldLabel: 'Test Case title',
                anchor: '-20',
            }, {
                xtype: 'hidden',
                name: 'action',
                ref: 'action',
                value: 'newtc',
            }, {
                xtype: 'displayfield',
                ref: 'descr',
                name: 'description',
                fieldLabel: 'Description',
                anchor: '-20',
            }, {
                xtype: 'displayfield',
                name: 'precondition',
                fieldLabel: 'Precondition',
                ref: 'precond',
                anchor: '-20',
            }, {
                xtype: 'fieldset',
                title: 'Details',
                autoWidth: true,
                ref: 'details',
                collapsible: true,
                items: [{
                    width: 200,
                    xtype: 'displayfield',
                    name: 'module',
                    ref: 'module',
                    fieldLabel: 'Module',
                }, {
                    width: 200,
                    xtype: 'displayfield',
                    name: 'smodule',
                    ref: 'submodules',
                    fieldLabel: 'Sub Module',
                }, {
                    width: 200,
                    xtype: 'combo',
                    name: 'envir',
                    ref: 'envir',
                    fieldLabel: 'Environment',
                    mode: 'local',
                    forceSelection: true,
                    allowBlank: false,
                    triggerAction: 'all',
                    editable: false,
                    displayField: 'name',
                    valueField: 'value',
                    store: new Ext.data.JsonStore({
                        data: comboData.reader.jsonData.config.envir,
                        fields: ['name', 'value'],
                    }),
                }, {
                    width: 200,
                    xtype: 'combo',
                    name: 'os',
                    ref: 'os',
                    fieldLabel: 'OS',
                    mode: 'local',
                    forceSelection: true,
                    allowBlank: false,
                    triggerAction: 'all',
                    editable: false,
                    displayField: 'name',
                    valueField: 'value',
                    store: new Ext.data.JsonStore({
                        data: comboData.reader.jsonData.config.os,
                        fields: ['name', 'value'],
                    }),
                }, {
                    width: 200,
                    xtype: 'combo',
                    name: 'browser',
                    ref: 'browser',
                    fieldLabel: 'Browser',
                    mode: 'local',
                    forceSelection: true,
                    allowBlank: false,
                    triggerAction: 'all',
                    editable: false,
                    displayField: 'name',
                    valueField: 'value',
                    store: new Ext.data.JsonStore({
                        data: comboData.reader.jsonData.config.browser,
                        fields: ['name', 'value'],
                    }),
                }, {
                    width: 200,
                    xtype: 'combo',
                    name: 'release',
                    ref: 'release',
                    fieldLabel: 'Release',
                    mode: 'local',
                    forceSelection: true,
                    allowBlank: false,
                    triggerAction: 'all',
                    editable: false,
                    displayField: 'name',
                    valueField: 'value',
                    store: new Ext.data.JsonStore({
                        data: comboData.reader.jsonData.config.release,
                        fields: ['name', 'value'],
                    }),
                }, {
                    width: 200,
                    xtype: 'combo',
                    name: 'version',
                    ref: 'version',
                    fieldLabel: 'Version',
                    mode: 'local',
                    forceSelection: true,
                    allowBlank: false,
                    triggerAction: 'all',
                    editable: false,
                    displayField: 'name',
                    valueField: 'value',
                    store: new Ext.data.JsonStore({
                        data: comboData.reader.jsonData.config.version,
                        fields: ['name', 'value'],
                    }),
                }, {
                    xtype: 'displayfield',
                    name: 'criticity',
                    ref: 'criticity',
                    fieldLabel: 'Criticity',
                    anchor: '-20',
                }, {
                    xtype: 'displayfield',
                    anchor: '-20',
                    name: 'tags',
                    ref: 'tags',
                    fieldLabel: 'tags',
                }, {
                    xtype: 'displayfield',
                    name: 'duration',
                    ref: 'duration',
                    fieldLabel: 'Duration (min)',
                    anchor: '-20',
                }]
            }, {
                xtype: 'fieldset',
                title: 'Steps',
                ref: 'steps',
                autoWidth: true,
                collapsible: true,
                items: [{
                    xtype: 'compositefield',
                    fieldLabel: "N°",
                    msgTarget: 'under',
                    items: [{
                        xtype: 'displayfield',
                        value: 'Action',
                        width: 280,
                    }, {
                        xtype: 'displayfield',
                        value: 'Expected Result',
                        width: 280,
                    }, {
                        xtype: 'displayfield',
                        value: 'Screenshot',
                        width: 80,
                    }, {
                        xtype: 'displayfield',
                        value: 'Status',
                        width: 60,
                    }, {
                        xtype: 'displayfield',
                        value: 'Jiras',
                        width: 130,
                    }, {
                        xtype: 'displayfield',
                        value: 'Comments',
                        width: 200,
                    }],
                }],
            },
        ],
        listeners: {
            'render': function(myForm) {
                window.onresize = function() {
                    myForm.syncSize();
                }
            },
        },
    });
    return form;
}
