function loadForm(comboData) {
    form = new Ext.form.FormPanel({
        renderTo: 'rep',
        headers: {
            'Content-type': 'multipart/form-data'
        },
        defaults: {
            width: 300,
        },
        fileUpload: true,
        id: 'tcForm',
        addStep: function() {
            var numField = form.steps.items.getCount();
            form.steps.add(new Ext.form.CompositeField({
                xtype: 'compositefield',
                fieldLabel: numField,
                autoWidth: true,
                ref: 'step' + numField,
                id: 'compositefield_step' + numField,
                msgTarget: 'under',
                items: [
                    {
                        xtype: 'hidden',
                        ref: 'sid',
                        name: 'sid' + numField,
                    }, {
                        xtype: 'displayfield',
                        ref: 'action',
                        name: 'action' + numField,
                        width: 300,
                    }, {
                        xtype: 'displayfield',
                        ref: 'expected',
                        name: 'expected' + numField,
                        width: 300,
                    }, {
                        xtype: 'displayfield',
                        ref: 'scrot_url',
                        html: '',
                        width: 60,
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
                items: [
                    {
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
                        fieldLabel: 'Criticity (0 - 5)',
                        anchor: '-20',
                        minValue: 0,
                        maxValue: 5,
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
                        minValue: 1,
                        maxValue: 492,
                        value: 15,
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
                            value: 'Link',
                            width: 60,
                        }],
                    },
                ],
            },
        ],
    });
    return form;
}
