function loadForm(comboData) {
    var submodule_list = new Ext.data.JsonStore({
        data: comboData.reader.jsonData.smodule,
        fields: ['name', 'value'],
    });
    function insertStep(but, evt) {
        form.addStep();
        form.doLayout();
        for(var i = form.steps.items.items.length - 2; i > but.index; i--)
        {
            var oldField = Ext.getCmp('compositefield_step' + (i - 1));
            var newField = Ext.getCmp('compositefield_step' + i);
            newField.action.setValue(oldField.action.getValue());
            newField.expected.setValue(oldField.expected.getValue());
            newField.xp_image.setValue(oldField.xp_image.getValue());
            newField.scrot_url.setValue(oldField.scrot_url.getValue());
            newField.sid.setValue(oldField.sid.getValue());
        }
        var blankField = Ext.getCmp('compositefield_step' + but.index);
        blankField.action.setValue('');
        blankField.expected.setValue('');
        blankField.xp_image.setValue('');
        blankField.scrot_url.setValue('');
        blankField.sid.setValue('');
    }
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
                oldField.scrot_url.update(newField.scrot_url.getValue());
                oldField.sid.setValue(newField.sid.getValue());
            } catch(error) {
                go_on = false;
                Ext.getCmp('compositefield_step' + i).destroy();
            }
            i++;
        }
    }
    form = new Ext.form.FormPanel({
        headers: {
            'Content-type': 'multipart/form-data'
        },
        defaults: {
            width: 300,
        },
        fileUpload: true,
        id: 'tcForm',
        addStep: function() {
            var numField = form.steps.items.getCount() - 1;
            form.steps.add(new Ext.form.CompositeField({
                xtype: 'compositefield',
                fieldLabel: numField,
                autoWidth: true,
                autoDestroy: true,
                ref: 'step' + numField,
                id: 'compositefield_step' + numField,
                msgTarget: 'under',
                items: [
                    {
                        xtype: 'hidden',
                        ref: 'sid',
                        name: 'sid' + numField,
                    }, {
                        xtype: 'textarea',
                        grow: true,
                        ref: 'action',
                        name: 'action' + numField,
                        width: 280,
                        maxLength: 2500,
                        maxLengthText: 'Text must not exceed 2500 characters',
                        allowBlank: false,
                        enableKeyEvents: true,
                        listeners: {
                            'keyup': function(myField, newVal, oldVal) {
                                form.doLayout(false, true);
                            },
                        },
                    }, {
                        xtype: 'textarea',
                        grow: true,
                        ref: 'expected',
                        name: 'expected' + numField,
                        width: 280,
                        maxLength: 2500,
                        maxLengthText: 'Text must not exceed 2500 characters',
                        allowBlank: true,
                        enableKeyEvents: true,
                        listeners: {
                            'keyup': function(myField, newVal, oldVal) {
                                form.doLayout(false, true);
                            },
                        },
                    }, {
                        xtype: 'fileuploadfield',
                        name: 'xp_image' + numField,
                        id: 'xp_image' + numField,
                        ref: 'xp_image',
                        width: 120,
                        allowBlank: true,
                    }, {
                        xtype: 'displayfield',
                        ref: 'scrot_url',
                        html: '',
                        width: 60,
                    }, {
                        xtype: 'panel',
                        border: false,
                        layout: 'column',
                        items: [{
                            xtype: 'button',
                            ref: 'addbut',
                            text: '+',
                            index: numField,
                            handler: insertStep,
                        }, {
                            xtype: 'button',
                            ref: 'delbut',
                            text: '-',
                            index: numField,
                            handler: removeStep,
                        }],
                    },
                ]
            }));
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
                maxLength: 200,
                maxLengthText: 'Text must not exceed 200 characters',
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
                maxLength: 200,
                maxLengthText: 'Text must not exceed 200 characters',
            }, {
                xtype: 'textarea',
                grow: true,
                name: 'precondition',
                fieldLabel: 'Precondition',
                ref: 'precond',
                anchor: '-20',
                allowBlank: true,
                maxLength: 2500,
                maxLengthText: 'Text must not exceed 2500 characters',
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
                        name: 'module',
                        ref: 'module',
                        fieldLabel: 'Module',
                        mode: 'local',
                        allowBlank: false,
                        triggerAction: 'all',
                        editable: true,
                        displayField: 'name',
                        valueField: 'value',
                        maxLength: 200,
                        maxLengthText: 'Text must not exceed 200 characters',
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
                        allowBlank: false,
                        triggerAction: 'all',
                        editable: true,
                        displayField: 'name',
                        valueField: 'value',
                        store: submodule_list,
                        maxLength: 200,
                        maxLengthText: 'Text must not exceed 200 characters',
                    }, {
                        xtype: 'numberfield',
                        name: 'criticity',
                        ref: 'criticity',
                        allowDecimals: false,
                        fieldLabel: 'Criticity (1 - 5)',
                        anchor: '-20',
                        minValue: 1,
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
                        maxValue: 2460,
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
                            width: 280,
                        }, {
                            xtype: 'displayfield',
                            value: 'Expected Result',
                            width: 280,
                        }, {
                            xtype: 'displayfield',
                            value: 'Attachment',
                            width: 120,
                        }, {
                            xtype: 'displayfield',
                            value: 'Link',
                            width: 60,
                        }, {
                            xtype: 'displayfield',
                            value: 'Add/Del',
                            autoWidth: true,
                        }],
                    }, {
                        xtype: 'compositefield',
                        fieldLabel: 1,
                        ref: 'step1',
                        id: 'compositefield_step1',
                        msgTarget: 'under',
                        items: [{
                            xtype: 'hidden',
                            ref: 'sid',
                            name: 'sid1',
                        }, {
                            xtype: 'textarea',
                            grow: true,
                            ref: 'action',
                            name: 'action1', width: 280,
                            allowBlank: false,
                            maxLength: 2500,
                            maxLengthText: 'Text must not exceed 2500 characters',
                            enableKeyEvents: true,
                            listeners: {
                                'keyup': function(myField, newVal, oldVal) {
                                    form.doLayout(false, true);
                                },
                            },
                        }, {
                            xtype: 'textarea',
                            grow: true,
                            ref: 'expected',
                            name: 'expected1', width: 280,
                            allowBlank: true,
                            maxLength: 2500,
                            maxLengthText: 'Text must not exceed 2500 characters',
                        }, {
                            xtype: 'fileuploadfield',
                            name: 'xp_image1',
                            id: 'xp_image1',
                            ref: 'xp_image',
                            width: 120,
                            allowBlank: true,
                            enableKeyEvents: true,
                            listeners: {
                                'keyup': function(myField, newVal, oldVal) {
                                    form.doLayout(false, true);
                                },
                            },
                        }, {
                            xtype: 'displayfield',
                            html: '',
                            ref: 'scrot_url',
                            width: 60,
                        }, {
                            xtype: 'panel',
                            border: false,
                            layout: 'column',
                            items: [{
                                xtype: 'button',
                                ref: 'addbut',
                                text: '+',
                                index: 1,
                                handler: insertStep,
                            }, {
                                xtype: 'button',
                                ref: 'delbut',
                                text: '-',
                                index: 1,
                                handler: removeStep,
                            }],
                        }],
                    },
                ],
            },
        ],
    });
    return form;
}
