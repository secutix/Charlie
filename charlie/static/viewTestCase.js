function showForm() {
    form = new Ext.form.FormPanel({
        hidden: true,
        headers: {
            'Content-type': 'multipart/form-data'
        },
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
                    width: 60,
                }, {
                    xtype: 'displayfield',
                    ref: 'jiras',
                    width: 80,
                }, {
                    xtype: 'displayfield',
                    ref: 'comment',
                    width: 200,
                    stepNum: numField,
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
                xtype: 'displayfield',
                fieldLabel: 'Done by',
                ref: 'tester',
            }, {
                xtype: 'displayfield',
                fieldLabel: 'On',
                ref: 'ex_date',
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
                    xtype: 'displayfield',
                    anchor: '-20',
                    ref: 'envir',
                    fieldLabel: 'Enviroment',
                }, {
                    width: 200,
                    xtype: 'displayfield',
                    anchor: '-20',
                    ref: 'os',
                    fieldLabel: 'OS',
                }, {
                    width: 200,
                    xtype: 'displayfield',
                    anchor: '-20',
                    ref: 'browser',
                    fieldLabel: 'Browser',
                }, {
                    width: 200,
                    xtype: 'displayfield',
                    anchor: '-20',
                    ref: 'release',
                    fieldLabel: 'Release',
                }, {
                    width: 200,
                    xtype: 'displayfield',
                    anchor: '-20',
                    ref: 'version',
                    fieldLabel: 'Version',
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
                        value: 'Attachment',
                        width: 80,
                    }, {
                        xtype: 'displayfield',
                        value: 'Status',
                        width: 60,
                    }, {
                        xtype: 'displayfield',
                        value: 'Jiras',
                        width: 80,
                    }, {
                        xtype: 'displayfield',
                        value: 'Comment',
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
