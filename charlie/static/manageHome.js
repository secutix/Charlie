var tsTree;
Ext.onReady(function() {
    Ext.QuickTips.init();
    var csrf_token = document.getElementById('csrf_token').innerHTML;
    function append_records(myNode, myArray) {
        for(var i = 0; i < myNode.childNodes.length; i++) {
            if(myNode.childNodes[i].isLeaf()) {
                myArray = myArray.concat(new Ext.data.Record({
                    tcid: myNode.childNodes[i].attributes.value,
                    tcname: myNode.childNodes[i].attributes.text,
                }));
            } else {
                myArray = append_records(myNode.childNodes[i], myArray);
            }
        }
        return myArray;
    }
    var form, historyPanel; /*filled by static/newTestcase.jsi
               *contains the fields for test case creation*/
    var comboData = new Ext.data.JsonStore({
        /*contains the fields required to create a new test case*/
        url: '/manage/home/?action=combodata',
        fields: ['os', 'module', 'envir', 'browser', 'release', 'version', 'smodule'],
        storeId: 'comboDataStore',
        listeners: {
            'load': function(myStore, myRecs, opts) {
                form = loadForm(comboData);
                form.hide();
                if(opts['edit']) {
                    form.add({
                        xtype: 'hidden',
                        name: 'tcid',
                        value: tsTree.getSelectionModel().getSelectedNode().attributes.value,
                    });
                    Ext.Ajax.request({
                        method: 'GET',
                        params: {
                            'action': 'tcinfo',
                            'tc': tsTree.getSelectionModel().getSelectedNode().attributes.value,
                        },
                        url: '/manage/home/',
                        success: function(response, options) {
                            var result = Ext.util.JSON.decode(response.responseText);
                            var subm = result.submodules;
                            form.action.setValue('edittc');
                            form.tctitle.setValue(result.title);
                            form.descr.setValue(result.description);
                            form.precond.setValue(result.precondition);
                            form.details.envir.setValue(result.environment);
                            form.details.os.setValue(result.os);
                            form.details.browser.setValue(result.browser);
                            form.details.release.setValue(result.release);
                            form.details.version.setValue(result.version);
                            form.details.module.setValue(result.module);
                            form.details.submodules.setValue(result.sub_module);
                            form.details.criticity.setValue(result.criticity);
                            form.details.tags.setValue(result.tags);
                            for(var i = 1; i < result.steps.length; i++) {
                                form.addStep();
                            }
                            for(var i = 0; i < result.steps.length; i++) {
                                Ext.getCmp('compositefield_step' + (i + 1)).action.setValue(result.steps[i].action);
                                Ext.getCmp('compositefield_step' + (i + 1)).expected.setValue(result.steps[i].expected);
                            }
                        },
                    });
                }
                form.add(new Ext.form.Hidden({
                    name: 'tsid',
                    ref: 'tsid',
                }));
                if(opts['leaf']) {
                    var tsid = tsTree.getSelectionModel().getSelectedNode().parentNode.attributes.tsid;
                } else {
                    var tsid = tsTree.getSelectionModel().getSelectedNode().attributes.tsid;
                }
                if(tsid == undefined) {
                    tsid = -1;
                }
                form.tsid.setValue(tsid);
                form.addButton(new Ext.Button({
                    text: 'Save',
                    handler: function() {
                        if (form.form.isValid()) {
                            form.getForm().submit({
                                waitTitle: 'Connecting',
                                url: '/manage/home/',
                                waitMsg: 'Sending data...',
                                params: {
                                    'csrfmiddlewaretoken': csrf_token,
                                },
                                success: function(f, a) {
                                    Ext.Msg.show({
                                        title: 'Saved',
                                        msg: 'Your test case has been saved',
                                        buttons: Ext.Msg.OK,
                                        icon: Ext.MessageBox.INFO,
                                        fn: function() {
                                            form.hide();
                                            tsTree.getLoader().load(tsTree.getRootNode());
                                            tsTree.show();
                                        }
                                    });
                                },
                                failure: function(f, action) {
                                    Ext.Msg.alert('error ' + action.response.status, action.response.statusText);
                                }
                            });
                        }
                    }
                }));
                /*buttons are not always the same, so here they are...*/
                form.addButton(new Ext.Button({
                    text: 'Reset',
                    handler: function() {
                        form.form.reset();
                    }
                }));
                form.addButton(new Ext.Button({
                    text: 'Cancel',
                    handler: function() {
                        form.hide();
                        tsTree.show();
                    }
                }));
                mainPanel.centerRegion.app.add(form);
                form.show();
                tsTree.hide();
                mainPanel.centerRegion.app.doLayout(true, true);
                form.doLayout();
            },
        },
    });
    var appTitle = '<h1>Choose a task in the left menu</h1>';    /*displays on top of the app*/
    var newUserForm = new Ext.form.FormPanel({
        /*formPanel to create a user*/
        autoHeight: true,
        autoWidth: true,
        padding: 10,
        border: false,
        hidden: true,
        csrf_included: false,
        id: 'newUserForm',
        items: [{
            xtype: 'hidden',
            name: 'action',
            ref: 'action',
            value: 'newUser',
        }, {
            xtype: 'textfield',
            name: 'username',
            ref: 'name',
            allowBlank: false,
            fieldLabel: 'User Name',
        }, {
            xtype: 'hidden',
            ref: 'team',
            name: 'team',
        }, {
            xtype: 'checkbox',
            fieldLabel: 'Privileged',
            ref: 'priv',
            name: 'privileged',
        }],
        buttons: [{
            xtype: 'button',
            text: 'OK',
            handler: function() {
                if(newUserForm.form.isValid()) {
                    var myUserId = teamsTree.getSelectionModel().getSelectedNode().attributes.uid;
                    newUserForm.getForm().submit({
                        waitTitle: 'Connecting',
                        url: '/manage/home/',
                        waitMsg: 'Sending data...',
                        params: {
                            'csrfmiddlewaretoken': csrf_token,
                            'uid': myUserId,
                        },
                        success: function(form, action) {
                            var successMsg = 'The new user has been saved';
                            if(newUserForm.action.getValue() == 'newUser') {
                                successMsg = 'The user has been successfully modified';
                            }
                            Ext.Msg.show({
                                title: 'Saved',
                                msg: successMsg,
                                buttons: Ext.Msg.OK,
                                icon: Ext.MessageBox.INFO,
                                fn: function() {
                                    newUserForm.getForm().reset();
                                    newUserForm.hide();
                                    teamsTree.getLoader().load(teamsTree.getRootNode());
                                    teamsTree.show();
                                }
                            });
                        },
                        failure: function(form, action) {
                            Ext.Msg.alert('error ' + action.response.status, action.response.statusText);
                        },
                    });
                }
            },
        }, {
            xtype: 'button',
            text: 'Cancel',
            handler: function() {
                newUserForm.hide();
                teamsTree.show();
            },
        }],
    });
    var newTeamForm = new Ext.form.FormPanel({
        /*formPanel to create a new team*/
        autoHeight: true,
        autoWidth: true,
        padding: 10,
        border: false,
        hidden: true,
        id: 'newTeamForm',
        items: [{
            xtype: 'hidden',
            name: 'action',
            value: 'newTeam',
        }, {
            xtype: 'textfield',
            name: 'name',
            allowBlank: false,
            fieldLabel: 'Team Name',
        }],
        buttons: [{
            xtype: 'button',
            text: 'OK',
            handler: function() {
                if(newTeamForm.form.isValid()) {
                    newTeamForm.getForm().submit({
                        waitTitle: 'Connecting',
                        url: '/manage/home/',
                        waitMsg: 'Sending data...',
                        success: function(form, action) {
                            Ext.Msg.show({
                                title: 'Saved',
                                msg: 'The new team has been saved',
                                buttons: Ext.Msg.OK,
                                icon: Ext.MessageBox.INFO,
                                fn: function() {
                                    newTeamForm.getForm().reset();
                                    newTeamForm.hide();
                                    teamsTree.getLoader().load(teamsTree.getRootNode());
                                    teamsTree.show();
                                }
                            });
                        },
                        failure: function(from, action) {
                            Ext.Msg.alert('error ' + action.response.status, action.response.statusText);
                        },
                    });
                }
            },
        }, {
            xtype: 'button',
            text: 'Cancel',
            handler: function() {
                newTeamForm.hide();
                teamsTree.show();
            },
        }],
        listeners: {
            'afterlayout': function(myForm, myLayout) {
                myForm.add({
                    xtype: 'hidden',
                    name: 'csrfmiddlewaretoken',
                    value: csrf_token,
                });
            },
        },
    });
    var newTestSetForm = new Ext.form.FormPanel({
        /*formPanel for creating a new test set*/
        autoHeight: true,
        width: 300,
        padding: 10,
        border: false,
        action: 'testSets',
        buttons: [{
            xtype: 'button',
            text: 'Submit',
            autoHeight: true,
            autoWidth: true,
            handler: function(button, curEvent) {
                var selected = testCasesGrid.getSelectionModel().getSelections();
                var testSetsData = {
                    'action': newTestSetForm.action,
                    'csrfmiddlewaretoken': csrf_token,
                    'testSetName': newTestSetForm.testSetName.getValue(),
                    'parentTestSetId': newTestSetForm.parentTestSetId.getValue()
                };
                if(newTestSetForm.action == 'editTs') {
                    testSetsData['tsid'] = newTestSetForm.tsid;
                }
                if(newTestSetForm.form.isValid() && selected.length > 0) {
                    for(i = 0; i < selected.length; i++) {
                        testSetsData['tc' + i] = selected[i].id;
                    }
                    Ext.Ajax.request({
                        method: 'POST',
                        url: '/manage/home/',
                        params: testSetsData,
                        success: function(suc) {
                            var result = Ext.util.JSON.decode(suc.responseText);
                            if(result.success) {
                                testCasesGrid.getSelectionModel().clearSelections();
                                testCasesGrid.hide();
                                newTestSetForm.getForm().reset();
                                newTestSetForm.hide();
                                tsTree.getLoader().load(tsTree.getRootNode());
                                tsTree.show();
                            } else {
                                Ext.Msg.alert('error', result.errorMessage);
                            }
                        },
                        failure: function(suc, err) {
                            Ext.Msg.alert('error', suc.statusText);
                        }
                    });
                } else {
                    Ext.Msg.alert('Error', 'Make sure you selected at least one Test Case and chose a name');
                }
            },
        }, {
            xtype: 'button',
            autoHeight: true,
            autoWidth: true,
            text: 'Cancel',
            handler: function(button, curEvent) {
                newTestSetForm.hide();
                testCasesGrid.hide();
                tsTree.show();
            }
        }],
        id: 'newTestSetForm',
        items: [{
            xtype: 'textfield',
            fieldLabel: 'Test Set Name',
            allowBlank: false,
            ref: 'testSetName',
            name: 'testSetName',
        }, {
            xtype: 'numberfield',
            hidden: true,
            name: 'parentTestSetId',
            ref: 'parentTestSetId',
            value: 0,
        }],
    });
    var testCasesStore = new Ext.data.JsonStore({
        /*store containing all of the test cases*/
        url: '/manage/home/?action=testSets',
        fields: ['title', 'id'],
        storeId: 'testCasesStore',
        listeners: {
            'load': function(myStore, myRecs, opts) {
                testCasesGrid.reconfigure(this, testCasesGrid.getColumnModel());
                mainPanel.centerRegion.app.add(testCasesGrid);
                testCasesGrid.show();
                mainPanel.centerRegion.app.add(newTestSetForm);
                newTestSetForm.show();
                mainPanel.centerRegion.app.doLayout(true, true);
                testCasesGrid.setHeight(Math.min(21 * testCasesStore.getCount() + 51, window.innerHeight - 55));
                testCasesGrid.setWidth(300);
                newTestSetForm.testSetName.setValue(opts['tsname']);
                if(opts['action'] == 'edit') {
                    newTestSetForm.action = 'editTs';
                    newTestSetForm.tsid = opts['tsid'];
                    Ext.Ajax.request({
                        method: 'GET',
                        url: '/manage/home/',
                        params: {
                            'tsid': opts['tsid'],
                            'action': 'getTsTc',
                        },
                        success: function(response, options) {
                            var result = Ext.util.JSON.decode(response.responseText);
                            for(var i = 0; i < result.length; i++) {
                                testCasesGrid.getSelectionModel().selectRecords([testCasesGrid.getStore().getById(result[i]['id'])], true);
                            }
                        },
                    });
                } else {
                    newTestSetForm.action = 'testSets';
                }
            },
        },
    });
    var teamsTree = new Ext.tree.TreePanel({
        /*treePanel containing the teams and the users*/
        autoHeight: true,
        autoWidth: true,
        enableDD: true,
        root: {
            leaf: false,
            nodeType: 'async',
            text: 'Teams',
            draggable: false,
            id: 'teamsSrc',
            expanded: true,
        },
        contextMenuLeaf: new Ext.menu.Menu({
            items: [{
                action: 'editUser',
                text: 'Edit this User',
            }, {
                action: 'newUser',
                text: 'Create User here',
            }, {
                action: 'delUser',
                text: 'Delete this User',
            }],
            listeners: {'itemclick': function(item) {
                switch(item.action) {
                case 'newUser':
                    teamsTree.hide();
                    if(teamsTree.getSelectionModel().getSelectedNode().parentNode.attributes.gid == undefined) {
                        newUserForm.team.setValue(-1);
                    } else {
                        newUserForm.team.setValue(teamsTree.getSelectionModel().getSelectedNode().parentNode.attributes.gid);
                    }
                    mainPanel.centerRegion.app.add(newUserForm);
                    mainPanel.centerRegion.app.doLayout(true, true);
                    newUserForm.show();
                    break;
                case 'editUser':
                    teamsTree.hide();
                    if(teamsTree.getSelectionModel().getSelectedNode().parentNode.attributes.gid == undefined) {
                        newUserForm.team.setValue(-1);
                    } else {
                        newUserForm.team.setValue(teamsTree.getSelectionModel().getSelectedNode().parentNode.attributes.gid);
                    }
                    mainPanel.centerRegion.app.add(newUserForm);
                    mainPanel.centerRegion.app.doLayout(true, true);
                    newUserForm.show();
                    var myUser = teamsTree.getSelectionModel().getSelectedNode().attributes;
                    newUserForm.action.setValue('editUser');
                    newUserForm.name.setValue(myUser.text);
                    Ext.Ajax.request({
                        method: 'GET',
                        params: {
                            'uid': myUser.uid,
                            'action': 'ispriv',
                        },
                        url: '/manage/home/',
                        success: function(response, options) {
                            var result = Ext.util.JSON.decode(response.responseText);
                            if(result.success) {
                                newUserForm.priv.setValue(result.priv);
                            }
                        },
                    });
                    break;
                case 'delUser':
                    Ext.Ajax.request({
                        method: 'POST',
                        params: {
                            'csrfmiddlewaretoken': csrf_token,
                            'action': 'deluser',
                            'u': teamsTree.getSelectionModel().getSelectedNode().attributes.uid,
                        },
                        url: '/manage/home/',
                        success: function(response, options) {
                            var result = Ext.util.JSON.decode(response.responseText);
                            if(result.success) {
                                teamsTree.getLoader().load(teamsTree.getRootNode())
                            } else {
                                Ext.Msg.alert("error", result.errorMessage);
                            }
                        },
                        failure: function(response, options) {
                            var result = Ext.util.JSON.decode(response.responseText);
                            Ext.Msg.alert("error", result.errorMessage);
                        },
                    });
                    break;
                }
            }},
        }),
        contextMenuNode: new Ext.menu.Menu({
            items: [{
                action: 'newTeam',
                text: 'Create new Team',
            }, {
                action: 'newUserHere',
                text: 'Create a User here',
            }, {
                action: 'delTeam',
                text: 'Delete this Team',
            }],
            listeners: {'itemclick': function(item) {
                switch(item.action) {
                case 'newUserHere':
                    teamsTree.hide();
                    if(teamsTree.getSelectionModel().getSelectedNode().attributes.gid == undefined) {
                        newUserForm.team.setValue(-1);
                    } else {
                        newUserForm.team.setValue(teamsTree.getSelectionModel().getSelectedNode().attributes.gid);
                    }
                    mainPanel.centerRegion.app.add(newUserForm);
                    newUserForm.show();
                    mainPanel.centerRegion.doLayout(false);
                    break;
                case 'newTeam':
                    teamsTree.hide();
                    mainPanel.centerRegion.app.add(newTeamForm);
                    newTeamForm.show();
                    mainPanel.centerRegion.doLayout(false);
                    break;
                case 'delTeam':
                    if(teamsTree.getSelectionModel().getSelectedNode() != teamsTree.getRootNode()) {
                        Ext.Ajax.request({
                            method: 'POST',
                            params: {
                                'csrfmiddlewaretoken': csrf_token,
                                'action': 'delteam',
                                't': teamsTree.getSelectionModel().getSelectedNode().attributes.gid,
                            },
                            url: '/manage/home/',
                            success: function(response, options) {
                                var result = Ext.util.JSON.decode(response.responseText);
                                if(result.success) {
                                    teamsTree.getLoader().load(teamsTree.getRootNode());
                                } else {
                                    Ext.Msg.alert("error", result.errorMessage);
                                }
                            },
                            failure: function(response, options) {
                                Ext.Msg.alert("error", "the team couldn't be deleted");
                            },
                        });
                    }
                    break;
                }
            }},
        }),
        listeners: {
            'dragdrop': function(myTreePanel, selNode, dragdrop, curEvent) {
                var team = selNode.parentNode.attributes.gid;
                if(team == undefined) {
                    team = -1;
                }
                if(selNode.isLeaf()) {
                    Ext.Ajax.request({
                        method: 'POST',
                        params: {
                            'action': 'mvuser',
                            'csrfmiddlewaretoken': csrf_token,
                            'team': team,
                            'user': selNode.attributes.uid,
                        },
                        url: '/manage/home/',
                        success: function(response, options) {
                            var result = Ext.util.JSON.decode(response.responseText);
                            if(!result.success) {
                                Ext.Msg.alert("error", result.errorMessage);
                            }
                        },
                        failure: function(response, options) {
                            Ext.Msg.alert("error", "the user couldn't be moved");
                        },
                    });
                    teamsTree.getLoader().load(new Ext.tree.AsyncTreeNode({
                        nodeType: 'async',
                        text: 'Teams',
                        draggable: false,
                        id: 'teamsSrc',
                        expanded: true,
                    }));
                    return true;
                } else {
                    return false;
                }
            },
            'contextmenu': function(selNode, curEvent) {
                selNode.select();
                var myCtxtMenu;
                if(selNode.isLeaf()) {
                    myCtxtMenu = selNode.getOwnerTree().contextMenuLeaf;
                } else {
                    myCtxtMenu = selNode.getOwnerTree().contextMenuNode;
                }
                myCtxtMenu.contextNode = selNode;
                myCtxtMenu.showAt(curEvent.getXY());
            }
        },
        loader: new Ext.tree.TreeLoader({
            requestMethod: 'GET',
            dataUrl: '/manage/home/?action=teams',
            listeners: {
                'load': function(myLoader, myNode, myResponse) {
                    teamsTree.expandAll();
                },
            },
        }),
    });
    tsTree = new Ext.tree.TreePanel({
        /*treePanel containing test cases and test sets*/
        autoHeight: true,
        autoWidth: true,
        enableDD: true,
        root: {
            leaf: false,
            nodeType: 'async',
            iconCls: 'folder',
            text: 'Test Sets',
            draggable: false,
            id: 'tsSrc',
            expanded: true,
        },
        contextMenuLeaf: new Ext.menu.Menu({
            items: [{
                action: 'editTestCase',
                text: 'Edit Test Case',
            }, {
                action: 'newTestCase',
                text: 'Create Test Case here',
            }, {
                action: 'delTestCase',
                text: 'Delete this Test Case',
            }],
            listeners: {
                'itemclick': function(item) {
                    switch(item.action) {
                    case 'editTestCase':
                        tsTree.hide();
                        comboData.load({'leaf': true, 'edit': true});
                        break;
                    case 'newTestCase':
                        tsTree.hide();
                        comboData.load({'leaf': true, 'edit': false});
                        break;
                    case 'delTestCase':
                        var tsid = tsTree.getSelectionModel().getSelectedNode().parentNode.attributes.tsid;
                        if(tsid == undefined) {
                            tsid = -1;
                        }
                        Ext.Ajax.request({
                            method: 'POST',
                            params: {
                                'csrfmiddlewaretoken': csrf_token,
                                'action': 'deltc',
                                'tc': tsTree.getSelectionModel().getSelectedNode().attributes.value,
                                'ts': tsid,
                            },
                            url: '/manage/home/',
                            success: function(response, options) {
                                var result = Ext.util.JSON.decode(response.responseText);
                                if(result.success) {
                                    tsTree.getLoader().load(tsTree.getRootNode());
                                } else {
                                    Ext.Msg.alert("error", result.errorMessage);
                                }
                            },
                            failure: function(response, options) {
                                Ext.Msg.alert("error", "the team couldn't be deleted");
                            },
                        });
                        break;
                    }
                },
            },
        }),
        contextMenuNode: new Ext.menu.Menu({
            items: [{
                action: 'editTestSet',
                text: 'Edit Test Set',
            }, {
                action: 'newTestCaseHere',
                text: 'Create Test Case here',
            }, {
                action: 'newTestSet',
                text: 'Create Test Set here',
            }, {
                action: 'delTestSet',
                text: 'Delete this Test Set',
            }],
            listeners: {
                'itemclick': function(item) {
                    var tsid = tsTree.getSelectionModel().getSelectedNode().attributes.tsid;
                    var tsName = tsTree.getSelectionModel().getSelectedNode().attributes.text;
                    var ptsid;
                    try {
                        ptsid = tsTree.getSelectionModel().getSelectedNode().parentNode.attributes.tsid;
                    } catch(err) {
                        ptsid = 0;
                    }
                    if(tsid == undefined)
                    {
                        tsid = 0;
                    }
                    if(ptsid == undefined)
                    {
                        ptsid = 0;
                    }
                    switch(item.action) {
                    case 'newTestCaseHere':
                        tsTree.hide();
                        comboData.load({'leaf': false});
                        break;
                    case 'editTestSet':
                        tsTree.hide();
                        newTestSetForm.parentTestSetId.setValue(ptsid);
                        testCasesStore.load({'action': 'edit', 'tsid': tsid, 'tsname': tsName});
                        break;
                    case 'newTestSet':
                        tsTree.hide();
                        newTestSetForm.parentTestSetId.setValue(tsid);
                        testCasesStore.load();
                        break;
                    case 'delTestSet':
                        if(tsTree.getSelectionModel().getSelectedNode() != tsTree.getRootNode()) {
                            Ext.Ajax.request({
                                method: 'POST',
                                params: {
                                    'csrfmiddlewaretoken': csrf_token,
                                    'action': 'delts',
                                    'ts': tsid,
                                },
                                url: '/manage/home/',
                                success: function(response, options) {
                                    var result = Ext.util.JSON.decode(response.responseText);
                                    if(result.success) {
                                        tsTree.getLoader().load(tsTree.getRootNode());
                                    } else {
                                        Ext.Msg.alert("error", result.errorMessage);
                                    }
                                },
                                failure: function(response, options) {
                                    Ext.Msg.alert("error", "the team couldn't be deleted");
                                },
                            });
                        }
                        break;
                    }
                }
            },
        }),
        listeners: {
            'dragdrop': function(myTree, selNode, dragdrop, curEvent) {
                var parentTs = selNode.parentNode.attributes.tsid;
                if(parentTs == undefined) {
                    parentTs = -1;
                }
                if(selNode.isLeaf()) {
                    var myMenu = new Ext.menu.Menu({
                        items: [{
                            action: 'moveIt',
                            text: 'Move here',
                        }, {
                            action: 'copyIt',
                            text: 'Copy here',
                        }],
                        listeners: {
                            'itemclick': function(item) {
                                switch(item.action) {
                                case 'moveIt':
                                    myTree.dropAction = 'move';
                                    Ext.Ajax.request({
                                        method: 'POST',
                                        params: {
                                            'csrfmiddlewaretoken': csrf_token,
                                            'fts': dragdrop.dragOverData.source.dragData.node.attributes.tsid,
                                            'tts': dragdrop.dragOverData.target.attributes.tsid,
                                            'tc': selNode.attributes.value,
                                            'action': 'mvtc',
                                        },
                                        url: '/manage/home/',
                                        success: function(response, options) {
                                            var result = Ext.util.JSON.decode(response.responseText);
                                            if(!result.success) {
                                                Ext.Msg.alert("error", result.errorMessage);
                                                tsTree.getLoader().load(tsTree.getRootNode());
                                            } else {
                                                tsTree.getLoader().load(tsTree.getRootNode());
                                            }
                                        }
                                    });
                                    break;
                                case 'copyIt':
                                    myTree.dropAction = 'copy';
                                    Ext.Ajax.request({
                                        method: 'POST',
                                        params: {
                                            'csrfmiddlewaretoken': csrf_token,
                                            'action': 'cptc',
                                            'ts': dragdrop.dragOverData.target.attributes.tsid,
                                            'tc': selNode.attributes.value,
                                        },
                                        url: '/manage/home/',
                                        success: function(response, options) {
                                            var result = Ext.util.JSON.decode(response.responseText);
                                            if(!result.success) {
                                                Ext.Msg.alert("error", result.errorMessage);
                                                tsTree.getLoader().load(tsTree.getRootNode());
                                            } else {
                                                tsTree.getLoader().load(tsTree.getRootNode());
                                            }
                                        }
                                    });
                                    break;
                                }
                            },
                        },
                    }).showAt(curEvent.getXY());
                } else {
                    Ext.Ajax.request({
                        method: 'POST',
                        params: {
                            'csrfmiddlewaretoken': csrf_token,
                            'action': 'mvts',
                            'pts': parentTs,
                            'cts': selNode.attributes.tsid
                        },
                        url: '/manage/home/',
                        success: function(response, options) {
                            var result = Ext.util.JSON.decode(response.responseText);
                            if(!result.success) {
                                Ext.Msg.alert("error", result.errorMessage);
                            }
                        }
                    });
                }
            },
            'contextmenu': function(selNode, curEvent) {
                selNode.select();
                var myCtxtMenu;
                if(selNode.isLeaf()) {
                    myCtxtMenu = selNode.getOwnerTree().contextMenuLeaf;
                } else {
                    myCtxtMenu = selNode.getOwnerTree().contextMenuNode;
                }
                myCtxtMenu.contextNode = selNode;
                myCtxtMenu.showAt(curEvent.getXY());
            },
        },
        loader: new Ext.tree.TreeLoader({
            baseParams: {
                'action': 'testsets',
            },
            requestMethod: 'GET',
            dataUrl: '/manage/home/',
            listeners: {
                'load': function(myLoader, myNode, myResponse) {
                    tsTree.expandAll();
                }
            },
        }),
    });
    var tree = new Ext.tree.TreePanel({
        /*treePanel containing the main management menu*/
        autoWidth: true,
        autoHeight: true,
        root: {
            nodeType: 'async',
            text: 'Administrative Tasks',
            draggable: false,
            leaf: false,
            id: 'menuSrc',
            expanded: true,
        },
        listeners: {
            'click': function(n, e) {
                if(form != undefined) { form.hide(); }
                if(historyPanel != undefined) { historyPanel.hide(); }
                teamsTree.hide();
                newSessPanel.hide();
                newUserForm.hide();
                newTeamForm.hide();
                newTestSetForm.hide();
                tsTree.hide();
                testCasesGrid.hide();
                if(n.isLeaf()) {
                    appTitle = '<h1>' + n.attributes.text + '</h1>';
                    mainPanel.centerRegion.appTitle.update(appTitle);
                    if(n.attributes.value == "testSets") {
                        tsTree.doLayout(true);
                        tsTree.show();
                        mainPanel.centerRegion.app.add(tsTree);
                        mainPanel.centerRegion.doLayout(false);
                    } else if(n.attributes.value == 'history') {
                        historyPanel = new Ext.Panel({
                            autoDestroy: true,
                            ref: 'history',
                            id: 'history',
                            hidden: true,
                            baseCls: 'x-plain',
                            autoWidth: true,
                            autoHeight: true,
                            layout: 'table',
                            layoutConfig: {
                                columns: 3,
                            },
                            defaults: {
                                margin: 3,
                                flex: 3,
                                padding: 3,
                                width: 250,
                                autoHeight: true,
                            },
                            listeners: {
                                'show': function(myPanel) {
                                    var sessions = new Ext.data.JsonStore({
                                        autoDestroy: true,
                                        method: 'GET',
                                        url: '/manage/home/?action=history',
                                        fields: [{
                                            name: 'name',
                                            type: 'string',
                                        }, {
                                            name: 'from',
                                            type: 'date',
                                        }, {
                                            name: 'to',
                                            type: 'date',
                                        }, {
                                            name: 'group',
                                            type: 'int',
                                        }],
                                        listeners: {
                                            'load': function(myStore, myRecs) {
                                                for(var i = 0; i < myRecs.length; i++) {
                                                    myPanel.add({
                                                        xtype: 'panel',
                                                        autoDestroy: true,
                                                        title: myRecs[i].json.name,
                                                        html: "<a class='hist' href='/manage/planning/?tsr=" + myRecs[i].json.id + "'><p>" + myRecs[i].json.from + " to " + myRecs[i].json.to + "</p><p>assigned to " + myRecs[i].json.teamname + "</p></a>",
                                                        bbar: {
                                                            layout: {
                                                                type: 'hbox',
                                                                align: 'top',
                                                            },
                                                            items: [{
                                                                xtype: 'checkbox',
                                                                autoShow: true,
                                                                autoDestroy: true,
                                                                checked: myRecs[i].json.disp,
                                                                tsr: myRecs[i].json.id,
                                                                boxLabel: 'Keep on the "Current sessions" calendar',
                                                                listeners: {
                                                                    'check': function(myCBox, checked) {
                                                                        Ext.Ajax.request({
                                                                            method: 'POST',
                                                                            params: {
                                                                                'csrfmiddlewaretoken': csrf_token,
                                                                                'tsr': myCBox.tsr,
                                                                                'disp': checked,
                                                                                'action': 'chgdisp',
                                                                            },
                                                                            url: '/manage/home/',
                                                                            success: function(response, options) {
                                                                                var result = Ext.util.JSON.decode(response.responseText);
                                                                                if(!result.success) {
                                                                                    Ext.Msg.alert("error", result.errorMessage);
                                                                                }
                                                                            },
                                                                            failure: function(response, options) {
                                                                                Ext.Msg.alert('error', 'The session status couldn\'t be changed');
                                                                            },
                                                                        });
                                                                    },
                                                                },
                                                            }],
                                                        },
                                                    });
                                                }
                                                myPanel.doLayout(true, true);
                                                mainPanel.centerRegion.app.doLayout(true, true);
                                            },
                                        },
                                    });
                                    sessions.load();
                                },
                            },
                        });
                        mainPanel.centerRegion.app.add(historyPanel);
                        historyPanel.show();
                    } else if(n.attributes.value == 'newSession') {
                        mainPanel.centerRegion.app.add(newSessPanel);
                        newSessPanel.show();
                        mainPanel.centerRegion.app.doLayout(true, true);
                    } else if(n.attributes.value == 'currentSession') {
                        window.location = "/manage/planning/";
                    } else if(n.attributes.value == 'teams') {
                        teamsTree.show();
                        mainPanel.centerRegion.app.add(teamsTree);
                        mainPanel.centerRegion.app.doLayout(true, true);
                    }
                }
            },
        },
        loader: new Ext.tree.TreeLoader({
            requestMethod: 'GET',
            baseParams: {'action': 'mainmenu'},
            dataUrl: '/manage/home/',
        }),
    });
    var newSessPanel = new Ext.Panel({
        ref: 'newsess',
        id: 'newsess',
        hidden: true,
        layout: 'table',
        padding: 8,
        layoutConfig: {
            columns: 2,
        },
        defaults: {
            width: 300,
            padding: 8,
        },
        items: [{
            xtype: 'form',
            colspan: 2,
            ref: 'nsform',
            border: true,
            width: 600,
            height: 200,
            padding: 8,
            id: 'newsessname',
            isOK: function() {
                var form_ok = false, dates_ok = false, grid_ok = false;
                if(newSessPanel.nsform.getForm().isValid())
                    form_ok = true;
                if(newSessPanel.nsform.startdate.getValue() < newSessPanel.nsform.enddate.getValue())
                    dates_ok = true;
                if(newSessPanel.sgrid.getStore().getCount() > 0)
                    grid_ok = true;
                if(form_ok && dates_ok && grid_ok) {
                    return {'success': true};
                } else {
                    var errormsg = "";
                    if(!form_ok) {
                        errormsg += "Fill in the form Properly. ";
                    }
                    if(!dates_ok) {
                        errormsg += "Start date must be the earliest. ";
                    }
                    if(!grid_ok) {
                        errormsg += "Select at least one test case. ";
                    }
                    return {'success': false, 'error': errormsg};
                }
            },
            items: [{
                xtype: 'textfield',
                ref: 'sessname',
                allowBlank: false,
                fieldLabel: 'New session Name',
                width: 250,
            }, {
                xtype: 'datefield',
                ref: 'startdate',
                allowBlank: false,
                fieldLabel: 'Starting Date',
                width: 250,
            }, {
                xtype: 'datefield',
                ref: 'enddate',
                allowBlank: false,
                fieldLabel: 'Ending Date',
                width: 250,
            }, {
                xtype: 'combo',
                ref: 'group',
                allowBlank: false,
                fieldLabel: 'Assign to team',
                width: 250,
                editable: false,
                mode: 'remote',
                store: new Ext.data.JsonStore({
                    fields: [{
                        name: 'gname', type: 'string',
                    }, {
                        name: 'gid', type: 'int',
                    }],
                    proxy: new Ext.data.HttpProxy({
                        method: 'GET',
                        url: '/manage/home/?action=getgroups',
                    }),
                }),
                forceSelection: true,
                triggerAction: 'all',
                displayField: 'gname',
                valueField: 'gid',
            }],
            buttons: [{
                text: 'Save',
                handler: function(myButton, myEvent) {
                    var test_form = newSessPanel.nsform.isOK();
                    if(test_form.success) {
                        var ajaxParams = {
                            'csrfmiddlewaretoken': csrf_token,
                            'action': 'newtestsetrun',
                            'name': newSessPanel.nsform.sessname.getValue(),
                            'from_y': newSessPanel.nsform.startdate.getValue().format('Y'),
                            'to_y': newSessPanel.nsform.enddate.getValue().format('Y'),
                            'from_m': newSessPanel.nsform.startdate.getValue().format('m'),
                            'to_m': newSessPanel.nsform.enddate.getValue().format('m'),
                            'from_d': newSessPanel.nsform.startdate.getValue().format('d'),
                            'to_d': newSessPanel.nsform.enddate.getValue().format('d'),
                            'group': newSessPanel.nsform.group.getValue(),
                        };
                        for(var i = 0; i < newSessPanel.sgrid.getStore().getCount(); i++) {
                            ajaxParams['tcid' + i] = newSessPanel.sgrid.getStore().getAt(i).data.tcid;
                            ajaxParams['tcname' + i] = newSessPanel.sgrid.getStore().getAt(i).data.tcname;
                        }
                        Ext.Ajax.request({
                            method: 'POST',
                            url: '/manage/home/',
                            params: ajaxParams,
                            success: function(response, options) {
                                var result = Ext.util.JSON.decode(response.responseText);
                                if(result.success) {
                                    location.reload(true);
                                } else {
                                    Ext.Msg.alert("error", result.errorMessage);
                                }
                            },
                            failure: function(response, options) {
                                Ext.Msg.alert('error', 'The test session couldn\'t be created');
                            }
                        });
                    } else {
                        Ext.Msg.alert("Error", test_form.error);
                    }
                },
            }, {
                text: 'Cancel',
                handler: function(myButton, myEvent) {
                    newSessPanel.hide();
                },
            }],
        }, {
            xtype: 'treepanel',
            height: 400,
            autoScroll: true,
            border: true,
            ref: 'stree',
            root: {
                leaf: false,
                nodeType: 'async',
                text: 'Test Sets',
                draggable: false,
                id: 'tsSrcNode',
                expanded: true,
            },
            loader: new Ext.tree.TreeLoader({
                requestMethod: 'GET',
                dataUrl: '/manage/home/?action=testsets',
            }),
            listeners: {
                'click': function(myNode, myEvent) {
                    if(myNode.isLeaf()) {
                        newSessPanel.sgrid.getStore().add([new Ext.data.Record({
                            tcid: myNode.attributes.value,
                            tcname: myNode.attributes.text,
                        })]);
                    } else {
                        newSessPanel.sgrid.getStore().add(append_records(myNode, []));
                    }
                },
            },
        }, new Ext.grid.GridPanel({
            autoWidth: true,
            enableColumnHide: false,
            enableColumnMove: false,
            enableColumnResize: false,
            enableHdMenu: false,
            height: 400,
            border: true,
            autoScroll: true,
            ref: 'sgrid',
            bbar: [{
                text: 'Reset',
                handler: function(myButton) {
                    newSessPanel.sgrid.getStore().removeAll();
                },
            }, {
                text: 'Remove...',
                enableToggle: true,
                id: 'rm_button',
                handler: function(myButton) {
                    var selected = newSessPanel.sgrid.getSelectionModel().getSelections();
                    if(selected.length > 0) {
                        myButton.toggle();
                        for(var i = 0; i < selected.length; i++) {
                            newSessPanel.sgrid.getStore().remove(selected[i]);
                        }
                    }
                },
            }],
            columns: [{
                id: 'tcid', header: 'Test Case Name', dataIndex: 'tcname', sortable: true, width: 280,
            }],
            store: new Ext.data.ArrayStore({
                fields: [{
                    name: 'tcid', type: 'string',
                }, {
                    name: 'tcname', type: 'string',
                }],
            }),
            listeners: {
                'cellclick': function(myGrid, myRow, myColumn, myEvent) {
                    var rm_button = Ext.getCmp('rm_button');
                    if(rm_button.pressed) {
                        myGrid.getStore().removeAt(myRow);
                    }
                },
                'celldblclick': function(myGrid, myRow, myColumn, myEvent) {
                    myGrid.getStore().removeAt(myRow);
                },
            },
        })],
    });
    var testCasesGrid = new Ext.grid.GridPanel({
        /*grid containing all of the test cases*/
        title: 'Choose the test cases',
        columns: [{
    id: 'id', header: 'Test Cases', dataIndex: 'title', autoWidth: true,
        }],
        id: 'appContent',
        store: testCasesStore,
        stripeRows: true,
        autoExpandColumn: 'id',
        disableSelection: false,
        enableColumnHide: false,
        enableColumnMove: false,
        enableColumnResize: false,
        enableHdMenu: false,
        hidden: true,
    });
    var mainPanel = new Ext.Viewport({
        /*main container of the app*/
        layout: 'border',
        hideBorders: true,
        items: [{
            region: 'north',
            html: '<div id="main_title">Charlie Management | <a href="/logout/">Logout</a></div>',
            autoHeight: true,
            hideBorders: true,
            margins: '0 0 0 0',
        },{
            region: 'center',
            xtype: 'panel',
            ref: 'centerRegion',
            id: 'centerRegion',
            layout: 'border',
            items: [{
                xtype: 'panel',
                hideBorders: true,
                region: 'north',
                ref: 'appTitle',
                html: appTitle,
            },{
                xtype: 'panel',
                hideBorders: true,
                region: 'center',
                autoScroll: true,
                ref: 'app',
                id: 'app',
            }],
        },{
            region: 'west',
            width: 300,
            xtype: 'panel',
            margins: '0 0 0 0',
            items: [tree],
        }],
    });
});
