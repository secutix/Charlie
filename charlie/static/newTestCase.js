function loadForm(comboData) {
    var submodule_list = new Ext.data.JsonStore({
        data: comboData.reader.jsonData.smodule,
        fields: ['name', 'value'],
    });
    function removeStep(myButton, myEvent) {
        var i = myButton.index;
        var go_on = true;
        while(go_on)
        {
            try {
                var oldField = Ext.getCmp('compositefield_step' + i);
                var newField = Ext.getCmp('compositefield_step' + (i + 1));
                oldField.action.setValue(newField.action.getValue());
                oldField.expected.setValue(newField.expected.getValue());
                oldField.xp_image.setValue(newField.xp_image.getValue());
            } catch(error) {
                go_on = false;
                Ext.getCmp('compositefield_step' + i).destroy();
            }
            i++;
        }
    }
    form = new Ext.form.FormPanel({
        defaults: {
            width: 300,
        },
        id: 'tcForm',
        addStep: function() {
            var numField = form.steps.items.getCount() - 1;
            form.steps.add(new Ext.form.CompositeField({
                xtype: 'compositefield',
                fieldLabel: numField,
                autoWidth: true,
                ref: 'step' + numField,
                id: 'compositefield_step' + numField,
                msgTarget: 'under',
                items: [
                    {
                        xtype: 'textarea',
                        ref: 'action',
                        name: 'action' + numField,
                        width: 300,
                        allowBlank: true,
                    }, {
                        xtype: 'textarea',
                        ref: 'expected',
                        name: 'expected' + numField,
                        width: 300,
                        allowBlank: true,
                    }, {
                        xtype: 'fileuploadfield',
                        name: 'xp_image' + numField,
                        ref: 'xp_image',
                        width: 200,
                        allowBlank: true,
                    }, {
                        xtype: 'button',
                        text: 'X',
                        ref: 'but',
                        index: numField,
                        handler: removeStep,
                    },
                ]
            }));
            form.doLayout();
        },
        title: 'Test case',
        autoHeight: true,
        autoWidth: true,
        bodyStyle: 'padding: 5px',
        defaults: {
            anchor: '0',
        },
        items: [
            {
                xtype: 'textfield',
                name: 'title',
                ref: 'tctitle',
                fieldLabel: 'Test Case title',
                anchor: '-20',
                allowBlank: false,
            }, {
                xtype: 'hidden',
                name: 'action',
                ref: 'action',
                value: 'newtc',
            }, {
                xtype: 'textfield',
                ref: 'descr',
                name: 'description',
                fieldLabel: 'Description',
                anchor: '-20',
                allowBlank: false,
            }, {
                xtype: 'textarea',
                name: 'precondition',
                fieldLabel: 'Precondition',
                ref: 'precond',
                anchor: '-20',
                allowBlank: true,
            }, {
                xtype: 'fieldset',
                title: 'Details',
                autoWidth: true,
                ref: 'details',
                collapsible: true,
                items: [
                    {
                        width: 200,
                        xtype: 'combo',
                        name: 'envir',
                        ref: 'envir',
                        fieldLabel: 'Environment',
                        mode: 'local',
                        forceSelection: true,
                        allowBlank: true,
                        triggerAction: 'all',
                        editable: true,
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
                        ref: 'os',
                        fieldLabel: 'OS',
                        mode: 'local',
                        forceSelection: true,
                        allowBlank: true,
                        triggerAction: 'all',
                        editable: true,
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
                        ref: 'browser',
                        fieldLabel: 'Browser',
                        mode: 'local',
                        forceSelection: true,
                        allowBlank: true,
                        triggerAction: 'all',
                        editable: true,
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
                        ref: 'release',
                        fieldLabel: 'Release',
                        mode: 'local',
                        forceSelection: true,
                        allowBlank: true,
                        triggerAction: 'all',
                        editable: true,
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
                        ref: 'version',
                        fieldLabel: 'Version',
                        mode: 'local',
                        forceSelection: true,
                        allowBlank: false,
                        triggerAction: 'all',
                        editable: true,
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
                        ref: 'module',
                        fieldLabel: 'Module',
                        mode: 'local',
                        forceSelection: true,
                        allowBlank: false,
                        triggerAction: 'all',
                        editable: true,
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
                        editable: true,
                        displayField: 'name',
                        valueField: 'value',
                        store: submodule_list,
                    }, {
                        xtype: 'numberfield',
                        name: 'criticity',
                        ref: 'criticity',
                        allowDecimals: false,
                        fieldLabel: 'Criticity (0 - 5)',
                        anchor: '-20',
                        minValue: 0,
                        maxValue: 5,
                        allowBlank: false,
                    }, {
                        xtype: 'textfield',
                        anchor: '-20',
                        name: 'tags',
                        ref: 'tags',
                        fieldLabel: 'tags',
                        allowBlank: false,
                    }, {
                        xtype: 'numberfield',
                        name: 'duration',
                        ref: 'duration',
                        allowDecimals: false,
                        fieldLabel: 'Duration (min)',
                        anchor: '-20',
                        minValue: 1,
                        maxValue: 492,
                        value: 15,
                        allowBlank: false,
                    }
                ]
            }, {
                xtype: 'fieldset',
                title: 'Steps',
                ref: 'steps',
                autoWidth: true,
                collapsible: true,
                items: [
                    {
                        xtype: 'button',
                        text: 'Add a step',
                        handler: function() {
                            form.addStep();
                        },
                    }, {
                        xtype: 'compositefield',
                        fieldLabel: "N°",
                        msgTarget: 'under',
                        items: [{
                            xtype: 'displayfield',
                            value: 'Action',
                            width: 300,
                        }, {
                            xtype: 'displayfield',
                            value: 'Expected Result',
                            width: 300,
                        }, {
                            xtype: 'displayfield',
                            value: 'Screenshot',
                            width: 200,
                        }, {
                            xtype: 'displayfield',
                            value: 'Remove',
                            autoWidth: true,
                        }],
                    }, {
                        xtype: 'compositefield',
                        fieldLabel: 1,
                        ref: 'step1',
                        id: 'compositefield_step1',
                        msgTarget: 'under',
                        items: [{
                            xtype: 'textarea',
                            ref: 'action',
                            name: 'action1', width: 300,
                            allowBlank: false,
                        }, {
                            xtype: 'textarea',
                            ref: 'expected',
                            name: 'expected1', width: 300,
                            allowBlank: false,
                        }, {
                            xtype: 'fileuploadfield',
                            name: 'xp_image1',
                            ref: 'xp_image',
                            width: 200,
                            allowBlank: true,
                        }, {
                            xtype: 'button',
                            ref: 'but',
                            text: 'X',
                            index: 1,
                            handler: removeStep,
                        }],
                    },
                ],
            },
        ],
    });
    return form;
}
