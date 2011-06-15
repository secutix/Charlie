            var form, comboData;
            function loadForm() {
                var submodule_list = new Ext.data.JsonStore({
                    data: comboData.reader.jsonData.smodule,
                    fields: ['name', 'value'],
                });
                form = new Ext.form.FormPanel({
                    defaults: {width: 300},
                    renderTo: 'tcform',
                    title: 'New test case',
                    autoHeight: true,
                    autoWidth: true,

                    bodyStyle: 'padding: 5px',
                    defaults: {
                        anchor: '0'
                    },
                    items: [
                        {
                            xtype: 'textfield',
                            name: 'title',
                            fieldLabel: 'Test Case title',
                            anchor: '-20',
                            allowBlank: false
                        }, {
                            xtype: 'textfield',
                            name: 'description',
                            fieldLabel: 'Description',
                            anchor: '-20',
                            allowBlank: false
                        }, {
                            xtype: 'textarea',
                            name: 'precondition',
                            fieldLabel: 'Precondition',
                            anchor: '-20',
                            allowBlank: false
                        }, {
                            xtype: 'fieldset',
                            title: 'Details',
                            ref: 'details',
                            collapsible: true,
                            items: [

                                {
                                    width: 200,
                                    xtype: 'combo',
                                    name: 'envir',
                                    fieldLabel: 'Environment',
                                    mode: 'local',
                                    forceSelection: true,
                                    allowBlank: false,
                                    triggerAction: 'all',
                                    editable: false,
                                    displayField: 'name',
                                    valueField: 'value',
                                    store: new Ext.data.JsonStore({
                                        data: comboData.reader.jsonData.envir,
                                        fields: ['name', 'value'],
                                    }),
                                }, {
                                    width: 200,
                                    xtype: 'combo',
                                    name: 'os',
                                    fieldLabel: 'OS',
                                    mode: 'local',
                                    forceSelection: true,
                                    allowBlank: false,
                                    triggerAction: 'all',
                                    editable: false,
                                    displayField: 'name',
                                    valueField: 'value',
                                    store: new Ext.data.JsonStore({
                                        data: comboData.reader.jsonData.os,
                                        fields: ['name', 'value'],
                                    }),
                                }, {
                                    width: 200,
                                    xtype: 'combo',
                                    name: 'browser',
                                    fieldLabel: 'Browser',
                                    mode: 'local',
                                    forceSelection: true,
                                    allowBlank: false,
                                    triggerAction: 'all',
                                    editable: false,
                                    displayField: 'name',
                                    valueField: 'value',
                                    store: new Ext.data.JsonStore({
                                        data: comboData.reader.jsonData.browser,
                                        fields: ['name', 'value'],
                                    }),
                                }, {
                                    width: 200,
                                    xtype: 'combo',
                                    name: 'release',
                                    fieldLabel: 'Release',
                                    mode: 'local',
                                    forceSelection: true,
                                    allowBlank: false,
                                    triggerAction: 'all',
                                    editable: false,
                                    displayField: 'name',
                                    valueField: 'value',
                                    store: new Ext.data.JsonStore({
                                        data: comboData.reader.jsonData.release,
                                        fields: ['name', 'value'],
                                    }),
                                }, {
                                    width: 200,
                                    xtype: 'combo',
                                    name: 'version',
                                    fieldLabel: 'Version',
                                    mode: 'local',
                                    forceSelection: true,
                                    allowBlank: false,
                                    triggerAction: 'all',
                                    editable: false,
                                    displayField: 'name',
                                    valueField: 'value',
                                    store: new Ext.data.JsonStore({
                                        data: comboData.reader.jsonData.version,
                                        fields: ['name', 'value'],
                                    }),
                                }, {
                                    width: 200,
                                    xtype: 'combo',
                                    name: 'module',
                                    fieldLabel: 'Module',
                                    mode: 'local',
                                    forceSelection: true,
                                    allowBlank: false,
                                    triggerAction: 'all',
                                    editable: false,
                                    displayField: 'name',
                                    valueField: 'value',
                                    store: new Ext.data.JsonStore({
                                        data: comboData.reader.jsonData.module,
                                        fields: ['name', 'value'],
                                    }),
                                    listeners: {'select': function(menu, rec, i) {
                                        form.details.submodules.store.loadData(comboData.reader.jsonData.submodules[rec.json.value]);
                                        form.doLayout();
                                    }},
                                }, {
                                    width: 200,
                                    xtype: 'combo',
                                    name: 'smodule',
                                    ref: 'submodules',
                                    fieldLabel: 'Sub Module',
                                    mode: 'local',
                                    forceSelection: true,
                                    allowBlank: false,
                                    triggerAction: 'all',
                                    editable: false,
                                    displayField: 'name',
                                    valueField: 'value',
                                    store: submodule_list,
                                }, {
                                    xtype: 'numberfield',
                                    name: 'criticity',
                                    fieldLabel: 'Criticity (0 - 5)',
                                    anchor: '-20',
                                    minValue: 0,
                                    maxValue: 5,
                                    allowBlank: false
                                }
                            ]
                        }, {
                            xtype: 'fieldset',
                            title: 'Steps',
                            ref: 'steps',
                            collapsible: true,
                            items: [
                                {
                                    xtype: 'button',
                                    text: 'Add a step',
                                    handler: function() {
                                        var numField = form.steps.items.getCount() - 1;
                                        form.steps.add(new Ext.form.CompositeField({
                                            xtype: 'compositefield',
                                            fieldLabel: numField,
                                            msgTarget: 'under',
                                            items: [
                                                {xtype: 'textarea',    name: 'action' + numField, width: 300, allowBlank: true},
                                                {xtype: 'textarea',    name: 'expected' + numField, width: 300, allowBlank: true}
                                            ]
                                        }));
                                        form.doLayout();
                                    }
                                }, {
                                    xtype: 'compositefield',
                                    fieldLabel: "N°",
                                    msgTarget: 'under',
                                    items: [
                                        {xtype: 'displayfield',    value: 'Action', width: 300},
                                        {xtype: 'displayfield',    value: 'Expected Result', width: 300}
                                    ]
                                }, {
                                    xtype: 'compositefield',
                                    fieldLabel: 1,
                                    msgTarget: 'under',
                                    items: [
                                        {xtype: 'textarea',    name: 'action1', width: 300, allowBlank: false},
                                        {xtype: 'textarea',    name: 'expected1', width: 300, allowBlank: false}
                                    ]
                                }
                            ]
                        }
                    ],
                    buttons: [
                        {
                            text: 'Save',
                            handler: function() {
                                if (form.form.isValid()) {
                                    var s = '';

                                    Ext.iterate(form.form.getValues(), function(key, value) {
                                        s += String.format("{0} = {1}<br />", key, value);
                                    }, this);

                                    form.getForm().submit({
                                        waitTitle: 'Connecting',
                                        url: '/test_manager/create_tc_updt/',
                                        waitMsg: 'Sending data...',
                                        success: function(f, a) {
                                            Ext.Msg.show({
                                                title: 'Saved',
                                                msg: 'Your test case has been saved',
                                                buttons: Ext.Msg.OK,
                                                icon: Ext.MessageBox.INFO,
                                                fn: function() {
                                                    window.location = '/test_manager/planning/';
                                                }
                                            });
                                        },
                                        failure: function(f, a) {
                                            Ext.Msg.alert('error ' + a.response.status, a.response.statusText);
                                        }
                                    });
                                }
                            }
                        }, {
                            text: 'Reset',
                            handler: function() {
                                form.form.reset();
                            }
                        }
                    ]
                });
            }
            Ext.onReady(function(){
                Ext.QuickTips.init();
                comboData = new Ext.data.JsonStore({
                    url: '/test_manager/create_tc_data/',
                    fields: ['os', 'module', 'envir', 'browser', 'release', 'version', 'smodule'],
                    storeId: 'comboDataStore',
                    listeners: {'load': loadForm},
                });
                comboData.load();
            });
